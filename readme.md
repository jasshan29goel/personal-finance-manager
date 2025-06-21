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

### Step 2: Create a virtual environment and install dependencies. 

```bash
# For macOS/Linux
python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

*Note: Additional dependencies may be required based on the modules used. Please refer to the code for any other necessary installations.*

### Step 3: Setting up the required credentials.

For the script to work, it needs to have access to your gmail account, so that it can read emails.
It also needs access to a sheet in so that it can output the results on to google sheets.
You would also need access to OPEN AI API key.

Generate the respective credential.json and service_account.json and put them inside a folder named creds in the root directory.
Also put the pdf_passwords based on your account config id inside the creds folder.

Also finall make a .env file in the root directory and paste code like this 
```bash
OPEN_AI_API_KEY=YOUR_API_KEY
```


### Step 3: Configure the email_configs.json for setting the the email parameters which you would like to filter.


The `email_configs.json` file defines how emails from different sources should be processed. Place this file in the `config/` folder.

#### 📄 Sample Structure

```json
[
  {
    "id": "hdfc-bank",
    "from_addresses": ["hdfcbanksmartstatement@hdfcbank.net"],
    "subject_keywords": ["HDFC Bank Combined Email Statement"],
    "field_parsers": {
      "transactions": {
        "type": "llm",
        "model": "gpt-4",
        "format": "json"
      }
    },
    "run": true
  }
]
```

#### 🔑 Key Fields

- `id`: A unique identifier for this config
- `from_addresses`: List of sender email addresses to match
- `subject_keywords`: Keywords to look for in the email subject
- `field_parsers`: Specifies how each field (e.g., `transactions`) should be extracted
- `run`: Set to `true` to activate this config

You can add multiple configs for different banks or cards in the same file.


### Step 4: Set up your target excel sheet as below.

📊 [View Sample Google Sheet](https://docs.google.com/spreadsheets/d/e/2PACX-1vRtUH5drGXeyIsZjODzRw-5PxbXPLk4ZekcKsxclbt3h_QJUUAGufblphvBPcbdVajFJm7wWSUfIDDr/pubhtml)

Sample file is also available in the github repo.
Replace the needed value in constants.json

### Step 5: Run the Application

Execute the main script to start the process:
In main.py setup your MONTH and YEAR and you are good to go.

```bash
python3 main.py
```



Upon first run, a browser window will prompt you to authorize access to your Gmail and Google Sheets.

---

## 🔐 Credential Configuration Guide

This project needs two types of credentials:

1. `credentials.json` – for accessing Gmail using OAuth (user-based authentication)
2. `service_account.json` – for accessing Google Sheets via a service account

---

### 📩 1. Creating `credentials.json` for Gmail API Access

> This is required to read emails from your Gmail account.

#### Steps:

1. Visit the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project, or choose an existing one
3. **Enable the Gmail API**:
   - Go to **APIs & Services > Library**
   - Search for **Gmail API**, then click **Enable**
4. **Generate OAuth credentials**:
   - Navigate to **APIs & Services > Credentials**
   - Click **Create Credentials > OAuth client ID**
   - Select **Desktop App** as the application type
   - Enter a name (e.g., `Gmail Desktop Client`) and click **Create**
   - Download the resulting JSON file
5. Rename and move the file to:
   ```bash
   creds/credentials.json
   ```

> 📝 On the first run, you will be prompted to authenticate in the browser. A `token.json` will be created automatically after successful authorization.

---

### 📊 2. Creating `service_account.json` for Google Sheets Access

> This is needed for writing data to Google Sheets without user interaction.

#### Steps:

1. In the same Google Cloud project, go to **APIs & Services > Library**
2. Search for and enable the **Google Sheets API**
3. Go to **APIs & Services > Credentials**
4. Click **Create Credentials > Service Account**
5. Enter a name and description (e.g., `Sheets Writer`) and click **Create and Continue**
6. (Optional) Skip role assignment for now by clicking **Done**
7. Click on the newly created service account
8. Open the **Keys** tab:
   - Click **Add Key > Create new key**
   - Select **JSON** format and click **Create**
   - Save the downloaded file
9. Rename and place the file in:
   ```bash
   creds/service_account.json
   ```

---

### 📋 Share Access to Your Google Sheet

Share your Google Sheet with the service account's email address (found in the downloaded `service_account.json` file). It should look like this:

```
your-service-account@your-project.iam.gserviceaccount.com
```

Grant **Editor** access to allow data writing.

---


## 📁 Project Structure

```plaintext
personal-finance-manager/
├── config/         # Configuration files and settings
├── domain/         # Core business logic and domain models
├── modules/        # Modular components for different functionalities
├── utils.py        # Utility functions
├── main.py         # Entry point of the application
└── README.md       # Project documentation
```

---

 ## 💰 Estimated Cost (OpenAI API)

Here’s a rough estimate based on actual usage during testing:

- **500 API requests**
- **500K input tokens**
- **Total spent:** $0.69
- **Model used:** `gpt-4-1-mini`

Each API request corresponds to one **PDF page** of transactions.

### 📅 Yearly Cost Estimate

Assuming ~100 PDF pages per month:

- **100 pages/month × 12 months = 1,200 requests/year**
- Approximate annual cost: **~$1.65/year**

> ⚠️ Costs may vary slightly depending on token count per page and model used.

---

## Future plans

* Obfuscate data being sent to LLMs to minimze personal infromation going over the internet.
* Add a better way for providing date range for email filter. 
* Add more fields to extracts like mutual fund transactions if possible. 
* Add a variety of text extractors and processors to improve validation.

## ✅ Prerequisites

* Python 3.x
* Google Account with Gmail access
* Google Cloud Project with Gmail API enabled
* Google Sheets API enabled (if writing to Sheets is implemented)([Opensource.com][1])

---

## Sample gif and screenshots

### 📊 Sample Dashboard Output
![Dashboard](samples/sample%20end%20dashboard.png)

### 📬 Email Execution Status
![Email Execution](samples/sample%20email%20execution%20status.png)

### 🛑 Script Completion
![Script End](samples/Sample%20script%20end%20screenhot.png)

### 📈 Run Status Output
![Run Status](samples/Sample%20run%20status.png)

### ▶️ Script in Action
![Script Run](samples/sample%20script%20run.gif)

📥 [Download Sample Excel Output](samples/Sample%20of%20personal-finance-manager.xlsx)


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
