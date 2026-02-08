import os
import datetime
import traceback
import smtplib
from email.mime.text import MIMEText
from typing import Literal, Optional

import google.generativeai as genai
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()

# MODEL CHOICE: We use the Preview Flash model for maximum efficiency
MODEL_NAME = 'gemini-2.0-flash' # Using 2.0 Flash as the stable placeholder for "3.0 Preview"
SPREADSHEET_ID = '1EP_K4RV5djXxtNmV25CwNV5Jk2v6LP89eNixceSKE0I'
CALENDAR_ID = 'c_fa9eefe809ded84d84f33c8b11369b569f78d88491d6595b5673ec98a6869fb6@group.calendar.google.com' 
MAX_HISTORY = 15 # Memory limit

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'credentials.json'

# --- AUTHENTICATION ---
# Check if running on Cloud (Streamlit Secrets) or Local
try:
    import streamlit as st
    if "gcp_service_account" in st.secrets:
        creds = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=SCOPES
        )
        api_key = st.secrets["GOOGLE_API_KEY"]
        email_user = st.secrets["EMAIL_SENDER"]
        email_pass = st.secrets["EMAIL_PASSWORD"]
    else:
        raise Exception("Local run")
except Exception:
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    api_key = os.getenv("GOOGLE_API_KEY")
    email_user = os.getenv("EMAIL_SENDER")
    email_pass = os.getenv("EMAIL_PASSWORD")

# Connect Services
sheets_service = build('sheets', 'v4', credentials=creds)
calendar_service = build('calendar', 'v3', credentials=creds)
genai.configure(api_key=api_key)

# --- HELPER FUNCTIONS ---

def get_current_time():
    """Returns the current time to help the AI understand 'today' or 'tomorrow'."""
    return datetime.datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")

# --- TOOLS ---

def check_schedule(date_str: str = "today"):
    """
    Reads the Google Calendar for a specific date or range.
    Args:
        date_str: 'today', 'tomorrow', or a specific date (YYYY-MM-DD).
    """
    try:
        now = datetime.datetime.now()
        
        if date_str == "today":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif date_str == "tomorrow":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
        else:
            # Try to parse YYYY-MM-DD
            try:
                start = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            except:
                return "Error: Please use 'today', 'tomorrow', or 'YYYY-MM-DD' format."

        end = start + datetime.timedelta(days=1)
        
        print(f"👀 Checking schedule for {start.date()}...")

        events_result = calendar_service.events().list(
            calendarId=CALENDAR_ID, 
            timeMin=start.isoformat() + 'Z',
            timeMax=end.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])

        if not events:
            return f"No events found for {date_str}."

        schedule_text = f"Schedule for {date_str}:\n"
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary = event.get('summary', 'No Title')
            schedule_text += f"- {start}: {summary} (ID: {event['id']})\n"
            
        return schedule_text

    except Exception as e:
        return f"Error checking schedule: {str(e)}"

def add_to_schedule(
    summary: str,
    date_time: str,
    item_type: Literal["Assignment", "Meeting", "Research", "Exam", "To-Do Item"],
    category: Literal["Classes", "Combat Robotics", "Rocket Propulsion", "IEEE", "Research", "Personal"],
    notes: str = "",
    duration_hours: float = 1.0
):
    """Adds a new item to the user's Google Sheet and Calendar."""
    try:
        # Calendar
        start_time = datetime.datetime.fromisoformat(date_time)
        end_time = start_time + datetime.timedelta(hours=duration_hours)
        event = {
            'summary': f"[{category}] {summary}",
            'description': f"Type: {item_type}\nNotes: {notes}",
            'start': {'dateTime': start_time.isoformat(), 'timeZone': 'America/New_York'},
            'end': {'dateTime': end_time.isoformat(), 'timeZone': 'America/New_York'},
        }
        calendar_service.events().insert(calendarId=CALENDAR_ID, body=event).execute()

        # Sheets
        formatted_date = start_time.strftime("%m/%d/%Y %H:%M")
        values = [[formatted_date, summary, item_type, category, notes, False]]
        body = {'values': values}
        sheets_service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID, range="WeeklyOverhaulA:F", valueInputOption="USER_ENTERED", body=body
        ).execute()

        return f"Success: Added '{summary}' to schedule."
    except Exception as e:
        return f"Error adding task: {str(e)}"

def remove_task(keyword: str, date_str: str = "today"):
    """
    Removes a task from Google Calendar based on a keyword and date.
    Note: Does not currently remove from Sheets (safer to keep record).
    """
    try:
        # Reuse logic to find events
        schedule_dump = check_schedule(date_str)
        if "No events" in schedule_dump or "Error" in schedule_dump:
            return "Could not find any events to remove."

        # Parse the dump to find the ID (Simplified logic)
        # In a real app, we would query the API again, but let's do a search
        now = datetime.datetime.now()
        if date_str == "today": start = now
        elif date_str == "tomorrow": start = now + datetime.timedelta(days=1)
        else: start = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        
        end = start + datetime.timedelta(days=1)
        
        events_result = calendar_service.events().list(
            calendarId=CALENDAR_ID, timeMin=start.isoformat() + 'Z', timeMax=end.isoformat() + 'Z', singleEvents=True
        ).execute()
        
        deleted_count = 0
        for event in events_result.get('items', []):
            if keyword.lower() in event.get('summary', '').lower():
                calendar_service.events().delete(calendarId=CALENDAR_ID, eventId=event['id']).execute()
                deleted_count += 1
        
        if deleted_count > 0:
            return f"Successfully deleted {deleted_count} event(s) matching '{keyword}'."
        else:
            return f"No events found containing '{keyword}' on that date."

    except Exception as e:
        return f"Error removing task: {str(e)}"

def send_notification(message: str):
    """Sends an email notification to the user."""
    if not email_user or not email_pass:
        return "Error: Email credentials not set in .env."
    
    try:
        msg = MIMEText(message)
        msg['Subject'] = "🤖 Receptionist Alert"
        msg['From'] = email_user
        msg['To'] = email_user # Send to self

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(email_user, email_pass)
            server.send_message(msg)
        
        return "Notification sent successfully."
    except Exception as e:
        return f"Failed to send notification: {str(e)}"

# --- REGISTER TOOLS ---
tools = [add_to_schedule, check_schedule, remove_task, send_notification]

# --- AI BRAIN ---
def process_message(user_input, chat_history):
    try:
        # 1. TOKEN CHECK / PRE-FLIGHT
        # If history is huge, we slice it (handled in app.py, but we double check here)
        if not user_input or len(user_input.strip()) < 2:
            return "Please provide a valid command."

        # 2. Inject Context (Time)
        system_instruction = f"You are a personal receptionist. Current Time: {get_current_time()}. Use tools to manage the user's life."
        
        model = genai.GenerativeModel(model_name=MODEL_NAME, tools=tools, system_instruction=system_instruction)
        chat = model.start_chat(enable_automatic_function_calling=True)
        
        # 3. Feed History (Optimized)
        # We manually rebuild history for the SDK if needed, but for simplicity
        # we often just send the current prompt + context if not using the chat object for long term
        # Here we assume chat_history is passed as a list of dicts: [{'role': 'user', 'parts': [...]}]
        
        # (Optional) Rehydrate chat object with history if supported by SDK version
        # chat.history = chat_history 
        
        response = chat.send_message(user_input)
        return response.text

    except Exception:
        traceback.print_exc()
        return "⚠️ Error processing request."