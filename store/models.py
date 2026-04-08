from django.db import models
import uuid



class Product(models.Model):
    name = models.CharField(max_length=200)          # Product ka naam
    description = models.TextField()                  # Product ki details
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price in INR
    image_emoji = models.CharField(max_length=10, default='📦')   # Emoji

    def __str__(self):
        return self.name

    def price_in_paise(self):
        return int(self.price * 100)



class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]

  
    idempotency_key = models.UUIDField(default=uuid.uuid4, unique=True)

    session_key = models.CharField(max_length=100)   
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

   
    stripe_session_id = models.CharField(max_length=200, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.status}"

    class Meta:
        ordering = ['-created_at']   # Latest order p



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)  

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    def subtotal(self):
        return self.quantity * self.price_at_purchase
