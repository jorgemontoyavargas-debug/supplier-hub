from django.urls import path

from . import views

urlpatterns = [
    path("", views.supplier_list, name="supplier_list"),
    path("nuevo/", views.supplier_create, name="supplier_create"),
    path("portal/", views.supplier_portal, name="supplier_portal"),
    path("invitacion/<str:token>/", views.accept_invitation, name="accept_invitation"),
    path("<uuid:supplier_id>/", views.supplier_detail, name="supplier_detail"),
    path("<uuid:supplier_id>/invitar/", views.invite_supplier, name="invite_supplier"),
]
