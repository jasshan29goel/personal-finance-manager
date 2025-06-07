from typing import Any
from pydantic import BaseModel

class BaseProcessorConfig(BaseModel):
    type: str

    def process_field(self, field_name: str, extracted_content) -> tuple[Any, str]:
        raise NotImplementedError("Subclasses must implement `process_field`")