from django.urls import path

from . import web_views

urlpatterns = [
    path("proveedores/csv/", web_views.supplier_csv, name="supplier_csv"),
]
