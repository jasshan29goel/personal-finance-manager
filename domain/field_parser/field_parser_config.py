from pydantic import BaseModel, Field
from typing import Literal, Annotated, Union, Any
from domain.field_parser.pdf_extractor.between_pdf_extractor_config import BetweenPDFExtractorConfig
from domain.field_parser.pdf_extractor.float_near_keyword_pdf_extractor_config import FloatNearKeywordPDFExtractorConfig
from domain.field_parser.field_processors.noop_processor_config import NOOPProcessorConfig
from domain.field_parser.field_processors.transactions_llm_processor_config import TransactionsProcessorUsingLLMConfig
from domain.field_parser.field_parser_utils import populate_transaction_alignment_scores

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
    def post_validate(self, field_name: str, result: Any, pdf_path: str) -> None:
        if field_name == 'transactions':
            populate_transaction_alignment_scores(pdf_path, result)


class EmailBodyFieldParserConfig(BaseModel):
    type: Literal["email_body"]

FieldParserConfig = Union[PDFFieldParserConfig, EmailBodyFieldParserConfig]
