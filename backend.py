import os
import datetime
import traceback
import smtplib
import time
from email.mime.text import MIMEText

import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted 
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()

# MODEL: Updated to the latest fast model
# If you have specific access to 'gemini-3-flash-preview', change this string.
MODEL_NAME = 'gemini-3.0-flash-preview' 

# IDs
SPREADSHEET_ID = '1EP_K4RV5djXxtNmV25CwNV5Jk2v6LP89eNixceSKE0I'
CALENDAR_ID = 'c_fa9eefe809ded84d84f33c8b11369b569f78d88491d6595b5673ec98a6869fb6@group.calendar.google.com'
SHEET_RANGE = 'WeeklyOverhaul!A:F'

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'credentials.json'

# --- KEY ROTATION SYSTEM ---
api_keys = []
current_key_index = 0

# 1. Load keys from Streamlit Secrets or .env
try:
    import streamlit as st
    # Check for keys named API_KEY_1, API_KEY_2, etc.
    i = 1
    while True:
        key = st.secrets.get(f"API_KEY_{i}")
        if not key: break
        api_keys.append(key)
        i += 1
    
    # Fallback to single key if numbered ones aren't found
    if not api_keys and "GOOGLE_API_KEY" in st.secrets:
        api_keys.append(st.secrets["GOOGLE_API_KEY"])

    # Load Service Account
    if "gcp_service_account" in st.secrets:
        creds = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=SCOPES
        )
        email_user = st.secrets.get("EMAIL_SENDER")
        email_pass = st.secrets.get("EMAIL_PASSWORD")
    else:
        raise Exception("Local run")

except Exception:
    # Local .env fallback
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
    raise ValueError("❌ No API Keys found! Please set API_KEY_1, API_KEY_2 etc. in secrets.")

print(f"🔑 Loaded {len(api_keys)} API Keys. Starting with Key #1.")
genai.configure(api_key=api_keys[0])

# Google Services
sheets_service = build('sheets', 'v4', credentials=creds)
calendar_service = build('calendar', 'v3', credentials=creds)


# --- HELPER FUNCTIONS ---
def switch_api_key():
    """Switches to the next available API key."""
    global current_key_index
    if len(api_keys) <= 1:
        print("⚠️ Quota hit, but only 1 key available. Cannot switch.")
        return False
    
    current_key_index = (current_key_index + 1) % len(api_keys)
    new_key = api_keys[current_key_index]
    print(f"🔄 Quota exceeded. Switching to API Key #{current_key_index + 1}...")
    genai.configure(api_key=new_key)
    return True

def get_current_time():
    return datetime.datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")

# --- TOOLS ---
def check_schedule(date_str: str = "today"):
    try:
        print(f"👀 Checking schedule for {date_str}...")
        now = datetime.datetime.now()
        if date_str.lower() == "today":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif date_str.lower() == "tomorrow":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
        else:
            try: start = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            except: return "Error: Date must be YYYY-MM-DD, 'today', or 'tomorrow'."
        
        end = start + datetime.timedelta(days=1)
        events_result = calendar_service.events().list(
            calendarId=CALENDAR_ID, timeMin=start.isoformat() + 'Z', timeMax=end.isoformat() + 'Z', singleEvents=True, orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        if not events: return f"No events found for {date_str}."

        text = f"Schedule for {date_str}:\n"
        for event in events:
            start_t = event['start'].get('dateTime', event['start'].get('date'))
            text += f"- {start_t}: {event.get('summary', 'No Title')}\n"
        return text
    except Exception as e: return f"Error checking schedule: {str(e)}"

def add_to_schedule(summary: str, date_time: str, item_type: str, category: str, notes: str = "", duration_hours: float = 1.0):
    try:
        print(f"📝 Adding to schedule: {summary}")
        start_time = datetime.datetime.fromisoformat(date_time)
        end_time = start_time + datetime.timedelta(hours=duration_hours)
        
        event = {
            'summary': f"[{category}] {summary}",
            'description': f"Type: {item_type}\nNotes: {notes}",
            'start': {'dateTime': start_time.isoformat(), 'timeZone': 'America/New_York'},
            'end': {'dateTime': end_time.isoformat(), 'timeZone': 'America/New_York'},
        }
        calendar_service.events().insert(calendarId=CALENDAR_ID, body=event).execute()

        formatted_date = start_time.strftime("%m/%d/%Y %H:%M")
        values = [[formatted_date, summary, item_type, category, notes, False]]
        sheets_service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID, range=SHEET_RANGE, valueInputOption="USER_ENTERED", body={'values': values}
        ).execute()

        return f"Success: Added '{summary}' to schedule."
    except Exception as e: return f"Error adding task: {str(e)}"

def remove_task(keyword: str, date_str: str = "today"):
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

tools = [add_to_schedule, check_schedule, remove_task, send_notification]
tool_map = {
    'add_to_schedule': add_to_schedule,
    'check_schedule': check_schedule,
    'remove_task': remove_task,
    'send_notification': send_notification
}

# --- AI BRAIN (WITH ROTATION LOGIC) ---
def process_message(user_input, chat_history):
    max_retries = len(api_keys) + 1  # Try every key at least once
    attempts = 0

    while attempts < max_retries:
        try:
            # 1. Setup Model
            system_instruction = f"You are a helpful receptionist. Use tools to manage the schedule."
            model = genai.GenerativeModel(model_name=MODEL_NAME, tools=tools, system_instruction=system_instruction)
            chat = model.start_chat(enable_automatic_function_calling=False)
            
            # 2. Inject Date
            date_context = f" [System Info: The current date and time is {get_current_time()}]"
            augmented_input = user_input + date_context
            
            # 3. Send Message
            response = chat.send_message(augmented_input)
            
            # 4. Handle Response (Manual Dispatch)
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

        except ResourceExhausted:
            # ⚠️ 429 ERROR CAUGHT HERE
            print("⚠️ API Quota Exceeded!")
            if switch_api_key():
                attempts += 1
                time.sleep(1) # Brief pause before retry
                continue # Restart the loop with the new key
            else:
                return "⚠️ Error: All API keys have exhausted their quota."
        
        except Exception as e:
            traceback.print_exc()
            return f"⚠️ System Error: {str(e)}"
    
    return "⚠️ Error: Request failed after trying all keys."