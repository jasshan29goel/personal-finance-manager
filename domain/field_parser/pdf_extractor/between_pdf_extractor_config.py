from domain.field_parser.pdf_extractor.base_pdf_extractor_config import BasePDFExtractorConfig
from typing import Optional, Literal, List
import pdfplumber

class BetweenPDFExtractorConfig(BasePDFExtractorConfig):
    type: Literal['between']
    start: str
    end: Optional[str]

    """
    Extracts text from each page of the PDF starting from a start marker to an optional end marker.
    
    Args:
        pdf_path: Path to the PDF file.
        start: The starting text marker.
        end: The ending text marker (optional).
    
    Returns:
        A list of dictionaries containing page number and extracted content.
    """
    def extract_from_pdf(self, pdf_path: str) -> List[str]:
        results = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text(layout=True) or ""
                    start_idx = text.find(self.start)
                    if start_idx == -1:
                        continue # skip page if marker not found

                    if self.end:
                        end_idx = text.find(self.end, start_idx)
                        content = text[start_idx:end_idx].strip() if end_idx != -1 else text[start_idx:].strip()
                    else:
                        content = text[start_idx:].strip()

                    results.append(content)
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {e}")

        return results