import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Any, Tuple
from app.extractor.normalizer import normalize_text

class PDFExtractionResult:
    def __init__(
        self,
        success: bool,
        status: str,  # EXTRACTED, OCR_REQUIRED, EXTRACTION_FAILED
        page_count: int,
        pages: List[Dict[str, Any]],  # [{"page_number": int, "raw_text": str, "normalized_text": str}]
        metadata: Dict[str, Any],
        error_message: str = ""
    ):
        self.success = success
        self.status = status
        self.page_count = page_count
        self.pages = pages
        self.metadata = metadata
        self.error_message = error_message

def extract_pdf_content(pdf_path: str | Path) -> PDFExtractionResult:
    """
    Extracts text page-aware from a local PDF using PyMuPDF.
    Returns structured page text, page numbers, and extraction status.
    """
    path_obj = Path(pdf_path)
    if not path_obj.exists():
        return PDFExtractionResult(
            success=False,
            status="EXTRACTION_FAILED",
            page_count=0,
            pages=[],
            metadata={},
            error_message=f"File not found: {pdf_path}"
        )

    try:
        doc = fitz.open(str(path_obj))
        page_count = len(doc)
        if page_count == 0:
            doc.close()
            return PDFExtractionResult(
                success=False,
                status="EXTRACTION_FAILED",
                page_count=0,
                pages=[],
                metadata={},
                error_message="Empty PDF document"
            )

        pages = []
        total_extracted_chars = 0

        for idx, page in enumerate(doc):
            page_num = idx + 1
            raw_text = page.get_text("text") or ""
            norm_text = normalize_text(raw_text)
            total_extracted_chars += len(norm_text)
            
            pages.append({
                "page_number": page_num,
                "raw_text": raw_text,
                "normalized_text": norm_text
            })

        metadata = {
            "title": doc.metadata.get("title", ""),
            "author": doc.metadata.get("author", ""),
            "subject": doc.metadata.get("subject", ""),
            "creationDate": doc.metadata.get("creationDate", ""),
            "modDate": doc.metadata.get("modDate", "")
        }
        doc.close()

        # Check if text is too sparse (indicating scanned/image PDF requiring OCR)
        avg_chars_per_page = total_extracted_chars / max(1, page_count)
        if avg_chars_per_page < 30 and page_count > 0:
            status = "OCR_REQUIRED"
        else:
            status = "EXTRACTED"

        return PDFExtractionResult(
            success=True,
            status=status,
            page_count=page_count,
            pages=pages,
            metadata=metadata
        )

    except Exception as e:
        return PDFExtractionResult(
            success=False,
            status="EXTRACTION_FAILED",
            page_count=0,
            pages=[],
            metadata={},
            error_message=str(e)
        )
