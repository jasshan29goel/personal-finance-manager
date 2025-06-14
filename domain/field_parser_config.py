from pydantic import BaseModel, Field
from typing import Literal, Annotated, Union, Optional


# === Extractor Config Models ===
class BetweenPDFExtractorConfig(BaseModel):
    type: Literal["between"]
    start: str
    end: Optional[str]


class FloatNearKeywordPDFExtractorConfig(BaseModel):
    type: Literal["float_near_keyword"]
    keyword: str
    location: Literal["RIGHT", "LEFT", "BELOW", "ABOVE"]


# === Processor Config Models ===
class NOOPProcessorConfig(BaseModel):
    type: Literal["noop"]


class TransactionsProcessorUsingLLMConfig(BaseModel):
    type: Literal["llm"]
    model: str = "gpt-4.1-mini"


PDFExtractorConfig = Annotated[
    Union[BetweenPDFExtractorConfig, FloatNearKeywordPDFExtractorConfig],
    Field(discriminator="type"),
]

ProcessorConfig = Annotated[
    Union[NOOPProcessorConfig, TransactionsProcessorUsingLLMConfig],
    Field(discriminator="type"),
]


class PDFFieldParserConfig(BaseModel):
    type: Literal["pdf_attachment"]
    pdf_extractor: PDFExtractorConfig
    processor: ProcessorConfig


class EmailBodyFieldParserConfig(BaseModel):
    type: Literal["email_body"]


FieldParserConfig = Annotated[
    Union[PDFFieldParserConfig, EmailBodyFieldParserConfig], Field(discriminator="type")
]
