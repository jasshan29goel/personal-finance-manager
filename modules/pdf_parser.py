from domain.transaction import Transaction
from domain.parsed_pdf import ParsedPDF
import pdfplumber

def extract_transactions_from_pdf(pdf_path: str, delete_after=True) -> ParsedPDF:
    print(f"🔍 Parsing PDF: {pdf_path}")
    transactions = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                if not table or len(table) < 2:
                    continue
                headers = table[0]
                for row in table[1:]:
                    # Very basic mapping: expects first three cols to be date, amount, note
                    if len(row) >= 3:
                        date, amount, note = row[0], row[1], row[2]
                        transactions.append(Transaction(date, amount, note))

    if delete_after:
        import os
        os.remove(pdf_path)

    return ParsedPDF(transactions=transactions)
