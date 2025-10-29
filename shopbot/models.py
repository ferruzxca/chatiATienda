from django.db import models
from decimal import Decimal

class Product(models.Model):
    sku = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=120)
    brand = models.CharField(max_length=80)
    category = models.CharField(max_length=80)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    cost = models.DecimalField(max_digits=9, decimal_places=2)
    stock = models.IntegerField(default=100)

    def margin_abs(self) -> Decimal:
        return self.price - self.cost

    def margin_rate(self) -> Decimal:
        if self.price == 0:
            return Decimal("0")
        return (self.price - self.cost) / self.price

    def __str__(self):
        return f"{self.name} {self.brand}"

class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    subtotal = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    paid = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=32, blank=True)
    email = models.EmailField(blank=True)
    invoice_requested = models.BooleanField(default=False)
    rfc = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"Orden #{self.id or ''}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=9, decimal_places=2)

    def line_total(self):
        return self.quantity * self.unit_price
