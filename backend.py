import os
import datetime
import traceback
import smtplib
import time
import pytz 
from email.mime.text import MIMEText

import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted 
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()

# MODEL
MODEL_NAME = 'gemini-3-flash-preview' 

# IDs
SPREADSHEET_ID = '1EP_K4RV5djXxtNmV25CwNV5Jk2v6LP89eNixceSKE0I'
CALENDAR_ID = 'c_fa9eefe809ded84d84f33c8b11369b569f78d88491d6595b5673ec98a6869fb6@group.calendar.google.com'
SHEET_RANGE = 'WeeklyOverhaul!A:F'

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'credentials.json'
TIMEZONE = 'America/New_York' 

# --- KEY ROTATION SYSTEM ---
api_keys = []
current_key_index = 0

try:
    import streamlit as st
    i = 1
    while True:
        key = st.secrets.get(f"API_KEY_{i}")
        if not key: break
        api_keys.append(key)
        i += 1
    
    if not api_keys and "GOOGLE_API_KEY" in st.secrets:
        api_keys.append(st.secrets["GOOGLE_API_KEY"])

    if "gcp_service_account" in st.secrets:
        creds = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=SCOPES
        )
        email_user = st.secrets.get("EMAIL_SENDER")
        email_pass = st.secrets.get("EMAIL_PASSWORD")
    else:
        raise Exception("Local run")

except Exception:
    i = 1
    while True:
        key = os.getenv(f"API_KEY_{i}")
        if not key: break
        api_keys.append(key)
        i += 1
    
    if not api_keys and os.getenv("GOOGLE_API_KEY"):
        api_keys.append(os.getenv("GOOGLE_API_KEY"))

    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    email_user = os.getenv("EMAIL_SENDER")
    email_pass = os.getenv("EMAIL_PASSWORD")

if not api_keys:
    print("❌ WARNING: No API Keys found.")

if api_keys:
    genai.configure(api_key=api_keys[0])

sheets_service = build('sheets', 'v4', credentials=creds)
calendar_service = build('calendar', 'v3', credentials=creds)

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

def get_date_range(date_str):
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
            return None, None

    end_dt = start_dt + datetime.timedelta(days=1)
    return start_dt.isoformat(), end_dt.isoformat()

def format_event_time(iso_str):
    """Converts ISO 8601 strings to human-readable 'Mon, Feb 9 at 10:00 AM'."""
    try:
        # Check if it's a full DateTime (contains 'T')
        if 'T' in iso_str:
            dt = datetime.datetime.fromisoformat(iso_str)
            # Example: Monday, Feb 09 at 10:20 AM
            return dt.strftime("%A, %b %d at %I:%M %p")
        else:
            # It's just a Date (YYYY-MM-DD) for all-day events
            dt = datetime.datetime.strptime(iso_str, "%Y-%m-%d")
            return dt.strftime("%A, %b %d (All Day)")
    except:
        return iso_str # Fallback to original if parsing fails

# --- TOOLS ---
def list_upcoming_events(max_results: float = 50):
    try:
        tz = pytz.timezone(TIMEZONE)
        now = datetime.datetime.now(tz).isoformat()
        events_result = calendar_service.events().list(
            calendarId=CALENDAR_ID, timeMin=now, maxResults=int(max_results), singleEvents=True, orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])
        if not events: return "No upcoming events found."
        
        # Build a pretty list
        text = "📅 Upcoming Events:\n"
        for event in events:
            start_raw = event['start'].get('dateTime', event['start'].get('date'))
            pretty_time = format_event_time(start_raw)
            summary = event.get('summary', 'No Title')
            
            text += f"• {pretty_time}: {summary}\n"
            
        return text
    except Exception as e: return f"Error fetching events: {str(e)}"

def check_schedule(date_str: str = "today"):
    try:
        start_iso, end_iso = get_date_range(date_str)
        if not start_iso: return "Error: Date must be YYYY-MM-DD, 'today', or 'tomorrow'."
        print(f"👀 Checking schedule from {start_iso} to {end_iso}...")
        events_result = calendar_service.events().list(
            calendarId=CALENDAR_ID, timeMin=start_iso, timeMax=end_iso, singleEvents=True, orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])
        if not events: return f"No events found for {date_str}."
        
        text = f"Schedule for {date_str}:\n"
        for event in events:
            start_raw = event['start'].get('dateTime', event['start'].get('date'))
            pretty_time = format_event_time(start_raw)
            summary = event.get('summary', 'No Title')
            
            text += f"• {pretty_time}: {summary}\n"
        return text
    except Exception as e: return f"Error checking schedule: {str(e)}"

def add_to_schedule(summary: str, date_time: str, item_type: str, category: str, notes: str = "", duration_hours: float = 1.0):
    try:
        print(f"📝 Adding to schedule: {summary}")
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
        formatted_date = start_time.strftime("%m/%d/%Y %H:%M")
        values = [[formatted_date, summary, item_type, category, notes, False]]
        sheets_service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID, range=SHEET_RANGE, valueInputOption="USER_ENTERED", body={'values': values}
        ).execute()
        return f"Success: Added '{summary}' to schedule."
    except Exception as e: return f"Error adding task: {str(e)}"

def delete_events(date_str: str = "today", keyword: str = ""):
    try:
        start_iso, end_iso = get_date_range(date_str)
        if not start_iso: return "Error: Invalid date."
        print(f"🗑️ Deleting events from {start_iso} to {end_iso} | Keyword: '{keyword}'")

        events_result = calendar_service.events().list(
            calendarId=CALENDAR_ID, timeMin=start_iso, timeMax=end_iso, singleEvents=True
        ).execute()
        events = events_result.get('items', [])
        if not events: return f"No events found on {date_str} to delete."

        deleted_count = 0
        deleted_titles = []
        
        for event in events:
            title = event.get('summary', 'No Title')
            should_delete = False
            if not keyword or keyword.upper() == "ALL" or keyword.strip() == "": should_delete = True
            elif keyword.lower() in title.lower(): should_delete = True
            
            if should_delete:
                print(f"   ❌ Deleting: {title}")
                calendar_service.events().delete(calendarId=CALENDAR_ID, eventId=event['id']).execute()
                deleted_count += 1
                deleted_titles.append(title)
        
        if deleted_count == 0: return f"Found {len(events)} events, but none matched '{keyword}'."
        return f"Success: Deleted {deleted_count} event(s): {', '.join(deleted_titles)}"
    except Exception as e: return f"Error removing: {str(e)}"

def send_notification(message: str):
    if not email_user or not email_pass: return "Error: Email credentials not configured."
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

tools = [add_to_schedule, check_schedule, list_upcoming_events, delete_events, send_notification]
tool_map = {
    'add_to_schedule': add_to_schedule,
    'check_schedule': check_schedule,
    'list_upcoming_events': list_upcoming_events, 
    'delete_events': delete_events,
    'send_notification': send_notification
}

# --- AI BRAIN ---
def process_message(user_input, chat_history):
    max_retries = len(api_keys) + 1 
    attempts = 0

    while attempts < max_retries:
        try:
            # Updated Prompt: Encourage nice formatting in the AI response too
            system_instruction = "You are a receptionist. Manage the schedule. When listing events, present them in a clean, bulleted format without technical IDs."
            model = genai.GenerativeModel(model_name=MODEL_NAME, tools=tools, system_instruction=system_instruction)
            chat = model.start_chat(enable_automatic_function_calling=False)
            
            date_context = f" [System Info: Current NY Time is {get_current_time()}]"
            augmented_input = user_input + date_context
            
            response = chat.send_message(augmented_input)
            
            function_call_part = None
            for part in response.parts:
                if part.function_call:
                    function_call_part = part
                    break
            
            if function_call_part:
                fc = function_call_part.function_call
                func_name = fc.name
                args = dict(fc.args)
                
                print(f"🤖 Gemini Request: {func_name} | Args: {args}")
                
                if func_name in tool_map:
                    result = tool_map[func_name](**args)
                else:
                    result = f"Error: Function {func_name} not found."
                
                print(f"✅ Tool Result: {result}")

                function_response = {
                    "function_response": {
                        "name": func_name,
                        "response": {"result": result}
                    }
                }
                final_response = chat.send_message(function_response)
                
                try:
                    text_response = final_response.text
                    if not text_response or len(text_response.strip()) < 2:
                        return f"{result}" # Clean result (already formatted by Python)
                    return text_response
                except ValueError:
                    return f"{result}"

            else:
                return response.text

        except ResourceExhausted:
            print("⚠️ API Quota Exceeded!")
            if switch_api_key():
                attempts += 1
                time.sleep(1)
                continue
            else:
                return "⚠️ Error: All API keys have exhausted their quota."
        
        except Exception as e:
            traceback.print_exc()
            return f"⚠️ System Error: {str(e)}"
    
    return "⚠️ Error: Request failed."
