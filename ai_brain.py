import json
import os
import time
import sqlite3
import gmail_connector # ---> here we intregate our gmail connect to our LLM brain
from dotenv import load_dotenv
from langchain_openrouter import ChatOpenRouter
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

# Load the API key from your .env file
load_dotenv()

print("Initializing Security Protocols (Presidio)...")
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

def mask_sensitive_data(text):
    results = analyzer.analyze(text=text, language='en')
    anonymized_result = anonymizer.anonymize(text=text, analyzer_results=results)
    return anonymized_result.text

def load_mock_emails(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)

# ---> here I can intergrate to model because if my one API gets fails the system can go with second api
def get_ai_model():
    # Primary AI 
    primary_llm = ChatOpenRouter(
        api_key=os.getenv("OPENROUTER_API_KEY_1"),
        model="nvidia/nemotron-3-ultra-550b-a55b:free", 
        temperature=0.0
    )
    # Backup AI (Optional: if you added a second key)
    backup_llm = ChatOpenRouter(
        api_key=os.getenv("OPENROUTER_API_KEY_2", os.getenv("OPENROUTER_API_KEY_1")),
        model="nvidia/nemotron-3-ultra-550b-a55b:free", 
        temperature=0.0
    )
    return primary_llm.with_fallbacks([backup_llm])

def get_rag_database():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

# ---> Initialize the Semantic Cache Database <---
def get_faq_cache():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return Chroma(persist_directory="./faq_cache_db", embedding_function=embeddings)

def categorize_email(email, llm):
    prompt = PromptTemplate(
        input_variables=["email_body", "email_subject"],
        template="""
        Categorize the following email into one of these categories: complaint, inquiry, spam.
        Subject: {email_subject}
        Body: {email_body}
        Respond ONLY with a valid JSON object containing the "category".
        Example: {{"category": "inquiry"}}
        """
    )
    chain = prompt | llm
    response = chain.invoke({"email_subject": email['subject'], "email_body": email['body']})
    try:
        return json.loads(response.content).get("category", "inquiry").lower()
    except:
        return "inquiry"

def generate_reply(email, category, db, llm):
    if category == "spam":
        return "[SYSTEM ACTION: Email ignored and moved to trash.]"
        
    elif category == "complaint":
        prompt = PromptTemplate(
            input_variables=["email_body"],
            template="""You are a helpful support agent. Reply politely to this customer complaint. 
            Apologize for the inconvenience, do not make excuses, and state that a human agent will review this case and reach out shortly. 
            Keep it brief and professional.
            Customer Email: {email_body}"""
        )
        chain = prompt | llm
        return chain.invoke({"email_body": email['body']}).content
        
    elif category == "inquiry":
        docs = db.similarity_search(email['body'], k=2)
        company_knowledge = "\n".join([doc.page_content for doc in docs])
        prompt = PromptTemplate(
            input_variables=["email_body", "knowledge"],
            template="""You are a helpful support agent. Answer the customer's inquiry using ONLY the provided company knowledge below. 
            If the answer is not in the knowledge base, politely say you don't know and a team member will reach out.
            Company Knowledge:
            {knowledge}
            Customer Email: {email_body}
            Draft a polite, professional reply."""
        )
        chain = prompt | llm
        return chain.invoke({"email_body": email['body'], "knowledge": company_knowledge}).content

def evaluate_reply_quality(customer_email, ai_draft, category, db, llm):
    # 1.---> Here we (Fetch the knowledge so the Judge knows the facts) ---
    knowledge_context = "No specific knowledge needed for this category."
    if category == "inquiry":
        docs = db.similarity_search(customer_email, k=2)
        knowledge_context = "\n".join([doc.page_content for doc in docs])
        
    prompt = PromptTemplate(
        input_variables=["customer_email", "ai_draft", "knowledge"],
        template="""You are a QA Agent evaluating an AI-drafted email. 
        
        Company Knowledge Base (Facts):
        {knowledge}
        
        Customer Email: {customer_email}
        AI Drafted Reply: {ai_draft}
        
        Rules for Evaluation:
        1. The tone must be professional.
        2. It must address the customer's core issue.
        3. NO HALLUCINATIONS: Any prices, features, or policies mentioned MUST exist in the Company Knowledge Base above. 
        If the email requires no facts (like a simple apology), just ensure it is polite.
        
        Output strictly the word PASS if it meets all criteria, or FAIL if it violates any.
        """
    )
    chain = prompt | llm
    try:
        result = chain.invoke({
            "customer_email": customer_email, 
            "ai_draft": ai_draft, 
            "knowledge": knowledge_context
        })
        decision = result.content.strip().upper()
        if "PASS" in decision:
            return "PASS"
        else:
            return "FAIL"
    except Exception as e:
        print(f"\n[SYSTEM WARNING] QA LLM API Failed: {e}")
        return "FAIL - API ERROR"

def setup_analytics_db():
    conn = sqlite3.connect('email_analytics.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS email_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            category TEXT,
            qa_status TEXT,
            processing_time REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    return conn

def log_email_metrics(conn, sender, category, qa_status, start_time):
    processing_time = time.time() - start_time
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO email_logs (sender, category, qa_status, processing_time)
        VALUES (?, ?, ?, ?)
    ''', (sender, category, qa_status, processing_time))
    conn.commit()

if __name__ == "__main__":
    print("Initializing AI, Knowledge Base, and Cache...\n")
    llm = get_ai_model()
    db = get_rag_database()
    cache_db = get_faq_cache() 
    analytics_conn = setup_analytics_db()
    
    # --- THE SEAMLESS INTEGRATION ---
    gmail_service = gmail_connector.authenticate_gmail()
    
    if gmail_service:
        print("📥 Fetching live unread emails from Gmail...")
        inbox_data = gmail_connector.fetch_unread_emails(gmail_service)
    else:
        print("📂 No Gmail credentials found. Falling back to test_emails.json...\n")
        inbox_data = load_mock_emails('test_emails.json')
    
    for email in inbox_data:
        start_time = time.time() 
        
        print(f"{'='*50}")
        print(f"NEW EMAIL FROM: {email['sender']}")
        print(f"SUBJECT: {email['subject']}\n")
        
        original_body = email['body']
        safe_body = mask_sensitive_data(original_body)
        email['body'] = safe_body 
        
        category = categorize_email(email, llm)
        print(f"AI CATEGORIZED AS: {category.upper()}")
        
        qa_result = "N/A" 
        
        if category == "inquiry":
            cache_results = cache_db.similarity_search_with_score(safe_body, k=1)
            
            if cache_results and cache_results[0][1] < 0.5:
                print("\n⚡ [CACHE HIT] Found similar previous question! Bypassing LLM...")
                reply = cache_results[0][0].metadata['cached_reply']
                print("\n--- CACHED REPLY ---")
                print(reply)
                print(f"\nQA STATUS: ✅ PASS - Served instantly from cache.")
                
                log_email_metrics(analytics_conn, email['sender'], category, "PASS", start_time)
                print(f"📊 [DATABASE] Email logged to analytics.")
                print(f"{'='*50}\n")
                continue 
        
        print("\n--- AI DRAFTED REPLY ---")
        reply = generate_reply(email, category, db, llm)
        print(reply)
        
        if category != "spam":
            print("\n--- RUNNING QUALITY ASSURANCE ---")
            qa_result = evaluate_reply_quality(safe_body, reply, category, db, llm)
            
            if qa_result == "PASS":
                print(f"QA STATUS: ✅ {qa_result} - Draft approved. Ready for Human-in-the-Loop review.")
                
                if category == "inquiry":
                    cache_db.add_texts(texts=[safe_body], metadatas=[{"cached_reply": reply}])
                    print("💾 [CACHE SAVED] New verified answer added to cache.")
                
                # --- NEW: Save Live Draft if connected to Gmail ---
                if gmail_service:
                    gmail_connector.create_draft(gmail_service, email['sender'], email['subject'], reply)
                    
            else:
                print(f"QA STATUS: ❌ {qa_result} - Draft flagged. Requires immediate human intervention.")
                
        qa_status_simple = "PASS" if qa_result == "PASS" else "FAIL"
        if category == "spam":
            qa_status_simple = "IGNORED"
            
        log_email_metrics(analytics_conn, email['sender'], category, qa_status_simple, start_time)
        print(f"📊 [DATABASE] Email logged to analytics.")
        print(f"{'='*50}\n")