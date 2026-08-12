from django.core.management.base import BaseCommand, CommandError

from integrations.models import APICredential
from organizations.models import Organization


class Command(BaseCommand):
    help = "Crea una credencial API y muestra su valor una sola vez."

    def add_arguments(self, parser):
        parser.add_argument("--organization", required=True, help="Slug de la organización")
        parser.add_argument("--name", required=True, help="Nombre descriptivo")

    def handle(self, *args, **options):
        try:
            organization = Organization.objects.get(slug=options["organization"])
        except Organization.DoesNotExist as error:
            raise CommandError("Organización no encontrada.") from error
        credential, raw_key = APICredential.issue(
            organization=organization, name=options["name"]
        )
        self.stdout.write(self.style.SUCCESS(f"Credencial creada: {credential.name}"))
        self.stdout.write(raw_key)
        self.stdout.write("Guárdala ahora: Supplier Hub no conserva el valor original.")
