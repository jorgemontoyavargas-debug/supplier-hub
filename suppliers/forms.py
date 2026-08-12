from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.utils import timezone

from accounts.models import User

from .models import Supplier, SupplierContact, SupplierInvitation


class SupplierCreateForm(forms.ModelForm):
    contact_first_name = forms.CharField(label="Nombres del contacto", max_length=120)
    contact_last_name = forms.CharField(
        label="Apellidos del contacto", max_length=120, required=False
    )
    contact_email = forms.EmailField(label="Correo del contacto")

    class Meta:
        model = Supplier
        fields = ("legal_name", "trade_name", "tax_id", "country_code")

    @transaction.atomic
    def save_for_organization(self, *, organization, created_by):
        supplier = self.save(commit=False)
        supplier.organization = organization
        supplier.created_by = created_by
        supplier.status = Supplier.Status.DRAFT
        supplier.save()
        SupplierContact.objects.create(
            supplier=supplier,
            first_name=self.cleaned_data["contact_first_name"],
            last_name=self.cleaned_data["contact_last_name"],
            email=self.cleaned_data["contact_email"].lower(),
            is_primary=True,
        )
        return supplier


class SupplierRegistrationForm(UserCreationForm):
    first_name = forms.CharField(label="Nombres", max_length=120)
    last_name = forms.CharField(label="Apellidos", max_length=120, required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("first_name", "last_name", "password1", "password2")

    def __init__(self, *args, invitation: SupplierInvitation, **kwargs):
        super().__init__(*args, **kwargs)
        self.invitation = invitation

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.invitation.email
        user.email = self.invitation.email
        if commit:
            user.save()
            contact, _ = SupplierContact.objects.get_or_create(
                supplier=self.invitation.supplier,
                email=self.invitation.email,
                defaults={
                    "first_name": self.cleaned_data["first_name"],
                    "last_name": self.cleaned_data["last_name"],
                    "is_primary": True,
                },
            )
            contact.first_name = self.cleaned_data["first_name"]
            contact.last_name = self.cleaned_data["last_name"]
            contact.portal_user = user
            contact.save()
            self.invitation.accepted_at = timezone.now()
            self.invitation.save(update_fields=("accepted_at", "updated_at"))
            supplier = self.invitation.supplier
            supplier.status = Supplier.Status.ACTIVE
            supplier.save(update_fields=("status", "updated_at"))
        return user
