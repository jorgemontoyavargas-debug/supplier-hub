from django.contrib import admin

from .models import AIAnalysisRun, AISuggestion


class AISuggestionInline(admin.TabularInline):
    model = AISuggestion
    extra = 0
    readonly_fields = (
        "field_code",
        "proposed_value",
        "confidence",
        "evidence_text",
        "page_number",
        "status",
        "resolved_by",
        "resolved_at",
    )


@admin.register(AIAnalysisRun)
class AIAnalysisRunAdmin(admin.ModelAdmin):
    list_display = ("created_at", "case", "provider", "model_name", "status")
    list_filter = ("provider", "status", "organization")
    readonly_fields = (
        "organization",
        "case",
        "document",
        "requested_by",
        "provider",
        "model_name",
        "prompt_version",
        "status",
        "error",
    )
    inlines = (AISuggestionInline,)

# Register your models here.
