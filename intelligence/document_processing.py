import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DocumentPage:
    number: int
    text: str


def extract_pages(path):
    engine = os.getenv("SUPPLIER_HUB_DOCUMENT_ENGINE", "pypdf")
    if engine == "docling":
        return _extract_with_docling(path)
    return _extract_with_pypdf(path)


def _extract_with_pypdf(path):
    from pypdf import PdfReader

    if Path(path).suffix.lower() != ".pdf":
        raise ValueError("El extractor básico admite PDF con texto embebido.")
    reader = PdfReader(path)
    pages = [
        DocumentPage(number=index, text=(page.extract_text() or "").strip())
        for index, page in enumerate(reader.pages, start=1)
    ]
    if not any(page.text for page in pages):
        raise ValueError(
            "El PDF no contiene texto. Activa Docling/OCR para documentos escaneados."
        )
    return pages


def _extract_with_docling(path):
    try:
        from docling.document_converter import DocumentConverter
    except ImportError as error:
        raise RuntimeError(
            "Docling no está instalado. Usa el perfil opcional de IA documental."
        ) from error
    result = DocumentConverter().convert(path)
    text = result.document.export_to_markdown()
    return [DocumentPage(number=1, text=text)]
