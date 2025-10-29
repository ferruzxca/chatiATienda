from django.contrib import admin
from .models import Product, Order, OrderItem

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("sku","name","brand","category","price","cost","stock")
    search_fields = ("sku","name","brand","category")

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id","created_at","subtotal","tax","total","paid","payment_method","email","invoice_requested")
    inlines = [OrderItemInline]
