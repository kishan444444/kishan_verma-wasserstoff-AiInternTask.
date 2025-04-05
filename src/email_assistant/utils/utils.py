import sys
import os
import base64
import sqlite3
import requests
import json
from googleapiclient.discovery import build
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from src.email_assistant.logger import logging
from src.email_assistant.exception import customexception
import os
from dotenv import load_dotenv
load_dotenv()



GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")
GOOGLE_SEARCH_API_KEY = "your_google_search_api_key"
GOOGLE_SEARCH_CX = "your_custom_search_engine_id"

llm = ChatGroq(groq_api_key=GROQ_API_KEY, model="Gemma2-9b-It")

class utils():
    def __init__(self):
        pass


    # ==== SLACK ====
    def send_slack_notification(self,message):
        try:
            url = "https://slack.com/api/chat.postMessage"
            headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}", "Content-Type": "application/json"}
            payload = {"channel": SLACK_CHANNEL_ID, "text": message}
            response = requests.post(url, json=payload, headers=headers)
            return response.json()
        except Exception as e:
            logging.info("exception occured at data ingestion stage")
            raise customexception(e,sys)

    # ==== EMAIL ====
    def extract_email_body(self,msg):
        try:
            if 'parts' in msg['payload']:
                for part in msg['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        return base64.urlsafe_b64decode(part['body']['data']).decode()
            return ""
        except Exception as e:
            logging.info("exception occured at data ingestion stage")
            raise customexception(e,sys)

    # ==== SUMMARIZE ====
    def summarize_email(self,email_body):
        """Summarizes email content using LLM."""
        try:
            if not email_body.strip():
                return "Summary not available."

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=100)
            split_texts = text_splitter.split_text(email_body)

            prompt_template = PromptTemplate(
                input_variables=['text'],
                template="Summarize the following email:\n{text}"
            )

            summary_chain = LLMChain(llm=llm, prompt=prompt_template)
            summary = summary_chain.run({"text": split_texts[0]})

            return summary
        except Exception as e:
            logging.info("exception occured at data ingestion stage")
            raise customexception(e,sys)
    # ==== MEETING ====
    def detect_meeting_request(self,email_body):
        try:
            prompt = PromptTemplate(input_variables=['text'], template="Does this email contain a request to schedule a meeting? Answer with 'Yes' or 'No'.\n{text}")
            chain = LLMChain(llm=llm, prompt=prompt)
            return chain.run({"text": email_body}).strip().lower() == "yes"
        except Exception as e:
            logging.info("exception occured at data ingestion stage")
            raise customexception(e,sys)

    def extract_meeting_details(self,email_body):
        try:
            prompt = PromptTemplate(input_variables=['text'], template="Extract meeting details from this email (date, time, title, attendees) and return as JSON.\n{text}")
            chain = LLMChain(llm=llm, prompt=prompt)
            response = chain.run({"text": email_body})
            try:
                return json.loads(response)
            except:
                return {}
        except Exception as e:
            logging.info("exception occured at data ingestion stage")
            raise customexception(e,sys)
        

    def create_calendar_event(self,service, event_details):
        try:
            event = {
                'summary': event_details.get('title', 'Meeting'),
                'start': {'dateTime': event_details.get('start_time'), 'timeZone': 'UTC'},
                'end': {'dateTime': event_details.get('end_time'), 'timeZone': 'UTC'},
                'attendees': [{'email': email} for email in event_details.get('attendees', [])]
            }
            service.events().insert(calendarId='primary', body=event).execute()
            return f"Meeting '{event['summary']}' scheduled!"
        except Exception as e:
            logging.info("exception occured at data ingestion stage")
            raise customexception(e,sys)

    # ==== REPLY ====
    def generate_reply_suggestion(self,email_body):
        """Generate a reply for an email."""
        try:
            if not email_body.strip():
                return "Reply suggestion not available."

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=100)
            split_texts = text_splitter.split_text(email_body)

            prompt_template = PromptTemplate(
                input_variables=['text'],
                template="Generate a professional reply to this email:\n{text}"
            )

            reply_chain = LLMChain(llm=llm, prompt=prompt_template)
            reply_suggestion = reply_chain.run({"text": split_texts[0]})

            return reply_suggestion
         
        except Exception as e:
            logging.info("exception occured at data ingestion stage")
            raise customexception(e,sys)

    # ==== WEB SEARCH ====
    def search_google(self,query):
        try:
            url = f"https://www.googleapis.com/customsearch/v1"
            params = {
                'key': GOOGLE_SEARCH_API_KEY,
                'cx': GOOGLE_SEARCH_CX,
                'q': query
            }
            response = requests.get(url, params=params)
            results = response.json().get("items", [])
            return "\n".join([f"- {item['title']}: {item['link']}" for item in results[:3]])
        
        except Exception as e:
            logging.info("exception occured at data ingestion stage")
            raise customexception(e,sys)

    def should_search_web(self,email_body):
        try:
            prompt = PromptTemplate(input_variables=['text'], template="Does this email require searching the web for information? Answer 'Yes' or 'No'.\n{text}")
            chain = LLMChain(llm=llm, prompt=prompt)
            return chain.run({"text": email_body}).strip().lower() == "yes"
        except Exception as e:
            logging.info("exception occured at data ingestion stage")
            raise customexception(e,sys)


    # ==== DATABASE ====
    def setup_database(self):
        try:
            conn = sqlite3.connect('emails.db')
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS emails (
                                id TEXT PRIMARY KEY,
                                sender TEXT,
                                recipient TEXT,
                                subject TEXT,
                                body TEXT,
                                summary TEXT,
                                reply_suggestion TEXT)
                        ''')
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.info("exception occured at data ingestion stage")
            raise customexception(e,sys)

    def save_email_to_db(self,email_data):
        try:
            conn = sqlite3.connect('emails.db')
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO emails VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (email_data['id'], email_data['sender'], email_data['recipient'],
                            email_data['subject'], email_data['body'], email_data['summary'],
                            email_data['reply_suggestion']))
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.info("exception occured at data ingestion stage")
            raise customexception(e,sys)

    # ==== MAIN ====
    def fetch_emails(self,service, max_results=5):
        try:
            results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=max_results).execute()
            return results.get('messages', [])
        except Exception as e:
            logging.info("exception occured at data ingestion stage")
            raise customexception(e,sys)
    
    #==== SEND MAIL ====  
    def send_email_reply(self,service, to_email, subject, body):
        """Send an email reply using Gmail API."""
        message = f"Subject: {subject}\nTo: {to_email}\n\n{body}"
        encoded_message = base64.urlsafe_b64encode(message.encode()).decode()
        
        raw_message = {'raw': encoded_message}
        service.users().messages().send(userId="me", body=raw_message).execute()

    def is_safe_for_autoreply(self,email_body):
        prompt = PromptTemplate(
            input_variables=['text'],
            template=(
                "Can this email be safely auto-replied to with minimal human oversight? "
                "Reply with 'Yes' or 'No'.\n\nEmail:\n{text}"
            )
        )
        chain = LLMChain(llm=llm, prompt=prompt)
        response = chain.run({"text": email_body}).strip().lower()
        return response == "yes"