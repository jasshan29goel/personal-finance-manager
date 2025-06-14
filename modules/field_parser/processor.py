import os
import json
import openai
from dotenv import load_dotenv
from typing import Dict, Type, List, Callable, Any

from constants import JSONL_EVAL_PATH, OPEN_AI_API_KEY
from domain.transaction import Transaction
from domain.field_parser_config import NOOPProcessorConfig
from domain.field_parser_config import TransactionsProcessorUsingLLMConfig
from modules.field_parser.field_parser_utils import count_tokens, append_eval_jsonl

def do_nothing(config: NOOPProcessorConfig, field_name: str, extracted_content: Any) -> tuple[Any, str]:
    return extracted_content, "Nothing to be done here"


load_dotenv()
client = openai.OpenAI(api_key=os.getenv(OPEN_AI_API_KEY))

SYSTEM_MESSAGE = (
    "You extract structured transaction data from bank or credit card statements. "
    "The data was extracted using pdfplumber. Return a JSON object matching the provided schema. "
    "Do not guess missing or unclear values. Amounts must be greater than zero. "
    "Dates must be in YYYY-MM-DD format"
    "If any field is ambiguous or incomplete reduce the overall confidence accordingly. "
)

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

def process_transactions_using_llm(config: TransactionsProcessorUsingLLMConfig, field_name: str, extracted_content: Any) -> tuple[List[Transaction], str]:
    if field_name != "transactions":
        raise ValueError(f"{config.__class__.__name__} only supports 'transactions' field")

    input_query = str(extracted_content)
    print(input_query)

    response = client.responses.create(
        model=config.model,
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
        confidence = parsed["confidence"]
        llm_message = f"Extracting transactions: {len(transactions)} via LLM. Confidence: {confidence}"
        llm_message += f"\n 📤 Running {config.model} responses api for {count_tokens(input_query)} input tokens"
        llm_message += f"\n 📤 Running {config.model} responses api for {count_tokens(response.output_text)} output tokens"
        
        print(llm_message)
        return transactions, llm_message
    except (KeyError, ValueError, json.JSONDecodeError) as e:
        raise ValueError(f"Failed to parse LLM response: {e}")
    
PROCESSOR_DISPATCH: Dict[Type, Callable] = {
    NOOPProcessorConfig: do_nothing,
    TransactionsProcessorUsingLLMConfig: process_transactions_using_llm,
}

def process_field(config, field_name: str, extracted_content):
    processor = PROCESSOR_DISPATCH[type(config)]
    return processor(config, field_name, extracted_content)
