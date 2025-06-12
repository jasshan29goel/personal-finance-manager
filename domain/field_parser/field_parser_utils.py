import pdfplumber
from typing import List
from difflib import SequenceMatcher
from domain.transaction import Transaction

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
