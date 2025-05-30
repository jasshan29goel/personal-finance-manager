from typing import List, Dict, Optional
from .field_parser_config import FieldParserConfig

class EmailConfig:
    def __init__(
        self,
        id: str,
        from_addresses: List[str],
        subject_keywords: List[str],
        field_parsers: Dict[str, FieldParserConfig],
        run: bool
    ):
        self.id = id
        self.from_addresses = [f.lower() for f in from_addresses]
        self.subject_keywords = [s.lower() for s in subject_keywords]
        self.field_parsers = field_parsers
        self.run = run

    def matches_email(self, from_header: str, subject: str) -> bool:
        from_header = from_header.lower()
        subject = subject.lower()
        return (
            any(sender in from_header for sender in self.from_addresses) and
            any(keyword in subject for keyword in self.subject_keywords)
        )

    def get_field_parser(self, field_name: str) -> Optional[FieldParserConfig]:
        return self.field_parsers.get(field_name)

    @classmethod
    def from_dict(cls, raw: dict):
        raw_field_parsers = raw.get("field_parsers", {})
        parsed_field_parsers = {
            key: FieldParserConfig(**value)
            for key, value in raw_field_parsers.items()
        }
        return cls(
            id=raw['id'],
            from_addresses=raw.get('from', []),
            subject_keywords=raw.get('subject_keywords', []),
            field_parsers=parsed_field_parsers,
            run=raw.get('run', False)
        )
