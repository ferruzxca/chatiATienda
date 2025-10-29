from django.core.management.base import BaseCommand
from shopbot.models import Product
from decimal import Decimal

DATA = [
    ("CO600", "Refresco 600ml", "Coca-Cola", "coca", "22.00", "14.00"),
    ("PE600", "Refresco 600ml", "Pepsi", "pepsi", "20.00", "13.00"),
    ("AG1L1", "Agua 1L", "Bonafont", "agua", "16.00", "8.00"),
    ("AG1L2", "Agua 1L", "Casa", "agua", "14.00", "6.00"),
    ("PAN01", "Pan Blanco", "Bimbo", "pan", "48.00", "33.00"),
    ("LEC01", "Leche 1L", "Lala", "leche", "29.00", "22.00"),
    ("HUE01", "Huevo docena", "San Juan", "huevo", "52.00", "41.00"),
    ("ATN01", "Atún 140g", "Dolores", "atun", "21.00", "14.00"),
    ("ACE01", "Aceite 1L", "123", "aceite", "49.00", "34.00"),
    ("CAF01", "Café 200g", "Nescafé", "cafe", "98.00", "64.00"),
    ("CAF02", "Café 200g", "Casa", "cafe", "89.00", "49.00"),
    ("HAR01", "Harina 1kg", "Maseca", "harina", "29.00", "20.00"),
    ("ZOT01", "Jabón 400g", "Zote", "jabonzote", "22.00", "12.00"),
    ("SHA01", "Shampoo 375ml", "Head&Shoulders", "shampoo", "99.00", "66.00"),
    ("PAP01", "Papas 45g", "Sabritas", "papas", "19.00", "10.00"),
    ("ORE01", "Galletas 117g", "Oreo", "oreo", "28.00", "16.00"),
]

class Command(BaseCommand):
    help = "Carga productos de ejemplo"

    def handle(self, *args, **kwargs):
        Product.objects.all().delete()
        for sku, name, brand, cat, price, cost in DATA:
            Product.objects.create(
                sku=sku, name=name, brand=brand, category=cat,
                price=Decimal(price), cost=Decimal(cost), stock=100
            )
        self.stdout.write(self.style.SUCCESS(f"Cargados {len(DATA)} productos"))
