## Intelligent Email Assistant

An AI-powered assistant that integrates with Gmail, Slack, and Google Calendar to intelligently manage and respond to emails. This system leverages large language models (LLMs) for summarization, intent detection, auto-reply, and scheduling—enhancing productivity and communication efficiency.

## Features

- Fetches and processes incoming emails
- Summarizes email content using Groq LLM (Gemma-2 9B)
- Detects and schedules meetings via Google Calendar
- Suggests and optionally sends auto-generated replies
- Sends Slack notifications for important messages
- Performs Google web searches for contextually rich replies
- Stores processed emails in a local SQLite database

## Technologies Used

| Technology             | Purpose                               |
|------------------------|----------------------------------------|
| Python 3.9+            | Core programming language              |
| LangChain + Groq       | Natural language processing            |
| Gmail API              | Email read/send access                 |
| Google Calendar API    | Scheduling and event management        |
| Slack API              | Real-time alerting and notifications   |
| Google Custom Search   | Web search integration                 |
| SQLite                 | Local database storage                 |

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/kishan444444/kishan_verma-wasserstoff-AiInternTask.git
cd kishan_verma-wasserstoff-AiInternTask
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up API Credentials

#### Gmail & Google Calendar

- Visit [Google Cloud Console](https://console.cloud.google.com/)
- Enable Gmail and Calendar APIs
- Download the `credentials.json` file
- Place it in the project root directory

#### Groq (LLM)

- Obtain your API key from [Groq](https://console.groq.com)
- Add it to your `.env` file as `GROQ_API_KEY`

#### Slack

- Create a bot via [Slack API](https://api.slack.com/)
- Enable `chat:write` scope
- Add `SLACK_BOT_TOKEN` and `SLACK_CHANNEL_ID` to `.env`

#### Google Custom Search

- Get an API Key from [Google Developers Console](https://console.developers.google.com/)
- Create a Search Engine and retrieve your `cx` ID
- Add both to `.env`

### 4. Configure Environment Variables

Create a `.env` file with the following content:

```env
GROQ_API_KEY=your_groq_api_key
SLACK_BOT_TOKEN=your_slack_token
SLACK_CHANNEL_ID=your_channel_id
GOOGLE_SEARCH_API_KEY=your_search_api_key
GOOGLE_SEARCH_CX=your_custom_search_engine_id
```

### 5. Run the Assistant

```bash
streamlit run main.py
```

## Sample Output

```
From: john@example.com | Subject: Project Kickoff
Summary: Request to set up a meeting to discuss project scope and deliverables.
Reply Suggestion:
Thank you for reaching out. I’m available to meet tomorrow at 3 PM to discuss the project scope. Please confirm your availability.
```

## System Architecture

```
+------------+        +--------------------+        +------------------+
| Gmail API  | -----> | Email Processor    | -----> | LangChain + Groq |
+------------+        +--------------------+        +------------------+
                                                     |
                                                     |
       +------------------+     +-------------------+ +--------------------+
       | Slack Notifier   |<----| Important Detector| | Meeting Scheduler  |
       +------------------+     +-------------------+ +--------------------+
                                                           |
                                                     +-------------------+
                                                     | Google Calendar   |
                                                     +-------------------+
```

## Description

- Emails are fetched via the Gmail API
- Emails are processed for summarization, intent detection, and reply suggestion
- Important emails are flagged and notified via Slack
- Meeting requests trigger Google Calendar event creation
- Auto-replies are sent when considered safe
- A local database stores all processed data

## Security Guidelines

- Do not commit API keys or the `token.json` file to version control

## Project Structure

```
email_assistant/
├── .env                        # Environment variables (API keys, secrets)
├── main.py                     # Entry-point to run the assistant
├── requirements.txt            # Project dependencies

├── github/
│   └── workflows/
│       └── .gitkeep            # Placeholder for CI/CD config (e.g., GitHub Actions)

└── src/
    └── email_assistant/
        ├── __init__.py         # Marks the package

        ├── Authentication/
        │   ├── __init__.py     # Package initializer
        │   └── auth.py         # Handles Google Auth (Gmail & Calendar)

        ├── utils/
        │   ├── __init__.py     # Package initializer
        │   └── utils.py        # Utility functions (e.g., Slack, search)

        ├── process_email/
        │   ├── __init__.py     # Package initializer
        │   └── process_email.py# Core logic: summarize, detect meetings, reply

        ├── logger.py           # Custom logger configuration
        └── exception.py        # Custom exceptions and error handling
```

## Future Enhancements

- Real-time email monitoring using push notifications
- Integration with voice assistants (e.g., Alexa, Google Assistant)
- Web-based dashboard for managing summaries and replies
- Sentiment analysis and email prioritization

## Author

**Kishan Verma**


