from django.urls import path
from . import views

urlpatterns = [
    
    path('', views.index, name='index'),
    path('checkout/', views.create_checkout_session, name='checkout'),
    path('order/success/', views.order_success, name='order_success'),
    path('order/cancel/', views.order_cancel, name='order_cancel'),
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
]