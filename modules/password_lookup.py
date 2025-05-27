import json

PDF_PASSWORDS_PATH = 'creds/pdf_passwords.json'

def load_passwords():
    with open(PDF_PASSWORDS_PATH, 'r') as f:
        return json.load(f)

def get_pdf_password(account_name):
    passwords = load_passwords()
    return passwords.get(account_name)
