import pdfplumber
from typing import List, Optional
from domain.field_parser_config import FieldParserConfig, BetweenChunkingConfig
from collections import defaultdict

def apply_extraction(config: FieldParserConfig, pdf_path: str):
    """
    Applies table extraction strategy to the PDF, returning all tables that match the required headers.
    """
    chunking = config.chunking
    
    if isinstance(chunking, BetweenChunkingConfig):
        return extract_from_text_per_page(pdf_path=pdf_path, start=chunking.start, end=chunking.end)

    raise ValueError(f"Unsupported chunking type: {chunking.type}")

def extract_from_text_per_page(pdf_path: str, start: str, end: Optional[str] = None) -> List[str]:
    """
    Extracts text from each page of the PDF starting from a start marker to an optional end marker.
    
    Args:
        pdf_path: Path to the PDF file.
        start: The starting text marker.
        end: The ending text marker (optional).
    
    Returns:
        A list of dictionaries containing page number and extracted chunk.
    """
    results = []

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text(layout=True) or ""
                start_idx = text.find(start)
                if start_idx == -1:
                    continue  # skip page if start marker not found

                if end:
                    end_idx = text.find(end, start_idx)
                    chunk = text[start_idx:end_idx].strip() if end_idx != -1 else text[start_idx:].strip()
                else:
                    chunk = text[start_idx:].strip()

                results.append(chunk)

        return results

    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {e}")
