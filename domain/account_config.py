from typing import List, Optional

class AccountConfig:
    def __init__(
        self,
        id: str,
        from_addresses: List[str],
        subject_keywords: List[str],
        table_matcher: Optional[dict] = None
    ):
        self.id = id
        self.from_addresses = [f.lower() for f in from_addresses]
        self.subject_keywords = [s.lower() for s in subject_keywords]
        self.table_matcher = table_matcher or {}

    def matches_email(self, from_header: str, subject: str) -> bool:
        from_header = from_header.lower()
        subject = subject.lower()
        return (
            any(sender in from_header for sender in self.from_addresses) and
            any(keyword in subject for keyword in self.subject_keywords)
        )

    def required_headers(self) -> List[str]:
        return [h.lower().strip() for h in self.table_matcher.get("required_headers", [])]

    @classmethod
    def from_dict(cls, raw: dict):
        return cls(
            id=raw['id'],
            from_addresses=raw.get('from', []),
            subject_keywords=raw.get('subject_keywords', []),
            table_matcher=raw.get('table_matcher', {})
        )
