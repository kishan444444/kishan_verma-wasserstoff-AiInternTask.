
from src.email_assistant.utils.utils import utils
from src.email_assistant.logger import logging
from src.email_assistant.exception import customexception
utils=utils()
import sys

class process_emails():
    def __init__(self):
        pass
    def process_email(self,service, msg_id, calendar_service):
        try:
            msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
            headers = msg['payload']['headers']
            email_body = utils.extract_email_body(msg)

            email_data = {
                'id': msg_id,
                'sender': next((h['value'] for h in headers if h['name'] == 'From'), None),
                'recipient': next((h['value'] for h in headers if h['name'] == 'To'), None),
                'subject': next((h['value'] for h in headers if h['name'] == 'Subject'), None),
                'body': email_body,
                'summary': utils.summarize_email(email_body),
                'reply_suggestion': utils.generate_reply_suggestion(email_body)
            }

            # ==== Important Email Detection ====
            important_keywords = [
                "urgent", "asap", "action required", "important", "immediate",
                "follow-up", "deadline", "response needed", "critical", "time sensitive"
            ]
            
            subject = (email_data['subject'] or "").lower()
            body = (email_body or "").lower()
            
            if any(keyword in subject or keyword in body for keyword in important_keywords):
                utils.send_slack_notification(
                    f"📬 *Important Email Alert!*\nFrom: `{email_data['sender']}`\nSubject: *{email_data['subject']}*"
                )

            if utils.detect_meeting_request(email_body):
                meeting_details = utils.extract_meeting_details(email_body)
                if meeting_details:
                    utils.create_calendar_event(calendar_service, meeting_details)
                    email_data['reply_suggestion'] = f"Meeting scheduled: {meeting_details.get('title', 'Untitled')}"

            if utils.should_search_web(email_body):
                search_results = utils.search_google(email_body[:300])
                email_data['reply_suggestion'] += f"\n\n🧠 Web Search Info:\n{search_results}"

            if utils.is_safe_for_autoreply(email_body):
                utils.send_email_reply(service, email_data['sender'], f"Re: {email_data['subject']}", email_data['reply_suggestion'])
            
            
            return email_data
    
        except Exception as e:
                logging.info("exception occured at data ingestion stage")
                raise customexception(e,sys)

    

        
        
        
        
