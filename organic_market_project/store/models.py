from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    farmer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='farmer_products')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_qty = models.IntegerField(default=50, help_text="Available stock in kg or units")
    image = models.URLField(max_length=500, blank=True, null=True, help_text="Image URL")
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (Farmer: {self.farmer.username if self.farmer else 'Admin'})"

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 0.0

    @property
    def total_reviews(self):
        return self.reviews.count()


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user_name = models.CharField(max_length=100)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user_name} - {self.product.name} ({self.rating}★)"


class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending Verification'),
        ('Accepted', 'Accepted / Packing'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Completed', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    customer_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    payment_method = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=100, blank=True, null=True, help_text="UPI UTR / Ref No")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_items = models.TextField(help_text="Summary of items ordered")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    # Live GPS Coordinates for Driver
    driver_latitude = models.FloatField(null=True, blank=True)
    driver_longitude = models.FloatField(null=True, blank=True)

    # Destination Coordinates
    dest_latitude = models.FloatField(null=True, blank=True)
    dest_longitude = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name} ({self.status})"