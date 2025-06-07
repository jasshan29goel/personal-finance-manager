from typing import Any
from pydantic import BaseModel

class BasePDFExtractorConfig(BaseModel):
    type: str

    def extract_from_pdf(self, pdf_path: str) -> Any:
        raise NotImplementedError("Subclasses must implement `extract_from_pdf`")