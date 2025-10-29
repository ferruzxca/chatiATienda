from django.urls import path
from . import views

urlpatterns = [
    path("", views.chat, name="chat"),
    path("api/message/", views.api_message, name="api_message"),
    path("api/add/", views.api_add_product, name="api_add_product"),
    path("recibo/<int:order_id>/", views.receipt, name="receipt"),
]
