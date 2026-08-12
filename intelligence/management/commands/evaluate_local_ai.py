import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from intelligence.document_processing import DocumentPage
from intelligence.providers import RuleBasedProvider
from intelligence.services import ALLOWED_FIELDS


class Command(BaseCommand):
    help = "Ejecuta el conjunto sintético reproducible de extracción local."

    def handle(self, *args, **options):
        dataset_path = (
            Path(__file__).resolve().parents[2] / "evals" / "document_extraction.json"
        )
        dataset = json.loads(dataset_path.read_text(encoding="utf-8"))
        passed = 0
        failures = []
        provider = RuleBasedProvider()
        for sample in dataset:
            pages = [
                DocumentPage(number=index, text=text)
                for index, text in enumerate(sample["pages"], start=1)
            ]
            actual = {
                proposal.field_code: proposal.value
                for proposal in provider.analyze(
                    pages=pages, allowed_fields=ALLOWED_FIELDS
                )
            }
            if actual == sample["expected"]:
                passed += 1
            else:
                failures.append(
                    {"name": sample["name"], "expected": sample["expected"], "actual": actual}
                )
        self.stdout.write(f"Evaluaciones correctas: {passed}/{len(dataset)}")
        if failures:
            raise CommandError(json.dumps(failures, ensure_ascii=False, indent=2))
