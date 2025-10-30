import re, unicodedata
from typing import List, Optional
from decimal import Decimal
from .models import Product

IVA = Decimal("0.16")

def norm(s: str) -> str:
    s = s.lower()
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    return s

# Detección de categorías en texto
CATEGORY_PATTERNS = {
    "coca":      r"\b(coca(\s|-)?cola|refresco\s*coca|coca\s*600)\b",
    "pepsi":     r"\b(pepsi|refresco\s*pepsi)\b",
    "agua":      r"\b(agua|bonafont|epura|ciel)\b",
    "pan":       r"\b(pan|bimbo)\b",
    "leche":     r"\b(leche|lala|alpura)\b",
    "huevo":     r"\b(huevo|docena)\b",
    "atun":      r"\b(at[uú]n|dolores|tuni)\b",
    "aceite":    r"\b(aceite)\b",
    "cafe":      r"\b(caf[eé]|nescafe|soluble)\b",
    "harina":    r"\b(maseca|harina)\b",
    "jabonzote": r"\b(zote|jab[oó]n)\b",
    "shampoo":   r"\b(shampoo|head\s*&?\s*shoulders|h&s)\b",
    "papas":     r"\b(papas|sabritas)\b",
    "oreo":      r"\b(oreo|galletas)\b",
}

# Aliases para aumentar recall
ALIASES = {
    "coca": ["coca cola","coca-cola","coca600","coca 600","refresco coca"],
    "pepsi": ["pepsi","refresco pepsi"],
    "agua": ["agua","bonafont","epura","ciel"],
    "pan": ["pan bimbo","pan blanco","bimbo"],
    "leche": ["leche lala","leche alpura","leche"],
    "huevo": ["huevo","docena huevo"],
    "atun": ["atun","atun dolores","atun tuni"],
    "aceite": ["aceite","aceite 1l"],
    "cafe": ["cafe","nescafe","cafe soluble"],
    "harina": ["maseca","harina"],
    "jabonzote": ["zote","jabon zote"],
    "shampoo": ["shampoo","head shoulders","h&s"],
    "papas": ["sabritas","papas fritas"],
    "oreo": ["oreo","galletas oreo","galletas"],
}

COMPLEMENTOS = {
    "leche": "galletas oreo",
    "pan": "mantequilla",
    "cafe": "crema en polvo",
    "agua": "papas",
    "huevo": "aceite",
    "harina": "aceite",
    "coca": "papas",
    "pepsi": "papas",
}

def extract_qty(msg: str) -> int:
    m = re.search(r"(?:x|por|de)?\s*(\d{1,2})\b", msg)
    return int(m.group(1)) if m else 1

def extract_category(msg: str) -> Optional[str]:
    q = norm(msg)
    for cat, pat in CATEGORY_PATTERNS.items():
        if re.search(pat, q):
            return cat
    return None

def find_products(msg: str, category: Optional[str] = None) -> List[Product]:
    q = norm(msg)
    hits = set()

    # 1) por alias
    for key, arr in ALIASES.items():
        if category and key != category:
            continue
        for a in arr:
            if norm(a) in q:
                qs = Product.objects.filter(category__icontains=key) | Product.objects.filter(name__icontains=key)
                hits.update(qs)

    # 2) tokens
    tokens = [t for t in re.findall(r"[a-zA-Záéíóúñ0-9]+", msg) if len(t) >= 3]
    base_qs = Product.objects.all()
    if category:
        base_qs = base_qs.filter(category__icontains=category)
    for t in tokens:
        hits.update(
            base_qs.filter(name__icontains=t) |
            base_qs.filter(brand__icontains=t) |
            base_qs.filter(category__icontains=t)
        )
    return list(hits)

def top_margin(n=3, category: Optional[str]=None) -> List[Product]:
    qs = Product.objects.all()
    if category:
        qs = qs.filter(category__icontains=category)
    return sorted(qs, key=lambda p: (p.margin_rate(), p.margin_abs()), reverse=True)[:n]

def brand_in_msg(msg: str) -> Optional[str]:
    q = norm(msg)
    brands = Product.objects.values_list("brand", flat=True).distinct()
    for b in brands:
        if norm(b) in q:
            return b
    m = re.search(r"marca\s+([a-zA-Z0-9ñáéíóú\-]+)", q)
    return m.group(1) if m else None

def known_brand(b: str) -> bool:
    if not b:
        return False
    brands = set(Product.objects.values_list("brand", flat=True))
    return any(norm(b) == norm(x) for x in brands)

def intent(msg: str) -> str:
    q = norm(msg)
    if any(w in q for w in ["pagar","cobrar","finalizar","terminar","checkout"]):
        return "checkout"
    if any(w in q for w in ["carrito","pedido","ver carrito"]):
        return "show_cart"
    if any(w in q for w in ["quitar","eliminar","remueve"]):
        return "remove"
    if any(w in q for w in ["factura","rfc"]):
        return "invoice"
    if any(w in q for w in ["efectivo","tarjeta","transferencia","oxxo"]):
        return "pay"
    if re.search(r"\b\d{1,2}\b", q) or any(w in q for w in ["agrega","añade","dame","quiero","llevo","pon","vende","ofrece"]):
        return "add"
    return "unknown"