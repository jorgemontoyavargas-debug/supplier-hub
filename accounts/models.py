from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Usuario humano de una empresa compradora o de un proveedor."""

    email = models.EmailField(_("correo electrónico"), unique=True)
    preferred_language = models.CharField(
        _("idioma preferido"), max_length=10, default="es"
    )

    def __str__(self):
        return self.get_full_name() or self.email or self.username

# Create your models here.
