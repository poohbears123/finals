from django.db import models
from django.contrib.auth.models import User

class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    variety = models.CharField(max_length=100, blank=True)
    total_quantity = models.IntegerField(default=0)
    quantity_remain = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    purchase_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} bought {self.quantity} of {self.item.name} on {self.purchase_date.strftime('%Y-%m-%d %H:%M:%S')}"
