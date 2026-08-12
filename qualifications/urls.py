from django.urls import path

from . import views

urlpatterns = [
    path("iniciar/<uuid:supplier_id>/", views.start_case, name="start_qualification"),
    path("<uuid:case_id>/", views.qualification_case, name="qualification_case"),
    path(
        "documentos/<uuid:document_id>/",
        views.download_evidence,
        name="download_evidence",
    ),
]
