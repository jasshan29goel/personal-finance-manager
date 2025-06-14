import pdfplumber
import re
import tiktoken
import json
from typing import List, Any, Optional
from difflib import SequenceMatcher
from domain.transaction import Transaction


# ✅ Matches:
#   "₹1,234.56"        → Valid number with currency symbol and decimals
#   "  -1,000"         → Valid negative number with leading space
#   "$123"             → Valid integer with prefix
#   "1,000"            → Valid comma-separated thousands
#   "1000"             → Valid plain integer
#   "123456.78"        → Valid plain decimal
#   "-123.45"          → Valid negative decimal
#
# ❌ Does NOT match:
#   "12,34"            → Incorrect comma grouping
#   "1,23,456"         → Incorrect comma grouping
#   "abc123"           → Letters before number not allowed unless non-digit
#   "123abc"           → Letters after number not allowed
#   "--123"            → Double negative sign not allowed
#   "1 000"            → Space instead of comma not allowed
#   "1,000.00.00"      → Multiple decimals not allowed

CURRENCY_REGEX = re.compile(r"^[^\d\-]*([\-]?\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+(?:\.\d+)?)$")

def extract_amount_from_text(text: str) -> Optional[float]:
    """
    Extracts a float from a string that may have currency symbols or garbage characters.
    Returns float if valid, else None.
    """
    match = CURRENCY_REGEX.match(text.strip())
    if match:
        num = match.group(1).replace(",", "")
        try:
            return float(num)
        except ValueError:
            return None
    return None

def is_float(text: str) -> bool:
    return extract_amount_from_text(text) is not None


def count_tokens(text: str, model: str = "gpt-4") -> int:
    """
    Returns the number of tokens in the input text for a given OpenAI model.

    Args:
        text (str): The input string to count tokens for.
        model (str): The name of the OpenAI model (e.g., 'gpt-4', 'gpt-3.5-turbo').

    Returns:
        int: The number of tokens in the input text.
    """
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def append_eval_jsonl(system_message: str, query, ideal, filepath: str):
    """
    Appends a row to a JSONL file for OpenAI evals.

    Parameters:
        system_message (str): The system prompt.
        query (Any): The user query (can be any JSON-serializable type).
        ideal (Any): The expected output (can be any JSON-serializable type).
        filepath (str): The path to the JSONL file.
    """
    entry = {
        "input": {
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": query}
            ]
        },
        "ideal": ideal
    }

    with open(filepath, "a", encoding="utf-8") as f:
        f.write("\n" + json.dumps(entry, ensure_ascii=False))


def normalize_text(text: str) -> str:
    return ''.join(e for e in text.lower() if e.isalnum() or e.isspace()).strip()


def tokenize(text: str) -> set:
    return set(normalize_text(text).split())


def fuzzy_match_score(line: str, tx_repr: str) -> float:
    return SequenceMatcher(None, normalize_text(line), normalize_text(tx_repr)).ratio()


def populate_transaction_alignment_scores(pdf_path: str, transactions: List[Transaction]) -> None:
    with pdfplumber.open(pdf_path) as pdf:
        all_lines = []
        for page in pdf.pages:
            text = page.extract_text(layout=True) or ""
            lines = text.split("\n")
            all_lines.extend([line.strip() for line in lines if line.strip()])

    if not all_lines:
        return

    for txn in transactions:
        tx_repr = f"{txn.date} {txn.note} {txn.amount} {txn.txn_type}"

        best_score = 0.0
        best_line = ""

        for line in all_lines:
            score = fuzzy_match_score(line, tx_repr)
            if score > best_score:
                best_score = score
                best_line = line

        txn.score = round(best_score, 4)
        txn.best_match_line = best_line

def post_validate(field_name: str, result: Any, pdf_path: str) -> None:
    if field_name == "transactions":
        populate_transaction_alignment_scores(pdf_path, result)