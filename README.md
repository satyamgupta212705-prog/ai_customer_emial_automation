# 🚀 Enterprise AI Email Automation System

A smart, autonomous AI assistant that acts as a customer support agent. It reads incoming emails, hides sensitive customer data, searches company documents for the right answers, and drafts highly accurate replies for human review. 

If it notices a question it has already answered before, it instantly remembers the answer to save time and API costs!

## 🧠 How It Works (The Workflow)
When a customer sends an email, the system follows this exact process:
1. **Fetch:** Connects to the inbox and reads unread emails.
2. **Protect:** Scans the email and masks private data (like credit card numbers) so it is never shared with external AI servers.
3. **Categorize:** The AI decides if the email is a `Complaint`, `Inquiry`, or `Spam`. (Spam is ignored).
4. **Draft (RAG):** If it's a valid email, the AI searches a local database of company FAQs to write a 100% factual reply.
5. **Quality Check (LLM-as-a-Judge):** A second AI reads the drafted reply to ensure it is polite, accurate, and doesn't hallucinate. 
6. **Save:** The approved draft is saved to the inbox for a human to hit "Send," and the system logs its performance to a beautiful web dashboard.

## 🌟 Key Features Explained Simply
* **Smart Memory (Semantic Caching):** The AI remembers previously approved answers. If a new customer asks a similar question, it serves the cached answer instantly instead of thinking from scratch.
* **Data Privacy (Microsoft Presidio):** Enterprise-grade security that redacts sensitive PII (Personally Identifiable Information) before the AI even reads the email.
* **Failsafe System:** If the live Gmail connection breaks or credentials are missing, the system doesn't crash. It safely switches to a "Dummy Data" mode using local test files so developers can keep working.
* **Manager Dashboard:** A live web app showing metrics like "Total Emails Processed," "Average Response Time," and "Pass/Fail Rates."

## 🛠️ Tech Stack
* **Language:** Python 3.12
* **AI Engine:** LangChain, OpenRouter (Nemotron-3-ultra-550b)
* **Memory & Database:** ChromaDB (Vector Search), SQLite (Analytics), HuggingFace Embeddings
* **Security Layer:** Microsoft Presidio, spaCy
* **Web Dashboard:** Streamlit
* **Live Connection:** Google Cloud Gmail API

---

