from django.contrib import admin

from .models import (
    EvidenceDocument,
    QualificationCase,
    QualificationTemplate,
    Requirement,
    RequirementResponse,
)


class RequirementInline(admin.TabularInline):
    model = Requirement
    extra = 0


@admin.register(QualificationTemplate)
class QualificationTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "version", "organization", "is_active")
    list_filter = ("organization", "is_active")
    search_fields = ("name",)
    inlines = (RequirementInline,)


class RequirementResponseInline(admin.TabularInline):
    model = RequirementResponse
    extra = 0


class EvidenceDocumentInline(admin.TabularInline):
    model = EvidenceDocument
    extra = 0


@admin.register(QualificationCase)
class QualificationCaseAdmin(admin.ModelAdmin):
    list_display = ("supplier", "template", "status", "created_at")
    list_filter = ("status", "organization")
    autocomplete_fields = ("organization", "supplier", "template")
    inlines = (RequirementResponseInline, EvidenceDocumentInline)

# Register your models here.
