import os
import base64
import pikepdf
import pdfplumber
from domain.matched_email import MatchedEmail
from modules.password_lookup import get_pdf_password

OUTPUT_DIR = 'output_pdfs'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_pdf_attachments(service, matched_emails: list[MatchedEmail]):
    saved_files = []

    for email_obj in matched_emails:
        message = email_obj.message
        account_id = email_obj.account.id
        parts = message.get('payload', {}).get('parts', [])

        for part in parts:
            if part.get('filename', '').lower().endswith('.pdf'):
                attachment_id = part['body'].get('attachmentId')
                if not attachment_id:
                    continue

                # Download the PDF directly (unlocked only)
                att = service.users().messages().attachments().get(
                    userId='me',
                    messageId=message['id'],
                    id=attachment_id
                ).execute()

                data = base64.urlsafe_b64decode(att['data'].encode('UTF-8'))

                # Create unlocked filename
                filename = email_obj.get_filename_prefix() + ".pdf"
                unlocked_path = os.path.join(OUTPUT_DIR, filename)
                password = get_pdf_password(account_id)

                try:
                    # Decrypt in memory, save only if successful
                    with open("temp.pdf", "wb") as temp:
                        temp.write(data)

                    with pikepdf.open("temp.pdf", password=password) as pdf:
                        pdf.save(unlocked_path)
                        saved_files.append(unlocked_path)
                        print(f"✅ Unlocked PDF: {unlocked_path}")
                    os.remove("temp.pdf")
                except Exception as e:
                    print(f"❌ Failed to unlock PDF for {account_id}: {e}")
                    if os.path.exists("temp.pdf"):
                        os.remove("temp.pdf")

    return saved_files
