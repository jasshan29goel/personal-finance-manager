from pydantic import BaseModel, Field
from typing import Literal, Annotated, Union
from domain.field_parser.pdf_extractor.between_pdf_extractor_config import BetweenPDFExtractorConfig
from domain.field_parser.pdf_extractor.float_near_keyword_pdf_extractor_config import FloatNearKeywordPDFExtractorConfig
from domain.field_parser.field_processors.noop_processor_config import NOOPProcessorConfig
from domain.field_parser.field_processors.transactions_llm_processor_config import TransactionsProcessorUsingLLMConfig

PDFExtractorConfig = Annotated[
    Union[BetweenPDFExtractorConfig, FloatNearKeywordPDFExtractorConfig],
    Field(discriminator="type")
]

ProcessorConfig = Annotated[
    Union[NOOPProcessorConfig, TransactionsProcessorUsingLLMConfig],
    Field(discriminator="type")
]
class PDFFieldParserConfig(BaseModel):
    type: Literal["pdf_attachment"]
    pdf_extractor: PDFExtractorConfig
    processor: ProcessorConfig

class EmailBodyFieldParserConfig(BaseModel):
    type: Literal["email_body"]

FieldParserConfig = Union[PDFFieldParserConfig, EmailBodyFieldParserConfig]
