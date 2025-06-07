from django.contrib import admin
from .models import Purchase

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('user', 'item', 'quantity', 'purchase_date', 'status')
    list_editable = ('status',)
    list_filter = ('status', 'purchase_date')
    search_fields = ('user__username', 'item__name')
