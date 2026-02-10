import os
import datetime
import traceback
import smtplib
import time
import json
import pytz 
import re
from email.mime.text import MIMEText

import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, DeadlineExceeded, ServiceUnavailable
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv
import streamlit as st

# --- CONFIGURATION ---
load_dotenv()

# MODEL
MODEL_NAME = 'gemini-1.5-flash' # 'gemini-3-flash-preview' is often experimental, 1.5-flash is stable for tools

# IDs (Replace these with your actual IDs if they change)
SPREADSHEET_ID = '1EP_K4RV5djXxtNmV25CwNV5Jk2v6LP89eNixceSKE0I'
CALENDAR_ID = 'c_fa9eefe809ded84d84f33c8b11369b569f78d88491d6595b5673ec98a6869fb6@group.calendar.google.com'
SHEET_RANGE = 'WeeklyOverhaul!A:F'
TIMEZONE = 'America/New_York' 

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/calendar']

# --- SMART CATEGORIES ---
VALID_TYPES = ["Assignment", "Meeting", "Research", "Exam", "To-Do Item"]
VALID_CATEGORIES = ["Combat Robotics", "Rocket Propulsion", "IEEE", "Fluids Research", "LRE Project", "General"]

# --- AUTHENTICATION & KEY ROTATION ---
api_keys = []
current_key_index = 0
creds = None
email_user = None
email_pass = None

def initialize_auth():
    global creds, email_user, email_pass
    
    # 1. Try Streamlit Secrets (Cloud)
    try:
        # API Keys
        i = 1
        while True:
            key = st.secrets.get(f"API_KEY_{i}")
            if not key: break
            api_keys.append(key)
            i += 1
        
        if not api_keys and "GOOGLE_API_KEY" in st.secrets:
            api_keys.append(st.secrets["GOOGLE_API_KEY"])

        # Service Account
        if "gcp_service_account" in st.secrets:
            creds = service_account.Credentials.from_service_account_info(
                st.secrets["gcp_service_account"], scopes=SCOPES
            )
        
        # Email
        email_user = st.secrets.get("EMAIL_SENDER")
        email_pass = st.secrets.get("EMAIL_PASSWORD")

    except FileNotFoundError:
        pass # Secrets file not found, try local

    # 2. Try Local Environment / Files (Fallback)
    if not api_keys or not creds:
        try:
            # API Keys
            i = 1
            while True:
                key = os.getenv(f"API_KEY_{i}")
                if not key: break
                api_keys.append(key)
                i += 1
            
            if not api_keys and os.getenv("GOOGLE_API_KEY"):
                api_keys.append(os.getenv("GOOGLE_API_KEY"))

            # Service Account
            if os.path.exists('credentials.json'):
                creds = service_account.Credentials.from_service_account_file(
                    'credentials.json', scopes=SCOPES
                )
            
            email_user = os.getenv("EMAIL_SENDER")
            email_pass = os.getenv("EMAIL_PASSWORD")
        except Exception as e:
            print(f"Local auth failed: {e}")

    if api_keys:
        genai.configure(api_key=api_keys[0])
    else:
        print("❌ CRITICAL: No API Keys found.")

# Initialize Auth immediately
initialize_auth()

# Build Services
try:
    sheets_service = build('sheets', 'v4', credentials=creds)
    calendar_service = build('calendar', 'v3', credentials=creds)
except Exception as e:
    print(f"⚠️ Service Build Error (Check Credentials): {e}")
    sheets_service = None
    calendar_service = None

# --- HELPER FUNCTIONS ---
def switch_api_key():
    global current_key_index
    if len(api_keys) <= 1: return False
    current_key_index = (current_key_index + 1) % len(api_keys)
    genai.configure(api_key=api_keys[current_key_index])
    return True

def get_current_time():
    tz = pytz.timezone(TIMEZONE)
    return datetime.datetime.now(tz).strftime("%A, %B %d, %Y at %I:%M %p %Z")

def get_date_range(date_str, days=1):
    tz = pytz.timezone(TIMEZONE)
    now = datetime.datetime.now(tz)
    
    if date_str.lower() == "today":
        start_dt = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif date_str.lower() == "tomorrow":
        start_dt = (now + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        try:
            dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            start_dt = tz.localize(dt)
        except:
             start_dt = now.replace(hour=0, minute=0, second=0, microsecond=0)

    end_dt = start_dt + datetime.timedelta(days=days)
    return start_dt.isoformat(), end_dt.isoformat()

def format_event_time(iso_str):
    try:
        if 'T' in iso_str:
            dt = datetime.datetime.fromisoformat(iso_str)
            return dt.strftime("%I:%M %p") # Simplified for voice
        else:
            dt = datetime.datetime.strptime(iso_str, "%Y-%m-%d")
            return "All Day"
    except:
        return iso_str 

def parse_smart_time(time_input, original_date_obj=None):
    tz = pytz.timezone(TIMEZONE)
    time_input = time_input.strip().upper()

    try:
        dt = datetime.datetime.fromisoformat(time_input)
        if dt.tzinfo is None: dt = tz.localize(dt)
        return dt
    except: pass

    if not original_date_obj: return None

    target_date = original_date_obj.date()
    formats = ["%H:%M", "%I:%M %p", "%I %p", "%I%p"] 
    
    for fmt in formats:
        try:
            t = datetime.datetime.strptime(time_input, fmt).time()
            dt = datetime.datetime.combine(target_date, t)
            return tz.localize(dt)
        except: continue
        
    return None

# --- TOOLS ---
def list_upcoming_events(max_results: float = 10):
    if not calendar_service: return "Calendar service unavailable."
    try:
        tz = pytz.timezone(TIMEZONE)
        now = datetime.datetime.now(tz).isoformat()
        events_result = calendar_service.events().list(
            calendarId=CALENDAR_ID, timeMin=now, maxResults=int(max_results), singleEvents=True, orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])
        if not events: return "No upcoming events found."
        
        # Return raw data for AI to narrate
        data_str = ""
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            time_str = format_event_time(start)
            summary = event.get('summary', 'No Title')
            data_str += f"{time_str}: {summary}. "
        return data_str
    except Exception as e: return f"Error fetching events: {str(e)}"

def check_schedule(date_str: str = "today"):
    if not calendar_service: return "Calendar service unavailable."
    try:
        start_iso, end_iso = get_date_range(date_str)
        events_result = calendar_service.events().list(
            calendarId=CALENDAR_ID, timeMin=start_iso, timeMax=end_iso, singleEvents=True, orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])
        if not events: return f"No events found for {date_str}."
        
        data_str = f"Events for {date_str}: "
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            time_str = format_event_time(start)
            summary = event.get('summary', 'No Title')
            data_str += f"{time_str}: {summary}. "
        return data_str
    except Exception as e: return f"Error checking schedule: {str(e)}"

def add_to_schedule(summary: str, date_time: str, item_type: str, category: str, notes: str = "", duration_hours: float = 1.0):
    if not calendar_service: return "Calendar service unavailable."
    try:
        if item_type not in VALID_TYPES: item_type = "To-Do Item"
        if category not in VALID_CATEGORIES: category = "General"

        try: start_time = datetime.datetime.fromisoformat(date_time)
        except: start_time = datetime.datetime.strptime(date_time, "%Y-%m-%dT%H:%M:%S")

        if start_time.tzinfo is None:
            tz = pytz.timezone(TIMEZONE)
            start_time = tz.localize(start_time)

        end_time = start_time + datetime.timedelta(hours=duration_hours)
        event = {
            'summary': f"[{category}] {summary}",
            'description': f"Type: {item_type}\nNotes: {notes}",
            'start': {'dateTime': start_time.isoformat(), 'timeZone': TIMEZONE},
            'end': {'dateTime': end_time.isoformat(), 'timeZone': TIMEZONE},
        }
        calendar_service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        
        if sheets_service:
            formatted_date = start_time.strftime("%m/%d/%Y %H:%M")
            values = [[formatted_date, summary, item_type, category, notes, False]]
            sheets_service.spreadsheets().values().append(
                spreadsheetId=SPREADSHEET_ID, range=SHEET_RANGE, valueInputOption="USER_ENTERED", body={'values': values}
            ).execute()
            
        return f"Added '{summary}' to your schedule."
    except Exception as e: return f"Error adding task: {str(e)}"

def update_event(keyword: str, date_str: str = "today", new_start_time: str = None, new_title: str = None):
    if not calendar_service: return "Calendar service unavailable."
    try:
        days_to_search = 7 if date_str.lower() == "today" else 2
        start_iso, end_iso = get_date_range(date_str, days=days_to_search)

        events_result = calendar_service.events().list(
            calendarId=CALENDAR_ID, timeMin=start_iso, timeMax=end_iso, q=keyword, singleEvents=True
        ).execute()

        events = events_result.get('items', [])
        if not events: return f"Could not find event matching '{keyword}'."

        target_event = events[0]
        event_id = target_event['id']
        
        changes = {}
        if new_title: changes['summary'] = new_title

        if new_start_time:
            current_start_raw = target_event['start'].get('dateTime')
            if current_start_raw:
                current_dt = datetime.datetime.fromisoformat(current_start_raw)
                new_dt = parse_smart_time(new_start_time, current_dt)
                if new_dt:
                    end_dt = new_dt + datetime.timedelta(hours=1)
                    changes['start'] = {'dateTime': new_dt.isoformat(), 'timeZone': TIMEZONE}
                    changes['end'] = {'dateTime': end_dt.isoformat(), 'timeZone': TIMEZONE}

        if not changes: return "No changes were made."

        calendar_service.events().patch(calendarId=CALENDAR_ID, eventId=event_id, body=changes).execute()
        return "Event updated successfully."

    except Exception as e: return f"Error updating event: {str(e)}"

def delete_events(date_str: str = "today", keyword: str = ""):
    if not calendar_service: return "Calendar service unavailable."
    try:
        start_iso, end_iso = get_date_range(date_str)
        events_result = calendar_service.events().list(
            calendarId=CALENDAR_ID, timeMin=start_iso, timeMax=end_iso, singleEvents=True
        ).execute()
        events = events_result.get('items', [])
        
        count = 0
        for event in events:
            title = event.get('summary', '')
            if not keyword or keyword.lower() in title.lower():
                calendar_service.events().delete(calendarId=CALENDAR_ID, eventId=event['id']).execute()
                count += 1
        
        return f"Deleted {count} event(s)."
    except Exception as e: return f"Error removing: {str(e)}"

def send_notification(message: str):
    if not email_user or not email_pass: return "Email not configured."
    try:
        msg = MIMEText(message)
        msg['Subject'] = "Receptionist Alert"
        msg['From'] = email_user
        msg['To'] = email_user
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(email_user, email_pass)
            s.send_message(msg)
        return "Notification sent."
    except Exception as e: return f"Email failed: {e}"

# Tool Mapping
tools_list = [add_to_schedule, check_schedule, list_upcoming_events, update_event, delete_events, send_notification]
tool_map = {
    'add_to_schedule': add_to_schedule,
    'check_schedule': check_schedule,
    'list_upcoming_events': list_upcoming_events, 
    'update_event': update_event,
    'delete_events': delete_events,
    'send_notification': send_notification
}

# --- AI BRAIN ---
def process_message(user_input, chat_history):
    if user_input.upper().strip() in ["STOP", "CANCEL", "RESET", "END"]:
        return "Stopped."

    # --- VOICE OPTIMIZED SYSTEM INSTRUCTION ---
    system_instruction = f"""
    You are N.A.O.M.I., a highly efficient AI assistant.
    
    Current Time: {get_current_time()}
    
    CRITICAL OUTPUT RULES FOR TTS (Text-to-Speech):
    1.  **NO MARKDOWN**: Do not use bold (**), italics (*), headers (#), or code blocks.
    2.  **NO LISTS**: Do not use bullet points or numbered lists.
    3.  **CONVERT TO PROSE**:
        * Bad: "Events: 1. Meeting 2. Lunch"
        * Good: "You have a meeting, followed by lunch."
    4.  **BE CONCISE**: Keep responses under 3 sentences unless detailing a long schedule.
    5.  **NO EMOJIS**: The TTS engine cannot read them.
    
    You have access to Google Calendar and Sheets tools. Use them to manage the user's life.
    """

    max_retries = 2
    attempts = 0
    response = None
    
    while attempts < max_retries:
        try:
            model = genai.GenerativeModel(model_name=MODEL_NAME, tools=tools_list, system_instruction=system_instruction)
            
            # Convert history to Gemini format
            history_formatted = []
            for msg in chat_history:
                role = "user" if msg["role"] == "user" else "model"
                history_formatted.append({"role": role, "parts": [msg["content"]]})
            
            chat = model.start_chat(history=history_formatted, enable_automatic_function_calling=False)
            response = chat.send_message(user_input)
            break 
            
        except Exception:
            switch_api_key()
            attempts += 1
            time.sleep(1)

    if not response:
        return "I am unable to connect to the neural network."

    # Function Calling Logic
    function_calls_found = []
    for part in response.parts:
        if part.function_call:
            function_calls_found.append(part.function_call)
    
    if function_calls_found:
        function_responses = []
        for fc in function_calls_found:
            func_name = fc.name
            args = dict(fc.args)
            
            if func_name in tool_map:
                try:
                    result = tool_map[func_name](**args)
                except Exception as e:
                    result = f"Error: {str(e)}"
            else:
                result = "Function not found."
            
            function_responses.append({
                "function_response": {
                    "name": func_name,
                    "response": {"result": result}
                }
            })
        
        # Send results back to AI for final natural language summary
        try:
            final_response = chat.send_message(function_responses)
            return final_response.text.strip()
        except:
            return "Task completed."

    return response.text.strip()