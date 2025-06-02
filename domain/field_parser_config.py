from typing import Union
from pydantic import BaseModel
from typing import List, Literal, Optional

class BetweenChunkingConfig(BaseModel):
    type: Literal['between']
    start: str
    end: Optional[str]

ChunkingConfig = Union[
    BetweenChunkingConfig
]

class LLMProcessorConfig(BaseModel):
    type: Literal['llm']
    model: str = "gpt-4.1-mini"

class NOOPProcessorConfig(BaseModel):
    type: Literal['noop']

ProcessorConfig = Union[
    LLMProcessorConfig,
    NOOPProcessorConfig
]

class FieldParserConfig(BaseModel):
    source: Literal['attachment', 'email_body']
    chunking: ChunkingConfig
    processor: ProcessorConfig
