import os
import json
from typing import Any, List

import openai
from dotenv import load_dotenv
from domain.transaction import Transaction
from domain.field_parser_config import ProcessorConfig, NOOPProcessorConfig, LLMProcessorConfig
from utils import count_tokens, append_eval_jsonl
from datetime import datetime

load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPEN_AI_API_KEY"))

JSONL_EVAL_PATH = "evals/current.jsonl"



today_str = datetime.now().strftime("%Y-%m-%d")

SYSTEM_MESSAGE = (
    "You extract structured transaction data from bank or credit card statements. "
    "The data was extracted using pdfplumber. Return a JSON object matching the provided schema. "
    "Do not guess missing or unclear values. Amounts must be greater than zero. "
    "Dates must be in YYYY-MM-DD format and must not be in the future. "
    "If any field is ambiguous or incomplete, exclude the transaction and reduce the overall confidence accordingly. "
    "Assume today's date is {today}."
).format(today=today_str)

TRANSACTION_SCHEMA = {
    "type": "object",
    "required": ["transactions", "confidence"],
    "properties": {
        "transactions": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "date",
                    "amount",
                    "txn_type",
                    "note",
                    "reason"
                ],
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
                    "reason": {
                        "type": "string",
                        "description": "For the given output explain why you choose the given amount date note and transaction type."
                    },
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

def process_field(field_name: str, chunk: Any, processor_config: ProcessorConfig) -> Any:
    if field_name == "transactions":
        return _process_transactions(chunk, processor_config)
    else:
        raise ValueError(f"Unsupported field: {field_name}")

def _process_transactions(chunk: Any, processor_config: ProcessorConfig) -> tuple[List[Transaction], float]:
    if isinstance(processor_config, NOOPProcessorConfig):
        return [], 0 # nothing to do.
    
    if isinstance(processor_config, LLMProcessorConfig):

        input_query = str(chunk)
        
        print(f"📤 Running {processor_config.model} responses api for {count_tokens(input_query)} tokens")
        print(input_query)

        response = client.responses.create(
            model=processor_config.model,
            input=[
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": SYSTEM_MESSAGE}]
                },
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": input_query}]
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
            temperature=0.01,
            max_output_tokens=16384,
            top_p=1,
            store=True
        )

        try:
            parsed = json.loads(response.output_text)
            append_eval_jsonl(SYSTEM_MESSAGE, input_query, response.output_text, JSONL_EVAL_PATH)
            transactions =  [
                Transaction(
                    date=txn["date"],
                    amount=txn["amount"],
                    note=txn["note"],
                    txn_type=txn["txn_type"],
                    reason=txn["reason"],
                    category="MISC"
                )
                for txn in parsed["transactions"]
            ]
            return transactions, parsed["confidence"]
        except (KeyError, ValueError, json.JSONDecodeError) as e:
            raise ValueError(f"Failed to parse LLM response: {e}")
    
    raise ValueError(f"Unsupported processor for transactions: {processor_config.type}")
