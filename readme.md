Certainly! Based on the information available from the GitHub repository , here's a comprehensive README for the **Personal Finance Manager** project:

---

# Personal Finance Manager

**Personal Finance Manager** is a Python-based tool designed to automate the extraction of financial data from your Gmail account and organize it into structured Google Sheets. This facilitates efficient personal finance tracking by consolidating transaction details from various sources into a single, manageable spreadsheet.

---

## ✨ Features

* **Automated Gmail Parsing**: Connects to your Gmail account to scan and parse financial statements.
* **Structured Data Output**: Extracted data is organized and pushed to Google Sheets for easy analysis.
* **Modular Architecture**: Well-structured codebase with separate modules for configuration, domain logic, state management, and utilities.
* **Customizable**: Designed for personal use, allowing customization to fit individual financial tracking needs.

---

## 🛠️ Setup Instructions

### Step 1: Clone the Repository

```bash
git clone https://github.com/jasshan29goel/personal-finance-manager.git
cd personal-finance-manager
```



### Step 2: Create a Google Cloud Project and Configure OAuth 2.0 Client

1. Go to the [Google Cloud Console](https://console.cloud.google.com/) and create a new project.
2. Enable the Gmail API for your project:

   * Navigate to **APIs & Services > Library**.
   * Search for "Gmail API" and enable it.
3. Configure OAuth consent screen:

   * Go to **APIs & Services > OAuth consent screen**.
   * Choose "External" and fill in the required details.
   * Add your email as a test user.
4. Create OAuth 2.0 credentials:

   * Navigate to **APIs & Services > Credentials**.
   * Click on "Create Credentials" and select "OAuth client ID".
   * Choose "Desktop app" as the application type.
   * Download the `credentials.json` file and place it in the root directory of the cloned repository.

### Step 3: Install Dependencies

Ensure you have Python installed. Then, install the required libraries:

```bash
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```



*Note: Additional dependencies may be required based on the modules used. Please refer to the code for any other necessary installations.*

### Step 4: Run the Application

Execute the main script to start the process:

```bash
python3 main.py
```



Upon first run, a browser window will prompt you to authorize access to your Gmail and Google Sheets.

---

## 📁 Project Structure

```plaintext
personal-finance-manager/
├── config/         # Configuration files and settings
├── domain/         # Core business logic and domain models
├── modules/        # Modular components for different functionalities
├── state/          # State management and persistence
├── utils.py        # Utility functions
├── main.py         # Entry point of the application
└── README.md       # Project documentation
```



---

## ✅ Prerequisites

* Python 3.x
* Google Account with Gmail access
* Google Cloud Project with Gmail API enabled
* Google Sheets API enabled (if writing to Sheets is implemented)([Opensource.com][1])

---

## 📌 Notes

* This tool is intended for personal use. Ensure that you comply with Google's API usage policies.
* Handle your credentials securely. Do not share your `credentials.json` file.
* Regularly review and clean up any sensitive data stored in your Google Sheets.

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).([GitHub][2])

---

## 🙏 Acknowledgements

Developed by [jasshan29goel](https://github.com/jasshan29goel).

---

*For any issues or contributions, please open an issue or submit a pull request on the [GitHub repository](https://github.com/jasshan29goel/personal-finance-manager).*

---
