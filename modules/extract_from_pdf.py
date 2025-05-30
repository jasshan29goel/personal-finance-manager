import pdfplumber
from typing import List, Optional
from domain.field_parser_config import FieldParserConfig, TableChunkingConfig, BetweenChunkingConfig

def apply_extraction(config: FieldParserConfig, pdf_path: str):
    """
    Applies table extraction strategy to the PDF, returning all tables that match the required headers.
    """
    chunking = config.chunking

    if isinstance(chunking, TableChunkingConfig):
        return _extract_matching_tables(pdf_path, chunking.required_headers)
    
    if isinstance(chunking, BetweenChunkingConfig):
        return _extract_between_from_pdf(pdf_path, chunking.start, chunking.end)

    raise ValueError(f"Unsupported chunking type: {chunking.type}")

def _extract_between_from_pdf(pdf_path: str, start: str, end: str) -> Optional[str]:
    """
    Extracts text between two markers from the full PDF text.
    
    Args:
        pdf_path: Path to the PDF file.
        start: Start string to locate.
        end: End string to locate after start.
    
    Returns:
        The substring between start and end, or None if not found.
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = "\n".join(page.extract_text() or "" for page in pdf.pages)

        start_idx = full_text.find(start)
        if start_idx == -1:
            return None

        start_idx += len(start)
        end_idx = full_text.find(end, start_idx)
        if end_idx == -1:
            return None

        return full_text[start_idx:end_idx].strip() or None

    except Exception as e:
        raise ValueError(f"Failed to extract between text from PDF: {e}")

def _extract_matching_tables(pdf_path: str, required_headers: List[str]) -> List[List[List[Optional[str]]]]:
    matching_tables = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                if any(_has_all_required_headers(row, required_headers) for row in table):
                    matching_tables.append(table)

    return matching_tables

def _has_all_required_headers(row: List[Optional[str]], required_headers: List[str]) -> bool:
    return all(any(req in str(cell) if cell is not None else "" for cell in row) for req in required_headers)
