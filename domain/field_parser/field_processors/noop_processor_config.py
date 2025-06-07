from typing import Literal, Any
from domain.field_parser.field_processors.base_processor_config import BaseProcessorConfig

class NOOPProcessorConfig(BaseProcessorConfig):
    type: Literal['noop']

    def process_field(self, field_name: str, extracted_content: Any) -> tuple[Any, str]:
        return extracted_content, "Nothing to be done here"
