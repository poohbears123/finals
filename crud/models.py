from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    variety = models.CharField(max_length=100, blank=True)
    total_quantity = models.IntegerField(default=0)
    quantity_remain = models.IntegerField(default=0)

    def __str__(self):
        return self.name
