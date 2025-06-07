from typing import List, Any
from domain.email import Email
from domain.parsed_email import ParsedEmail
from modules.attachment_service import save_unlocked_attachment_pdf
from utils import write_strings_to_file

def parse_emails(emails: List[Email], gmail_service: Any) -> List[ParsedEmail]:
    parsed_emails: List[ParsedEmail] = []

    for email in sorted(emails):
        try:
            field_outputs = {}
            script_message = ""
            for field_name, field_config in email.config.field_parsers.items():
                # Step 1: Get the input text/table
                if field_config.type == "pdf_attachment":
                    pdf_path = save_unlocked_attachment_pdf(email, gmail_service) 
                    extracted_content = field_config.pdf_extractor.extract_from_pdf(pdf_path=pdf_path)
                else:
                    raise ValueError(f"Unsupported source: {field_config.type}")

                # Step 2: Process the extracted content
                # print(str(extracted_content))
                # write_strings_to_file(extracted_content, 'output.txt')
                result, message = field_config.processor.process_field(field_name=field_name, extracted_content=extracted_content)
                field_outputs[field_name] = result
                script_message += f"\n field: {field_name} message: {message}"

            parsed_emails.append(
                ParsedEmail(
                    message_id=email.get_message_id(),
                    email_date=email.get_email_date(),
                    account_id=email.config.id,
                    **field_outputs,
                    status="success",
                    script_message=script_message
                )
            )

        except Exception as e:
            parsed_emails.append(
                ParsedEmail(
                    message_id=email.get_message_id(),
                    email_date=email.get_email_date(),
                    account_id=email.config.id,
                    status="failed",
                    script_message=str(e)
                )
            )

    return parsed_emails
