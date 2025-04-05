import streamlit as st
from googleapiclient.discovery import build
from src.email_assistant.Authentication.auth import authenticate
from src.email_assistant.process_email.process_email import process_emails
from src.email_assistant.utils.utils import utils

st.set_page_config(page_title="AI Email Assistant", layout="wide")
st.title("📧 AI-Powered Email Assistant")

# Initialize helpers
auth_handler = authenticate()
utils_handler = utils()
email_processor = process_emails()

# Session state
if 'emails' not in st.session_state:
    st.session_state['emails'] = []

# Sidebar
with st.sidebar:
    st.header("Controls")
    max_results = st.slider("How many emails to fetch?", min_value=1, max_value=20, value=5)
    fetch_btn = st.button("🔄 Fetch & Process Emails")

# Main logic
if fetch_btn:
    try:
        creds = auth_handler.authenticate_google()
        service = build('gmail', 'v1', credentials=creds)
        calendar_service = build('calendar', 'v3', credentials=creds)
        utils_handler.setup_database()

        messages = utils_handler.fetch_emails(service, max_results=max_results)
        emails_data = []

        for msg in messages:
            email_data = email_processor.process_email(service, msg['id'], calendar_service)
            utils_handler.save_email_to_db(email_data)
            emails_data.append(email_data)

        st.session_state['emails'] = emails_data
        st.success("✅ Emails processed successfully!")

    except Exception as e:
        st.error(f"❌ Error occurred: {e}")

# Display email cards
for email in st.session_state['emails']:
    with st.expander(f"📬 {email['subject']} — From: {email['sender']}"):
        st.markdown(f"**Summary:** {email['summary']}")
        st.markdown(f"**Reply Suggestion:**\n\n{email['reply_suggestion']}")
        if "urgent" in email['subject'].lower():
            st.warning("🚨 This email was marked as URGENT.")
