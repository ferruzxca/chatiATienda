from django.shortcuts import render
from django.http import JsonResponse, HttpRequest
from django.template.loader import render_to_string
from decimal import Decimal
from .models import Product, Order, OrderItem
from .nlp import (
    intent, extract_qty, find_products, top_margin,
    brand_in_msg, known_brand, IVA, COMPLEMENTOS, extract_category
)

def _session_cart(request: HttpRequest) -> dict:
    cart = request.session.get("cart", {})
    request.session["cart"] = cart
    return cart

def _cart_add(cart: dict, sku: str, qty: int = 1):
    cart[sku] = cart.get(sku, 0) + max(1, qty)

def _cart_remove(cart: dict, sku: str, qty: int = 999):
    if sku in cart:
        cart[sku] = max(0, cart[sku] - qty)
        if cart[sku] == 0:
            del cart[sku]

def _cart_totals(cart: dict):
    subtotal = Decimal("0")
    lines = []
    for sku, qty in cart.items():
        p = Product.objects.get(sku=sku)
        line = {"p": p, "qty": qty, "line_total": p.price * qty}
        subtotal += line["line_total"]
        lines.append(line)
    tax = (subtotal * IVA).quantize(Decimal("0.01"))
    total = (subtotal + tax).quantize(Decimal("0.01"))
    return lines, subtotal.quantize(Decimal("0.01")), tax, total

def _cart_html(request):
    cart = _session_cart(request)
    lines, subtotal, tax, total = _cart_totals(cart)
    return render_to_string(
        "shopbot/_cart.html",
        {"lines": lines, "subtotal": subtotal, "tax": tax, "total": total},
        request=request
    )

def chat(request: HttpRequest):
    request.session.setdefault("stage", "chat")
    return render(request, "shopbot/chat.html")

def api_add_product(request: HttpRequest):
    sku = request.GET.get("sku")
    qty = int(request.GET.get("qty", "1"))
    cart = _session_cart(request)
    try:
        Product.objects.get(sku=sku)
        _cart_add(cart, sku, qty)
        request.session.modified = True
        reply = "Perfecto. Agregué el producto al carrito."
    except Product.DoesNotExist:
        reply = "No encontré ese producto. En esta tienda no se vende."
    html = _cart_html(request)
    return JsonResponse({"reply": reply, "cart_html": html})

def api_message(request: HttpRequest):
    msg = request.POST.get("message","").strip()
    stg = request.session.get("stage","chat")
    cart = _session_cart(request)

    # Etapas de cierre
    if stg == "ask_invoice":
        need = msg.lower().startswith(("s","y"))
        request.session["invoice"] = need
        request.session["stage"] = "ask_payment"
        return JsonResponse({"reply": "¿Método de pago? efectivo, tarjeta o transferencia.", "cart_html": _cart_html(request)})

    if stg == "ask_payment":
        method = "efectivo" if "efectivo" in msg.lower() else \
                 "tarjeta" if "tarjeta" in msg.lower() else \
                 "transferencia" if "transferencia" in msg.lower() else None
        if not method:
            return JsonResponse({"reply": "Indica: efectivo, tarjeta o transferencia.", "cart_html": _cart_html(request)})
        request.session["payment_method"] = method
        if request.session.get("invoice"):
            request.session["stage"] = "ask_rfc"
            return JsonResponse({"reply": "Dame tu RFC para la factura.", "cart_html": _cart_html(request)})
        request.session["stage"] = "ask_email"
        return JsonResponse({"reply": "Compra registrada. ¿Me compartes un correo para enviarte promociones y tu ticket?", "cart_html": _cart_html(request)})

    if stg == "ask_rfc":
        request.session["rfc"] = msg.strip().upper()
        request.session["stage"] = "ask_email"
        return JsonResponse({"reply": "Gracias. ¿Correo para enviarte factura y promociones?", "cart_html": _cart_html(request)})

    if stg == "ask_email":
        request.session["email"] = msg.strip()
        lines, subtotal, tax, total = _cart_totals(cart)
        order = Order.objects.create(
            subtotal=subtotal, tax=tax, total=total, paid=True,
            payment_method=request.session.get("payment_method",""),
            email=request.session.get("email",""),
            invoice_requested=bool(request.session.get("invoice")),
            rfc=request.session.get("rfc",""),
        )
        for ln in lines:
            OrderItem.objects.create(order=order, product=ln["p"], quantity=ln["qty"], unit_price=ln["p"].price)
        request.session["stage"] = "done"
        request.session["last_order_id"] = order.id
        request.session["cart"] = {}
        return JsonResponse({"reply": f"Listo. Ticket {'y factura ' if order.invoice_requested else ''}pagados. Gracias por tu compra. Descarga tu comprobante: /recibo/{order.id}/", "cart_html": _cart_html(request)})

    # Chat normal
    it = intent(msg)
    cat = extract_category(msg)  # categoría detectada en el mensaje

    if it == "add":
        qty = extract_qty(msg)
        products = find_products(msg, category=cat)

        # Si el usuario pidió una categoría específica que no vendemos
        if cat and not products:
            reply = f"No se vende la categoría solicitada ('{cat}') en esta tienda."
            return JsonResponse({"reply": reply, "cart_html": _cart_html(request)})

        # Marca no registrada → ofrecer 3 similares SOLO de esa categoría si existe
        b = brand_in_msg(msg)
        if b and not known_brand(b):
            options = top_margin(3, category=cat) if cat else top_margin(3)
            if cat and not options:
                # categoría pedida pero sin inventario
                reply = f"No se vende la categoría solicitada ('{cat}') en esta tienda."
                return JsonResponse({"reply": reply, "cart_html": _cart_html(request)})
            reply = f"No manejo la marca '{b}'. Te ofrezco estas opciones con excelente valor:"
            sugg = [{"sku": p.sku, "text": f"{p.name} {p.brand} ${p.price}"} for p in options]
            return JsonResponse({"reply": reply, "suggestions": sugg, "cart_html": _cart_html(request)})

        # Si no encontró nada y tampoco hay categoría clara → sugerencias generales
        if not products:
            options = top_margin(3)
            reply = "No identifiqué el producto. Mira estas opciones recomendadas:"
            sugg = [{"sku": p.sku, "text": f"{p.name} {p.brand} ${p.price}"} for p in options]
            return JsonResponse({"reply": reply, "suggestions": sugg, "cart_html": _cart_html(request)})

        # Agrega el mejor por margen dentro del conjunto filtrado
        p = sorted(products, key=lambda x: (-x.margin_rate(), -x.margin_abs()))[0]
        _cart_add(cart, p.sku, qty)
        request.session.modified = True

        # Upsell relacionado o por margen dentro de la misma categoría si es posible
        comp = None
        if cat:
            comp_candidates = top_margin(3, category=cat)
            comp = next((x for x in comp_candidates if x.sku != p.sku), None)
        if not comp:
            key = cat or next((k for k in COMPLEMENTOS.keys() if k in msg.lower()), None)
            if key:
                from .nlp import find_products as fp
                comp = next((x for x in fp(COMPLEMENTOS.get(key, "")) if x.sku != p.sku), None)
        if not comp:
            comp = top_margin(1, category=cat)[0] if cat and top_margin(1, category=cat) else top_margin(1)[0]

        reply = f"Agregué {qty} x {p.name} {p.brand}. Te recomiendo además: {comp.name} {comp.brand}."
        sugg = [{"sku": comp.sku, "text": f"{comp.name} {comp.brand} ${comp.price}"}]
        return JsonResponse({"reply": reply, "suggestions": sugg, "cart_html": _cart_html(request)})

    if it == "remove":
        products = find_products(msg, category=cat)
        if cat and not products:
            return JsonResponse({"reply": f"No se vende la categoría solicitada ('{cat}') en esta tienda.", "cart_html": _cart_html(request)})
        if products:
            _cart_remove(cart, products[0].sku)
            reply = "Listo. Ajusté tu carrito."
        else:
            reply = "Indica qué producto quieres quitar."
        return JsonResponse({"reply": reply, "cart_html": _cart_html(request)})

    if it == "show_cart":
        return JsonResponse({"reply": "Este es tu pedido actual.", "cart_html": _cart_html(request)})

    if it == "invoice":
        request.session["stage"] = "ask_invoice"
        return JsonResponse({"reply": "¿Necesitas factura? responde sí o no.", "cart_html": _cart_html(request)})

    if it == "checkout":
        request.session["stage"] = "ask_invoice"
        return JsonResponse({"reply": "Vamos a cerrar. ¿Necesitas factura? sí/no.", "cart_html": _cart_html(request)})

    # Mensaje desconocido → si hay categoría pero no vendemos, avisar. Si no, sugerencias generales.
    if cat and not top_margin(1, category=cat):
        return JsonResponse({"reply": f"No se vende la categoría solicitada ('{cat}') en esta tienda.", "cart_html": _cart_html(request)})

    options = top_margin(3, category=cat) if cat else top_margin(3)
    reply = "Te muestro opciones disponibles."
    sugg = [{"sku": p.sku, "text": f"{p.name} {p.brand} ${p.price}"} for p in options]
    return JsonResponse({"reply": reply, "suggestions": sugg, "cart_html": _cart_html(request)})

def receipt(request: HttpRequest, order_id: int):
    order = Order.objects.get(id=order_id)
    return render(request, "shopbot/receipt.html", {"order": order})