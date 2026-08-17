# Enterprise AI Customer Email Automation System

This project is an AI-powered customer support assistant. It reads customer emails, protects sensitive information, understands the email type, searches company FAQ data, drafts a professional reply, checks the reply quality, and saves useful performance data for a dashboard.

The goal is not to send emails automatically without control. The system prepares high-quality draft replies so a human team member can review and send them safely.

## What This Project Does

The system helps customer support teams handle emails faster and more consistently.

It can:

* Read unread emails from Gmail.
* Use local test emails when Gmail credentials are not available.
* Hide sensitive customer information before sending text to an AI model.
* Classify emails as `inquiry`, `complaint`, or `spam`.
* Search company FAQ content using RAG.
* Generate polite and professional email replies.
* Run a quality check on the AI-generated reply.
* Save approved answers in a semantic cache for faster future replies.
* Create Gmail drafts for human review.
* Store analytics in SQLite.
* Show email performance metrics in a Streamlit dashboard.

## How It Works

The email automation pipeline follows these steps:

1. **Fetch emails**
   The system tries to connect to Gmail and read unread emails. If Gmail credentials are missing, it uses `test_emails.json` instead.

2. **Protect customer data**
   Microsoft Presidio scans the email body and masks sensitive information such as personal details before the AI model processes it.

3. **Classify the email**
   The AI model categorizes the email as:

   * `inquiry` for normal customer questions.
   * `complaint` for negative feedback or support issues.
   * `spam` for unwanted messages.

4. **Generate a reply**
   For inquiries, the system searches the local FAQ knowledge base and writes a reply using only that information. For complaints, it creates a polite acknowledgement and informs the customer that a human will review the issue.

5. **Check reply quality**
   A second AI prompt reviews the draft reply. It checks that the tone is professional, the answer addresses the customer issue, and no unsupported facts are added.

6. **Save useful results**
   If the reply passes quality checks, the system can save it as a Gmail draft and store similar verified replies in a semantic cache.

7. **Track analytics**
   Each processed email is logged in `email_analytics.db`, including category, QA status, processing time, and timestamp.

## Project Structure

```text
.
|-- ai_brain.py          # Main AI email processing pipeline
|-- build_database.py    # Builds the ChromaDB vector database from company_faq.txt
|-- dashboard.py         # Streamlit dashboard for analytics
|-- gmail_connector.py   # Gmail authentication, email fetching, and draft creation
|-- company_faq.txt      # Company FAQ knowledge used for RAG
|-- test_emails.json     # Local test emails used when Gmail is not connected
|-- requirements.txt     # Python dependencies
|-- .gitignore           # Files and folders excluded from GitHub
`-- README.md            # Project documentation
```

## Tech Stack

* **Python 3.12** for the main application.
* **LangChain** for prompt chains and AI workflow.
* **OpenRouter** for LLM access.
* **ChromaDB** for vector search and semantic cache.
* **HuggingFace Embeddings** for converting FAQ text into searchable vectors.
* **Microsoft Presidio** for sensitive data detection and anonymization.
* **SQLite** for analytics logging.
* **Streamlit** for the dashboard.
* **Gmail API** for live email reading and draft creation.

## Setup Instructions

### 1. Create and activate a virtual environment

```powershell
python -m venv email
.\email\Scripts\activate
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Install the spaCy English model

Microsoft Presidio requires an NLP model.

```powershell
python -m spacy download en_core_web_lg
```

If the large model is too heavy for your system, you can use:

```powershell
python -m spacy download en_core_web_sm
```

### 4. Create a `.env` file

Create a `.env` file in the project root and add your OpenRouter API key:

```env
OPENROUTER_API_KEY_1=your_openrouter_api_key_here
OPENROUTER_API_KEY_2=your_optional_backup_key_here
```

`OPENROUTER_API_KEY_2` is optional. If it is not provided, the system uses the first key as the fallback.

## Gmail Setup

Live Gmail connection is optional.

To enable Gmail:

1. Create a project in Google Cloud Console.
2. Enable the Gmail API.
3. Create OAuth client credentials for a desktop app.
4. Download the credentials file.
5. Rename it to `credentials.json`.
6. Place it in the project root.

When you run the app for the first time, Google will ask you to sign in. After successful login, a `token.json` file is created automatically.

Important: `credentials.json`, `token.json`, and `.env` are ignored by Git and should not be uploaded to GitHub.

## How To Run

### Step 1: Build the FAQ vector database

Run this whenever you create or update `company_faq.txt`.

```powershell
python build_database.py
```

This creates a local `chroma_db` folder.

### Step 2: Process emails

```powershell
python ai_brain.py
```

If Gmail is connected, the system reads unread Gmail messages. If Gmail is not connected, it uses `test_emails.json`.

### Step 3: Open the analytics dashboard

```powershell
streamlit run dashboard.py
```

The dashboard shows:

* Total emails processed.
* QA pass rate.
* Average processing time.
* Emails by category.
* QA status distribution.
* Raw email processing logs.

## Data and Generated Files

The project creates some local files while running:

* `chroma_db/` stores the FAQ vector database.
* `faq_cache_db/` stores verified cached answers.
* `email_analytics.db` stores dashboard analytics.
* `token.json` stores Gmail login tokens.

These files are intentionally ignored by Git because they are local, generated, or sensitive.

## Safety Features

This project includes multiple safety layers:

* Sensitive information is masked before AI processing.
* Replies are drafted for human review instead of being sent automatically.
* Inquiry replies are based on the company FAQ knowledge base.
* A quality-check prompt reviews replies before they are approved.
* Spam emails are ignored.
* Gmail credentials are optional, so the project can still run in test mode.

## Example Use Case

A customer asks a question about company pricing, refund policy, or services. The system searches `company_faq.txt`, drafts a reply using the matching information, checks the reply for quality, saves the result, and logs the processing data for the dashboard.

If a similar question appears again later, the semantic cache can reuse the previous approved answer, making the response faster and reducing API usage.

## Current Status

This is a working AI email automation prototype. It is suitable for local testing, demos, and further development. Before using it in production, add stronger error handling, access controls, monitoring, and a manual review workflow that matches your business process.
