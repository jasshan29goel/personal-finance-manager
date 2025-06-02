import json
from typing import List
from domain.transaction import Transaction
from domain.parsed_email import ParsedEmail  # Assuming you defined ParsedEmail in a domain module
from pprint import pprint
from difflib import SequenceMatcher


def validate_parsed_emails(expected_json_path: str, generated_parsed_emails: List[ParsedEmail]):
    with open(expected_json_path, 'r') as f:
        expected_data = json.load(f)

    mismatches = validate_generated_vs_expected(generated_parsed_emails, expected_data)
    return mismatches


def validate_generated_vs_expected(generated_data: List[ParsedEmail], expected_data: List[dict]):
    mismatches = []

    expected_by_id = {item["message_id"]: item for item in expected_data}

    for generated in generated_data:
        message_id = generated.message_id
        expected = expected_by_id.get(message_id)

        if not expected:
            mismatches.append({
                "message_id": message_id,
                "error": "Missing expected response"
            })
            continue

        expected_transactions = expected.get("transactions", [])
        generated_transactions = generated.transactions or []

        tx_mismatches = compare_transactions(expected_transactions, generated_transactions)

        if tx_mismatches:
            mismatches.append({
                "account_id": generated.account_id,
                "email_date": generated.email_date,
                "mismatches": tx_mismatches
            })

    return mismatches


def compare_transactions(expected: List[dict], generated: List[Transaction], note_similarity_threshold: float = 0.8):
    def sort_key(tx):
        return (tx["date"], tx["amount"], tx["note"], tx["txn_type"])

    expected_sorted = sorted(expected, key=sort_key)
    generated_sorted = sorted([tx.dict() for tx in generated], key=sort_key)

    mismatches = []
    if len(expected_sorted) != len(generated_sorted):
        mismatches.append(f"Transaction count mismatch. Expected {len(expected_sorted)}, got {len(generated_sorted)}")
        return mismatches

    for i, (e_tx, g_tx) in enumerate(zip(expected_sorted, generated_sorted)):
        tx_context = f"(generated: date={g_tx['date']}, amount={g_tx['amount']}, type={g_tx['txn_type']}, note='{g_tx['note']}')"

        for field in ["date", "amount", "txn_type"]:
            if e_tx[field] != g_tx[field]:
                mismatches.append(
                    f"Mismatch at index {i} on '{field}' → expected '{e_tx[field]}', got '{g_tx[field]}' {tx_context}"
                )

        # Fuzzy note comparison
        e_note = e_tx.get("note", "").strip().lower()
        g_note = g_tx.get("note", "").strip().lower()

        if e_note and g_note:
            similarity = SequenceMatcher(None, e_note, g_note).ratio()
            if similarity < note_similarity_threshold:
                mismatches.append(
                    f"Mismatch at index {i}: note similarity {similarity:.2f} below threshold → "
                    f"expected '{e_note}', got '{g_note}' {tx_context}"
                )
        elif e_note != g_note:
            mismatches.append(
                f"Mismatch at index {i}: note presence → expected '{e_note}', got '{g_note}' {tx_context}"
            )

    return mismatches
