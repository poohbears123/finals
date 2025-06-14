from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Variety(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Item(models.Model):
    SIZE_CHOICES = [
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('XXL', 'XXL'),
    ]
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    variety = models.ForeignKey(Variety, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    size = models.CharField(max_length=3, choices=SIZE_CHOICES, default='M')
    stock = models.IntegerField(default=0)
    price = models.IntegerField(default=0)
    photo = models.ImageField(upload_to='product_photos/', null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def quantity_remain(self):
        return self.stock

class Purchase(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Ready for Pick Up', 'Ready for Pick Up'),
        ('Completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    purchase_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.user.username} bought {self.quantity} of {self.item.name} on {self.purchase_date.strftime('%Y-%m-%d %H:%M:%S')} (Status: {self.status})"
