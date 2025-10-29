# AbarrotesIA — Chat inteligente de ventas (Django 5)

## Requisitos macOS
```bash
brew install python@3.12
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Inicialización
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py seed_products
python manage.py runserver
```

Visita http://127.0.0.1:8000

### Flujo
- "2 leches Lala", "coca 600", "agrega pan bimbo"
- Marca no registrada → sugiere 3 productos de **alto margen**
- "carrito" → muestra pedido
- "pagar" → factura sí/no → método de pago → RFC (si aplica) → correo → ticket/factura pagados
- Descarga comprobante en `/recibo/<id>/`
