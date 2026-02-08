import os
import datetime
import traceback
import smtplib
from email.mime.text import MIMEText
from typing import Literal

import google.generativeai as genai
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()

# MODEL: Updated to the latest Flash Lite preview (closest to your request)
# If this gives a 404, switch to 'gemini-2.0-flash' or 'gemini-1.5-flash'
MODEL_NAME = 'gemini-2.0-flash-lite-preview-02-05'

# UPDATED IDs
SPREADSHEET_ID = '1EP_K4RV5djXxtNmV25CwNV5Jk2v6LP89eNixceSKE0I'
CALENDAR_ID = 'c_fa9eefe809ded84d84f33c8b11369b569f78d88491d6595b5673ec98a6869fb6@group.calendar.google.com'
SHEET_RANGE = 'WeeklyOverhaul!A:F'  # Updated Sheet Name

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'credentials.json'

# --- AUTHENTICATION ---
try:
    import streamlit as st
    if "gcp_service_account" in st.secrets:
        creds = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=SCOPES
        )
        api_key = st.secrets["GOOGLE_API_KEY"]
        email_user = st.secrets.get("EMAIL_SENDER")
        email_pass = st.secrets.get("EMAIL_PASSWORD")
    else:
        raise Exception("Local run")
except Exception:
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    api_key = os.getenv("GOOGLE_API_KEY")
    email_user = os.getenv("EMAIL_SENDER")
    email_pass = os.getenv("EMAIL_PASSWORD")

sheets_service = build('sheets', 'v4', credentials=creds)
calendar_service = build('calendar', 'v3', credentials=creds)
genai.configure(api_key=api_key)

# --- HELPER FUNCTIONS ---
def get_current_time():
    """Returns the current date and time in a clear format."""
    return datetime.datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")

# --- TOOL DEFINITIONS ---

def check_schedule(date_str: str = "today"):
    """Reads the calendar for a specific day."""
    try:
        print(f"👀 Checking schedule for {date_str}...")
        now = datetime.datetime.now()
        
        # Handle 'today', 'tomorrow', or specific dates
        if date_str.lower() == "today":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif date_str.lower() == "tomorrow":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
        else:
            try:
                start = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                return "Error: Date must be YYYY-MM-DD, 'today', or 'tomorrow'."
        
        end = start + datetime.timedelta(days=1)
        
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

        text = f"Schedule for {date_str}:\n"
        for event in events:
            # Handle different time formats (all-day vs timed)
            start_t = event['start'].get('dateTime', event['start'].get('date'))
            summary = event.get('summary', 'No Title')
            text += f"- {start_t}: {summary}\n"
            
        return text
    except Exception as e:
        return f"Error checking schedule: {str(e)}"

def add_to_schedule(summary: str, date_time: str, item_type: str, category: str, notes: str = "", duration_hours: float = 1.0):
    """Adds item to Calendar and Sheets (WeeklyOverhaul)."""
    try:
        print(f"📝 Adding to schedule: {summary}")
        # Parse the ISO date string provided by Gemini
        start_time = datetime.datetime.fromisoformat(date_time)
        end_time = start_time + datetime.timedelta(hours=duration_hours)
        
        # 1. Add to Google Calendar
        event = {
            'summary': f"[{category}] {summary}",
            'description': f"Type: {item_type}\nNotes: {notes}",
            'start': {'dateTime': start_time.isoformat(), 'timeZone': 'America/New_York'},
            'end': {'dateTime': end_time.isoformat(), 'timeZone': 'America/New_York'},
        }
        calendar_service.events().insert(calendarId=CALENDAR_ID, body=event).execute()

        # 2. Add to Google Sheets (Using new WeeklyOverhaul tab)
        formatted_date = start_time.strftime("%m/%d/%Y %H:%M")
        values = [[formatted_date, summary, item_type, category, notes, False]]
        body = {'values': values}
        
        sheets_service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID, 
            range=SHEET_RANGE,  # Uses "WeeklyOverhaul!A:F"
            valueInputOption="USER_ENTERED", 
            body=body
        ).execute()

        return f"Success: Added '{summary}' to schedule."
    except Exception as e:
        return f"Error adding task: {str(e)}"

def remove_task(keyword: str, date_str: str = "today"):
    """Removes a task from Calendar by keyword."""
    try:
        print(f"🗑️ Removing task: {keyword}")
        now = datetime.datetime.now()
        if date_str == "today": start = now.replace(hour=0, minute=0, second=0)
        elif date_str == "tomorrow": start = now.replace(hour=0, minute=0, second=0) + datetime.timedelta(days=1)
        else: start = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        end = start + datetime.timedelta(days=1)

        events = calendar_service.events().list(
            calendarId=CALENDAR_ID, timeMin=start.isoformat() + 'Z', timeMax=end.isoformat() + 'Z', singleEvents=True
        ).execute().get('items', [])

        deleted = 0
        for event in events:
            if keyword.lower() in event.get('summary', '').lower():
                calendar_service.events().delete(calendarId=CALENDAR_ID, eventId=event['id']).execute()
                deleted += 1
        
        if deleted == 0: return f"No events found matching '{keyword}'."
        return f"Success: Deleted {deleted} event(s)."
    except Exception as e: return f"Error removing: {str(e)}"

def send_notification(message: str):
    """Sends email notification."""
    if not email_user or not email_pass: return "Error: Email credentials not configured."
    try:
        print(f"📧 Sending email...")
        msg = MIMEText(message)
        msg['Subject'] = "Receptionist Alert"
        msg['From'] = email_user
        msg['To'] = email_user
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(email_user, email_pass)
            s.send_message(msg)
        return "Notification sent."
    except Exception as e: return f"Email failed: {e}"

# --- REGISTER TOOLS ---
tools = [add_to_schedule, check_schedule, remove_task, send_notification]

# Map string names to actual functions (Safe Dispatch)
tool_map = {
    'add_to_schedule': add_to_schedule,
    'check_schedule': check_schedule,
    'remove_task': remove_task,
    'send_notification': send_notification
}

# --- AI BRAIN ---
def process_message(user_input, chat_history):
    try:
        # 1. SETUP MODEL
        system_instruction = f"You are a helpful receptionist. Use tools to manage the schedule."
        model = genai.GenerativeModel(model_name=MODEL_NAME, tools=tools, system_instruction=system_instruction)
        chat = model.start_chat(enable_automatic_function_calling=False)
        
        # 2. INJECT DATE INTO PROMPT
        # By adding this to the user's message, the model CANNOT miss it.
        date_context = f" [System Info: The current date and time is {get_current_time()}]"
        augmented_input = user_input + date_context
        
        response = chat.send_message(augmented_input)
        
        # 3. MANUAL DISPATCH (Safe Mode)
        if not response.parts:
            return "⚠️ Error: AI returned empty response."
            
        part = response.candidates[0].content.parts[0]
        
        if part.function_call:
            fc = part.function_call
            func_name = fc.name
            args = dict(fc.args)
            
            print(f"🤖 Gemini Request: {func_name} | Args: {args}")
            
            if func_name in tool_map:
                result = tool_map[func_name](**args)
            else:
                result = f"Error: Function {func_name} not found."
            
            print(f"✅ Tool Result: {result}")

            # Send result back
            function_response = {
                "function_response": {
                    "name": func_name,
                    "response": {"result": result}
                }
            }
            final_response = chat.send_message(function_response)
            return final_response.text

        else:
            return response.text

    except Exception as e:
        traceback.print_exc()
        return f"⚠️ System Error: {str(e)}"
