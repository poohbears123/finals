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
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    variety = models.ForeignKey(Variety, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=0)
    price = models.IntegerField(default=0)  # Price in Philippine Peso
    photo = models.ImageField(upload_to='product_photos/', null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def quantity_remain(self):
        # Calculate remaining quantity, for example, quantity minus sold quantity
        # Assuming you have a Purchase model tracking sold quantities
        from .models import Purchase
        sold_quantity = Purchase.objects.filter(item=self, status='Completed').aggregate(total=models.Sum('quantity'))['total'] or 0
        return self.quantity - sold_quantity

class Purchase(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    purchase_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.user.username} bought {self.quantity} of {self.item.name} on {self.purchase_date.strftime('%Y-%m-%d %H:%M:%S')} (Status: {self.status})"
