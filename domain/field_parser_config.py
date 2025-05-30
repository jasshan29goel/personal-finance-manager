from typing import Union
from pydantic import BaseModel
from typing import List, Literal

class TableChunkingConfig(BaseModel):
    type: Literal['table']
    required_headers: List[str]

class BetweenChunkingConfig(BaseModel):
    type: Literal['between']
    start: str
    end: str

class PageRangeChunkingConfig(BaseModel):
    type: Literal['page_range']
    start_page: int
    end_page: int

ChunkingConfig = Union[
    TableChunkingConfig,
    BetweenChunkingConfig,
    PageRangeChunkingConfig
]

class FieldParserConfig(BaseModel):
    source: Literal['attachment', 'email_body']
    chunking: ChunkingConfig
    processor: str
