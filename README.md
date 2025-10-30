# 🛒 Chat Abarrotero IA — Sistema Experto de Ventas con Django + SP/SBR

El **Chat Abarrotero Inteligente** es un sistema experto en **Django** que automatiza la venta conversacional en una tienda de abarrotes usando **Sistemas de Producción (SP)** y **Sistemas Basados en Reglas (SBR)**. Reconoce intención, valida categoría y marca, sugiere sustitutos de **alto margen**, arma el carrito, calcula **IVA**, genera **ticket** o **factura** simulada y solicita correo para promociones.

---

## 🎯 Objetivo

Entregar un chatbot funcional orientado a **maximizar margen** y **cerrar ventas** mediante **reglas SI→ENTONCES** y un **motor de inferencia** con encadenamiento hacia adelante.

---

## 🧠 Modelo de IA

- Sistema de Producción (SP) con **Base de Hechos** dinámica
- **SBR** con políticas de prioridad: *disponibilidad > margen > upsell > cierre*
- Reglas SI→ENTONCES para: detección de categoría, sustitución, upsell, cobro, factura
- Manejo explícito de casos: **producto inexistente**, **categoría no vendida**, **marca no registrada**

---

## 🏗️ Arquitectura

**Tres componentes SP/SBR**: **Base de Hechos**, **Base de Reglas**, **Motor de Inferencia**.  
Integración en Django: vistas web para chat, sesión como memoria de trabajo, SQLite como catálogo, plantillas HTML/CSS/JS para interfaz.

Diagrama de operación y diagrama del motor incluidos en formato **.drawio** (ver sección de diagramas).

---

## 🚀 Tecnologías

- Python **3.12** recomendado (3.14 no soportado por Django estable)
- Django **4.2 LTS**
- HTML + CSS + JavaScript
- SQLite
- Draw.io (diagrams.net) para diagramas

---

## 📁 Estructura del proyecto

```
grocerbot/
├─ manage.py
├─ requirements.txt
├─ db.sqlite3
├─ shopbot/
│  ├─ __init__.py
│  ├─ models.py
│  ├─ views.py
│  ├─ nlp.py
│  ├─ admin.py
│  ├─ urls.py
│  ├─ management/
│  │  └─ commands/
│  │     └─ seed_products.py
│  ├─ templates/
│  │  └─ shopbot/
│  │     ├─ chat.html
│  │     ├─ _cart.html
│  │     └─ receipt.html
│  └─ static/
│     ├─ css/style.css
│     └─ js/chat.js
└─ docs/
   ├─ flujo_completo_chat_abarrotero.drawio
   └─ motor_spsbr_chat_abarrotero.drawio
```

> Si tus .drawio están fuera de `docs/`, muévelos o actualiza las rutas del README.

---

## ⚙️ Instalación rápida (macOS con Homebrew)

```bash
git clone https://github.com/TU_USUARIO/grocerbot.git
cd grocerbot
brew install python@3.12
$($(brew --prefix)/opt/python@3.12/bin/python3.12 -m venv .venv)
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
printf "Django>=4.2,<5\n" > requirements.txt
pip install -r requirements.txt
```

---

## 🗄️ Migraciones y datos de ejemplo

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py seed_products --reset
```

---

## ▶️ Ejecutar el servidor

```bash
python manage.py runserver
```

Navega a: **http://127.0.0.1:8000/**

---

## 💬 Guía de uso del chat

Ejemplos de interacción y resultado esperado:
- “Quiero una Coca-Cola 600” → agrega al carrito y propone **upsell**.
- “Dame Pepsi frambuesa” → no existe, sugiere **top 3** de bebidas por margen.
- “Quiero arroz marca La Montaña” → marca no registrada; ofrece **3 equivalentes**.
- “Pagar” → calcula subtotal + **IVA 16%**, genera **ticket** y pregunta por **factura**.
- “Sí, factura” → solicita **RFC** y correo para enviar comprobante.

El chat mantiene **estado** por sesión: carrito, etapa del flujo y totales.

---

## 🧩 Núcleo lógico (resumen técnico)

- `nlp.py`: normaliza texto, extrae **cantidad**, **categoría**, **marca** y detecta **intención**.
- `views.py`: orquesta el flujo; si categoría no existe, responde que **no se vende** y muestra opciones; si marca no existe, ofrece **alternativas de alto margen**; si producto exacto no se halla, sugiere **equivalentes**.
- `models.py`: `Product` con `price`, `cost` y helpers de **margen**; `Order` y `OrderItem` para cierre.
- `seed_products.py`: catálogo base reproducible.

---

## 🧾 Ticket y factura simulada

Durante el **checkout** el sistema calcula subtotal, **IVA 16%** y total.  
Si el usuario solicita **factura**, pide **RFC** y **correo**; si no, emite **ticket**.  
Se registran pedidos en la base para auditoría simple.

---

## 🗺️ Diagramas (Draw.io)

Descarga y abre en **diagrams.net**:
- **Flujo completo del Chat**: [`docs/flujo_completo_chat_abarrotero.drawio`](docs/flujo_completo_chat_abarrotero.drawio)
- **Motor SP/SBR y ciclo de inferencia**: [`docs/motor_spsbr_chat_abarrotero.drawio`](docs/motor_spsbr_chat_abarrotero.drawio)

Si necesitas PNG/SVG, exporta desde draw.io o solicita versiones renderizadas.

---

## 🧪 Pruebas manuales sugeridas

- Producto **existente** y **no existente** por categoría.
- Marca **no registrada** con categoría válida.
- Flujo de **remoción** del carrito y **ver carrito**.
- **Cierre** con y sin factura.
- **Reinicio** de carrito mediante recarga o endpoint de reset (si se habilitó).

---

## 🛠️ Solución de problemas

**Error:** *ModuleNotFoundError: No module named 'django'*  
Causa: venv activo sin dependencias.  
Solución: `pip install -r requirements.txt` y reintenta.

**Error:** *Django<6,>=5.0 no disponible / Python 3.14*  
Causa: Django estable no soporta 3.14.  
Solución: usar **Python 3.12**, reinstalar venv y `Django>=4.2,<5`.

**Error:** *ProtectedError al seedear productos*  
Causa: hay `OrderItem` que referencia `Product`.  
Solución: usar `--reset` que limpia respetando integridad o eliminar órdenes de prueba.

---

## 🤝 Contribuir

- Issues y PRs bienvenidos. Estructura reglas en `nlp.py` y políticas en `views.py`.
- Propuestas: nuevas categorías, reglas de **upsell**, métricas de conversión y margen.

---

## 📜 Licencia

MIT o la que prefieras. Agrega un archivo `LICENSE`.

---

## 👤 Autor

**Ferruzca** — Proyecto académico de **IA Simbólica** aplicada a ventas minoristas.  
Si te sirve, deja una ⭐ en GitHub.

