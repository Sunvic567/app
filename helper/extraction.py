"""
Pulls text out of an uploaded file so the classifier has something to
read. Handles PDFs (via pdfplumber) and plain text; falls back to the
filename alone if extraction fails or the file type isn't supported yet.

Scanned/image-only PDFs won't yield real text here — that's an OCR step
(e.g. pytesseract) worth adding once the text-based path is proven out,
noted as a stretch item rather than blocking the Day 2 milestone.
"""
import io

import pdfplumber


def extract_text(filename: str, file_bytes: bytes) -> str:
    lower = filename.lower()

    if lower.endswith(".pdf"):
        try:
            text_chunks = []
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_chunks.append(page_text)
            text = "\n".join(text_chunks).strip()
            if text:
                return text
            return f"[No extractable text found in PDF: {filename} — likely a scanned image.]"
        except Exception as exc:  # noqa: BLE001 — surface any parse failure as text for the classifier
            return f"[Failed to parse PDF '{filename}': {exc}]"

    if lower.endswith(".txt"):
        try:
            return file_bytes.decode("utf-8", errors="ignore")
        except Exception as exc:  # noqa: BLE001
            return f"[Failed to decode text file '{filename}': {exc}]"

    return f"[Unsupported file type for '{filename}' — no text extracted.]"
