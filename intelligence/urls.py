from django.urls import path

from . import views

urlpatterns = [
    path("expedientes/<uuid:case_id>/", views.case_assistance, name="case_assistance"),
    path("documentos/<uuid:document_id>/analizar/", views.analyze_evidence, name="analyze_evidence"),
    path("propuestas/<uuid:suggestion_id>/resolver/", views.resolve_ai_suggestion, name="resolve_ai_suggestion"),
]
