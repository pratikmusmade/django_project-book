from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class User(AbstractUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    is_seller = models.BooleanField(default=False)  # ✅ New field to indicate if user is a seller


    def __str__(self):
        return self.username


class Book(models.Model):
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('used', 'Used'),
    ]

    book_id = models.AutoField(primary_key=True)
    seller = models.ForeignKey('Seller', on_delete=models.CASCADE, related_name="books")  # ✅ Correct ForeignKey field name
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    availability_status = models.BooleanField(default=True)
    rental_option = models.BooleanField(default=False)
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)
    quantity = models.PositiveIntegerField(default=1)
    image = models.ImageField(upload_to='book_images/', null=True, blank=True)

    def __str__(self):
        return f"{self.title} by {self.author} - {self.seller.shop_name}"


    def __str__(self):
        return f"{self.title} by {self.author}"
    
class Seller(models.Model):
    seller_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sellers")
    shop_name = models.CharField(max_length=255)
    approved_status = models.BooleanField(default=False)
    gstin = models.CharField(max_length=15, unique=True) 

    @staticmethod
    def get_sellers_by_user(user_id):
        return Seller.objects.filter(user__id=user_id)  # ✅ Fetch sellers by user ID
    
    def __str__(self):
        return f"{self.shop_name} - {'Approved' if self.approved_status else 'Pending'}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    order_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")  # User FK
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="orders")  # Book FK
    order_date = models.DateTimeField(auto_now_add=True)  # Auto set when order is created
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')  # Enum Choices

    def __str__(self):
        return f"Order {self.order_id} - {self.user.username} - {self.status}"

class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    book = models.ForeignKey('Book', on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveIntegerField()  # Ensure rating is positive
    comment = models.TextField()
    review_date = models.DateTimeField(auto_now_add=True)  # Auto set timestamp on creation

    def __str__(self):
        return f"Review by {self.user.username} for {self.book.title} - {self.rating}⭐"


class Request(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('fulfilled', 'Fulfilled'),
        ('rejected', 'Rejected'),
    ]

    REQUEST_STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
    ]

    request_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="requests")
    book_title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    request_status = models.CharField(max_length=15, choices=REQUEST_STATUS_CHOICES, default='open')
    accepted_seller = models.ForeignKey('Seller', on_delete=models.SET_NULL, null=True, blank=True, related_name="accepted_requests")

    def __str__(self):
        return f"{self.book_title} by {self.author} - {self.status}"
