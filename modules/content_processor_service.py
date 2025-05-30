import os
import json
from typing import Any, List

import openai
from dotenv import load_dotenv
from domain.transaction import Transaction
from utils import count_tokens

load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPEN_AI_API_KEY"))

MODEL = "gpt-4.1-nano"

SYSTEM_MESSAGE = (
    "You are helping extract structured transaction data from bank or credit card statements. "
    "The data below is extracted using pdfplumber. Your task is to return a JSON object containing "
    "a list of transactions. Modify confidence of output as you see fit, "
    "with 1 being 100 percent accurate and 0 being 0 percent accurate"
)

TRANSACTION_SCHEMA = {
    "type": "object",
    "required": ["transactions", "confidence"],
    "properties": {
        "transactions": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["date", "amount", "txn_type", "note", "confidence"],
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "Transaction date in YYYY-MM-DD format"
                    },
                    "note": {
                        "type": "string",
                        "description": "Narration or description of the transaction"
                    },
                    "amount": {
                        "type": "number",
                        "minimum": 0,
                        "description": "Transaction amount"
                    },
                    "txn_type": {
                        "type": "string",
                        "enum": ["CREDIT", "DEBIT"],
                        "description": "Type of transaction: CREDIT or DEBIT"
                    },
                    "confidence": {
                        "type": "number",
                        "description": "value from 0 - 1 to indicate your confidence in the parsing of the given transaction and its accuracy."
                    }
                },
                "additionalProperties": False
            }
        },
        "confidence": {
            "type": "number",
            "description": "value from 0 - 1 to indicate your confidence in the parsing of the entire query and its accuracy."
        }
    },
    "additionalProperties": False
}

def process_field(field_name: str, chunk: Any, processor_id: str) -> Any:
    if field_name == "transactions":
        return _process_transactions(chunk, processor_id)
    else:
        raise ValueError(f"Unsupported field: {field_name}")

def _process_transactions(chunk: Any, processor_id: str) -> tuple[List[Transaction], float]:
    if not processor_id.startswith("llm:"):
        raise ValueError(f"Unsupported processor for transactions: {processor_id}")

    query = str(chunk)
    print(f"📤 Running {MODEL} responses api for {count_tokens(query)} tokens")

    response = client.responses.create(
        model=MODEL,
        input=[
            {
                "role": "system",
                "content": [{"type": "input_text", "text": SYSTEM_MESSAGE}]
            },
            {
                "role": "user",
                "content": [{"type": "input_text", "text": query}]
            }
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "transaction_response",
                "schema": TRANSACTION_SCHEMA,
                "strict": True
            }
        },
        reasoning={},
        tools=[],
        temperature=0,
        max_output_tokens=32768,
        top_p=1,
        store=True
    )

    try:
        parsed = json.loads(response.output_text)
        transactions =  [
            Transaction(
                date=txn["date"],
                amount=txn["amount"],
                note=txn["note"],
                txn_type=txn["txn_type"],
                confidence=txn["confidence"]
            )
            for txn in parsed["transactions"]
        ]
        return transactions, parsed["confidence"]
    except (KeyError, ValueError, json.JSONDecodeError) as e:
        raise ValueError(f"Failed to parse LLM response: {e}")
