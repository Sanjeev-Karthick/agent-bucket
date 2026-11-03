from pathlib import Path
from tempfile import TemporaryDirectory

SUPPORTED = {".txt", ".md", ".pdf", ".docx", ".html"}


class DocumentParser:
    def parse(self, key: str, data: bytes) -> str:
        suffix = Path(key).suffix.lower()
        if suffix in {".txt", ".md"}:
            return data.decode("utf-8")
        if suffix not in SUPPORTED:
            raise ValueError("Unsupported document format")
        from docling.datamodel.base_models import InputFormat
        from docling.datamodel.pipeline_options import PdfPipelineOptions
        from docling.document_converter import DocumentConverter, PdfFormatOption

        options = PdfPipelineOptions()
        options.do_ocr = False
        options.enable_remote_services = False
        converter = DocumentConverter(
            allowed_formats=[InputFormat.PDF, InputFormat.DOCX, InputFormat.HTML],
            format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=options)},
        )
        with TemporaryDirectory(prefix="agent-bucket-") as directory:
            path = Path(directory) / f"document{suffix}"
            path.write_bytes(data)
            return str(converter.convert(path).document.export_to_markdown())


def chunk_text(text: str, size: int, overlap: int) -> list[str]:
    if size <= 0 or overlap < 0 or overlap >= size:
        raise ValueError("Invalid chunk size or overlap")
    chunks = []
    start = 0
    while start < len(text):
        chunk = text[start : start + size].strip()
        if chunk:
            chunks.append(chunk)
        if start + size >= len(text):
            break
        start += size - overlap
    return chunks
