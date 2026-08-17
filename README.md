# Enterprise AI Email Automation System

A smart, autonomous AI assistant that acts as a customer support agent. It reads incoming emails, hides sensitive customer data, searches company documents for the right answers, and drafts accurate replies for human review.

If it notices a question it has already answered before, it instantly remembers the answer to save time and API costs.

## How It Works

When a customer sends an email, the system follows this process:

1. **Fetch:** Connects to the inbox and reads unread emails.
2. **Protect:** Scans the email and masks private data, such as credit card numbers, so it is never shared with external AI servers.
3. **Categorize:** The AI decides if the email is a `Complaint`, `Inquiry`, or `Spam`. Spam is ignored.
4. **Draft (RAG):** If it is a valid email, the AI searches a local database of company FAQs to write a factual reply.
5. **Quality Check:** A second AI reads the drafted reply to ensure it is polite, accurate, and does not hallucinate.
6. **Save:** The approved draft is saved to the inbox for a human to send, and the system logs performance to a web dashboard.

## Key Features

* **Smart Memory (Semantic Caching):** Remembers previously approved answers. If a new customer asks a similar question, it serves the cached answer instantly.
* **Data Privacy (Microsoft Presidio):** Redacts sensitive PII before the AI reads the email.
* **Failsafe System:** If the live Gmail connection breaks or credentials are missing, the system switches to dummy data mode using local test files.
* **Manager Dashboard:** A Streamlit dashboard showing metrics like total emails processed, average response time, and pass/fail rates.

## Tech Stack

* **Language:** Python 3.12
* **AI Engine:** LangChain, OpenRouter
* **Memory and Database:** ChromaDB, SQLite, HuggingFace Embeddings
* **Security Layer:** Microsoft Presidio, spaCy
* **Web Dashboard:** Streamlit
* **Live Connection:** Google Cloud Gmail API
