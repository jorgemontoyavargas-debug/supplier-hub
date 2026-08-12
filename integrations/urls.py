from django.urls import path

from . import views

urlpatterns = [path("v1/suppliers", views.suppliers_api, name="api_suppliers")]
