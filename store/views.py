import stripe
import logging

from django.conf import settings
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.db import transaction

from .models import Product, Order, OrderItem

# Logger setup - debugging ke liye
logger = logging.getLogger(__name__)


stripe.api_key = settings.STRIPE_SECRET_KEY


def get_or_create_session_key(request):
    """
    Har visitor ko ek unique session key milti hai.
    Bina login ke user identify karne ka tarika.
    """
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key



def index(request):
    session_key = get_or_create_session_key(request)

    products = Product.objects.all()

    # Sirf is user ke PAID orders dikhao
    orders = Order.objects.filter(
        # session_key=session_key,
        status='paid'
    ).prefetch_related('items__product')

    context = {
        'products': products,
        'orders': orders,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
    }
    return render(request, 'store/index.html', context)



@require_POST
def create_checkout_session(request):
    """
    1. Form se quantities padhta hai
    2. Order database mein save karta hai (pending)
    3. Stripe Checkout session banata hai
    4. User ko Stripe pe redirect karta hai
    """
    session_key = get_or_create_session_key(request)

    quantities = {}
    for product in Product.objects.all():
        qty_str = request.POST.get(f'qty_{product.id}', '0')
        try:
            qty = int(qty_str)
        except ValueError:
            qty = 0
        if qty > 0:
            quantities[product.id] = qty

    
    if not quantities:
        return redirect('index')

    products_in_cart = Product.objects.filter(id__in=quantities.keys())

  
    total = sum(p.price * quantities[p.id] for p in products_in_cart)

   
    with transaction.atomic():
        order = Order.objects.create(
            session_key=session_key,
            status='pending',
            total_amount=total,
        )

        line_items = []
        for product in products_in_cart:
            qty = quantities[product.id]
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=qty,
                price_at_purchase=product.price,
            )

           
            
            line_items.append({
                'price_data': {
                    'currency': 'inr',
                    'product_data': {
                        'name': product.name,
                        'description': product.description,
                    },
                    'unit_amount': product.price_in_paise(),
                },
                'quantity': qty,
            })

  
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=f"{settings.BASE_URL}/order/success/?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.BASE_URL}/order/cancel/",
            metadata={'order_id': str(order.id)},
            idempotency_key=str(order.idempotency_key),
        )

        order.stripe_session_id = checkout_session.id
        order.save(update_fields=['stripe_session_id'])

        # User ko Stripe pe bhejo
        return redirect(checkout_session.url, code=303)

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error for order {order.id}: {e}")
        order.status = 'failed'
        order.save(update_fields=['status'])
        return redirect('index')



def order_success(request):
    """
    Stripe payment ke baad user yahan aata hai.
    Stripe se verify karte hain ki payment sach mein hui.
    """
    session_id = request.GET.get('session_id')

    if not session_id:
        return redirect('index')

    try:
        checkout_session = stripe.checkout.Session.retrieve(session_id)

        if checkout_session.payment_status == 'paid':
            order_id = checkout_session.metadata.get('order_id')

            # select_for_update() - database lock
            # Race condition nahi hogi webhook aur success page ke beech
            with transaction.atomic():
                order = Order.objects.select_for_update().get(
                    id=order_id,
                    stripe_session_id=session_id
                )
                if order.status == 'pending':
                    order.status = 'paid'
                    order.save(update_fields=['status'])

    except (stripe.error.StripeError, Order.DoesNotExist) as e:
        logger.error(f"Success page error: {e}")

    return redirect('index')



def order_cancel(request):
    """User ne payment cancel ki - wapas main page"""
    return redirect('index')



@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Stripe ka automatic notification.
    Agar user ka browser band ho gaya payment ke baad,
    tab bhi yeh webhook order paid mark kar deta hai.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        logger.warning(f"Webhook signature failed: {e}")
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        if session.get('payment_status') == 'paid':
            order_id = session.get('metadata', {}).get('order_id')

            if order_id:
                try:
                    with transaction.atomic():
                        order = Order.objects.select_for_update().get(id=order_id)
                        if order.status == 'pending':
                            order.status = 'paid'
                            order.save(update_fields=['status'])
                            logger.info(f"Order {order_id} paid via webhook")
                except Order.DoesNotExist:
                    logger.error(f"Order {order_id} not found")

    
    return HttpResponse(status=200)
