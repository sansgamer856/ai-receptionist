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

# --- CONFIGURATION ---
load_dotenv()

# MODEL
MODEL_NAME = 'gemini-2.0-flash' 

# IDs
SPREADSHEET_ID = '1EP_K4RV5djXxtNmV25CwNV5Jk2v6LP89eNixceSKE0I'
CALENDAR_ID = 'c_fa9eefe809ded84d84f33c8b11369b569f78d88491d6595b5673ec98a6869fb6@group.calendar.google.com'
SHEET_RANGE = 'WeeklyOverhaul!A:F'

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'credentials.json'
TIMEZONE = 'America/New_York' 

# --- SMART CATEGORIES ---
VALID_TYPES = ["Assignment", "Meeting", "Research", "Exam", "To-Do Item"]
VALID_CATEGORIES = ["Combat Robotics", "Rocket Propulsion", "IEEE", "Fluids Research", "LRE Project", "General"]

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
    print(f"🔄 Switched to API Key #{current_key_index + 1}")
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
            return None, None

    end_dt = start_dt + datetime.timedelta(days=days)
    return start_dt.isoformat(), end_dt.isoformat()

def format_event_time(iso_str):
    try:
        if 'T' in iso_str:
            dt = datetime.datetime.fromisoformat(iso_str)
            return dt.strftime("%A, %b %d at %I:%M %p")
        else:
            dt = datetime.datetime.strptime(iso_str, "%Y-%m-%d")
            return dt.strftime("%A, %b %d (All Day)")
    except:
        return iso_str 

def parse_smart_time(time_input, original_date_obj=None):
    """
    Parses fuzzy time strings (e.g. "15:00", "3pm", "3:00 PM")
    and combines them with the original event date.
    """
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
def list_upcoming_events(max_results: float = 50):
    try:
        tz = pytz.timezone(TIMEZONE)
        now = datetime.datetime.now(tz).isoformat()
        events_result = calendar_service.events().list(
            calendarId=CALENDAR_ID, timeMin=now, maxResults=int(max_results), singleEvents=True, orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])
        if not events: return "No upcoming events found."
        
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
        if item_type not in VALID_TYPES: item_type = "To-Do Item"
        if category not in VALID_CATEGORIES: category = "General"

        print(f"📝 Adding to schedule: {summary} [{item_type} | {category}]")
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
        return f"Success: Added '{summary}' ({item_type}/{category}) to schedule."
    except Exception as e: return f"Error adding task: {str(e)}"

def update_event(keyword: str, date_str: str = "today", new_start_time: str = None, new_title: str = None):
    try:
        start_iso, end_iso = get_date_range(date_str, days=2)
        if not start_iso: return "Error: Invalid date."

        print(f"🔄 Searching to update '{keyword}' around {date_str}...")
        events_result = calendar_service.events().list(
            calendarId=CALENDAR_ID, timeMin=start_iso, timeMax=end_iso, q=keyword, singleEvents=True
        ).execute()

        events = events_result.get('items', [])
        if not events: return f"Could not find any event matching '{keyword}' on {date_str}."

        target_event = events[0]
        event_id = target_event['id']
        current_summary = target_event.get('summary', 'No Title')
        
        current_start_raw = target_event['start'].get('dateTime', target_event['start'].get('date'))
        current_start_dt = None
        if 'T' in current_start_raw:
            current_start_dt = datetime.datetime.fromisoformat(current_start_raw)
        
        changes = {}
        updated_log = []

        if new_title:
            changes['summary'] = new_title
            updated_log.append(f"Title -> {new_title}")

        if new_start_time and current_start_dt:
            new_dt = parse_smart_time(new_start_time, current_start_dt)
            if new_dt:
                end_dt = new_dt + datetime.timedelta(hours=1)
                changes['start'] = {'dateTime': new_dt.isoformat(), 'timeZone': TIMEZONE}
                changes['end'] = {'dateTime': end_dt.isoformat(), 'timeZone': TIMEZONE}
                updated_log.append(f"Time -> {format_event_time(new_dt.isoformat())}")
            else:
                return f"Error: Could not understand time '{new_start_time}'."

        if not changes: return "Found event, but no changes were understood."

        calendar_service.events().patch(calendarId=CALENDAR_ID, eventId=event_id, body=changes).execute()
        return f"Success: Updated '{current_summary}'. ({', '.join(updated_log)})"

    except Exception as e: return f"Error updating event: {str(e)}"

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
                calendar_service.events().delete(calendarId=CALENDAR_ID, eventId=event['id']).execute()
                deleted_count += 1
                deleted_titles.append(title)
        
        if deleted_count == 0: return f"Found events, but none matched '{keyword}'."
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

tools = [add_to_schedule, check_schedule, list_upcoming_events, update_event, delete_events, send_notification]
tool_map = {
    'add_to_schedule': add_to_schedule,
    'check_schedule': check_schedule,
    'list_upcoming_events': list_upcoming_events, 
    'update_event': update_event,
    'delete_events': delete_events,
    'send_notification': send_notification
}

# --- AI BRAIN (V2.3 - Stability Update) ---
def process_message(user_input, chat_history):
    if user_input.upper().strip() in ["STOP", "CANCEL", "RESET", "END"]:
        return "🛑 Process Stopped."

    # Condensed System Instruction (Saves Tokens & Speed)
    system_instruction = f"""
    You are a receptionist. Manage tasks using: {', '.join(VALID_TYPES)} and {', '.join(VALID_CATEGORIES)}.
    Tools:
    - add_to_schedule: Create events.
    - update_event: Change time/title. Accepts simple times (e.g. "3pm").
    - delete_events: Remove events.
    - list_upcoming_events: Show future events.
    - check_schedule: Show specific day.
    
    Notes:
    - If a tool fails, Report the error. DO NOT retry.
    - Be concise.
    """

    max_retries = 3
    attempts = 0

    while attempts < max_retries:
        try:
            # 1. Enforce Rate Limit (Wait 2s before every call)
            time.sleep(2) 

            model = genai.GenerativeModel(model_name=MODEL_NAME, tools=tools, system_instruction=system_instruction)
            chat = model.start_chat(enable_automatic_function_calling=False)
            
            date_context = f" [System Info: NY Time: {get_current_time()}]"
            augmented_input = user_input + date_context
            
            # 2. Send Message
            response = chat.send_message(augmented_input)
            
            # 3. Process Tool Calls
            function_calls_found = []
            seen_calls = set()

            for part in response.parts:
                if part.function_call:
                    fc = part.function_call
                    signature = (fc.name, json.dumps(dict(fc.args), sort_keys=True))
                    if signature not in seen_calls:
                        function_calls_found.append(fc)
                        seen_calls.add(signature)
            
            if function_calls_found:
                function_responses = []
                all_results_text = []

                for fc in function_calls_found:
                    func_name = fc.name
                    args = dict(fc.args)
                    print(f"🤖 Gemini Request: {func_name} | Args: {args}")
                    
                    if func_name in tool_map:
                        try:
                            result = tool_map[func_name](**args)
                        except Exception as tool_e:
                            result = f"Error executing {func_name}: {str(tool_e)}"
                    else:
                        result = f"Error: Function {func_name} not found."
                    
                    print(f"✅ Tool Result: {result}")
                    all_results_text.append(result)

                    function_responses.append({
                        "function_response": {
                            "name": func_name,
                            "response": {"result": result}
                        }
                    })
                
                # 4. Send Results (Retry on 504/Timeout errors specifically here)
                try:
                    time.sleep(1) # Extra pause before summary
                    final_response = chat.send_message(function_responses)
                    text = final_response.text
                    if not text or len(text.strip()) < 2:
                        return f"✅ Actions completed:\n" + "\n".join(all_results_text)
                    return text
                except (DeadlineExceeded, ServiceUnavailable):
                     # If summary fails, just return the raw results. Don't crash.
                    return f"✅ Actions completed (Summary Unavailable due to Timeout):\n" + "\n".join(all_results_text)
                except Exception:
                    return f"✅ Actions completed:\n" + "\n".join(all_results_text)

            else:
                return response.text

        # 5. Handle Specific Rate Limit / Timeout Errors
        except (ResourceExhausted, DeadlineExceeded, ServiceUnavailable):
            print(f"⚠️ API Limit/Timeout. Switching Key or Retrying... (Attempt {attempts+1})")
            if switch_api_key():
                attempts += 1
                time.sleep(2) # Longer wait on retry
                continue
            else:
                return "⚠️ Error: System is busy or quota exceeded. Please wait 1 minute."
        
        except Exception as e:
            traceback.print_exc()
            return f"⚠️ System Error: {str(e)}"
    
    return "⚠️ Error: Request failed after multiple attempts."