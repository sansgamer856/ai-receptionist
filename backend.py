import os
import datetime
import traceback
import smtplib
from email.mime.text import MIMEText
from typing import Literal

import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content # Crucial for manual responses
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()

# Use the stable model
MODEL_NAME = 'gemini-2.5-flash' 
SPREADSHEET_ID = '1EP_K4RV5djXxtNmV25CwNV5Jk2v6LP89eNixceSKE0I' 
CALENDAR_ID = 'c_fa9eefe809ded84d84f33c8b11369b569f78d88491d6595b5673ec98a6869fb6@group.calendar.google.com' 

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
    return datetime.datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")

# --- TOOL DEFINITIONS ---
def check_schedule(date_str: str = "today"):
    try:
        print(f"👀 Checking schedule for {date_str}...")
        now = datetime.datetime.now()
        if date_str == "today": start = now.replace(hour=0, minute=0, second=0)
        elif date_str == "tomorrow": start = now.replace(hour=0, minute=0, second=0) + datetime.timedelta(days=1)
        else: start = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        
        end = start + datetime.timedelta(days=1)
        
        events_result = calendar_service.events().list(
            calendarId=CALENDAR_ID, timeMin=start.isoformat() + 'Z', timeMax=end.isoformat() + 'Z', singleEvents=True, orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        if not events: return f"No events found for {date_str}."

        text = f"Schedule for {date_str}:\n"
        for event in events:
            text += f"- {event['start'].get('dateTime', event['start'].get('date'))}: {event.get('summary', 'No Title')}\n"
        return text
    except Exception as e: return f"Error: {str(e)}"

def add_to_schedule(summary: str, date_time: str, item_type: str, category: str, notes: str = "", duration_hours: float = 1.0):
    try:
        print(f"📝 Adding to schedule: {summary}")
        start_time = datetime.datetime.fromisoformat(date_time)
        end_time = start_time + datetime.timedelta(hours=duration_hours)
        
        # Calendar
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
        sheets_service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID, range="WeeklyOverhaul!A:F", valueInputOption="USER_ENTERED", body={'values': values}
        ).execute()

        return "Success: Item added to Calendar and Sheets."
    except Exception as e: 
        print(f"❌ Error in add_to_schedule: {e}")
        return f"Error: {str(e)}"

def remove_task(keyword: str, date_str: str = "today"):
    try:
        print(f"🗑️ Attempting to remove task matching: {keyword}")
        schedule_info = check_schedule(date_str)
        # (Simplified logic - in production use IDs)
        # Rerunning list to get IDs
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
        return f"Deleted {deleted} event(s)."
    except Exception as e: return f"Error: {str(e)}"

def send_notification(message: str):
    if not email_user or not email_pass: return "Email not configured."
    try:
        print(f"📧 Sending email...")
        msg = MIMEText(message)
        msg['Subject'] = "Receptionist Alert"
        msg['From'] = email_user
        msg['To'] = email_user
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(email_user, email_pass)
            s.send_message(msg)
        return "Email sent."
    except Exception as e: return f"Email failed: {e}"

# --- REGISTER TOOLS ---
tools = [add_to_schedule, check_schedule, remove_task, send_notification]

# --- AI BRAIN (MANUAL CONTROL) ---
def process_message(user_input, chat_history):
    try:
        # 1. SETUP
        system_instruction = f"You are a receptionist. Current Time: {get_current_time()}. Use tools to modify the schedule."
        model = genai.GenerativeModel(model_name=MODEL_NAME, tools=tools, system_instruction=system_instruction)
        
        # Disable auto-function calling so we can see what happens
        chat = model.start_chat(enable_automatic_function_calling=False)
        
        # 2. SEND MESSAGE
        response = chat.send_message(user_input)
        
        # 3. MANUAL CHECK: DID GEMINI CALL A FUNCTION?
        # We look at the 'parts' of the response
        try:
            function_call = response.candidates[0].content.parts[0].function_call
        except (IndexError, AttributeError):
            function_call = None

        if function_call:
            # 🤖 A Tool was triggered!
            func_name = function_call.name
            args = dict(function_call.args)
            
            print(f"🤖 Gemini Request: {func_name}")
            print(f"📦 Arguments: {args}")

            # Execute Python Code
            result = "Error: Function not found"
            if func_name == "add_to_schedule":
                result = add_to_schedule(**args)
            elif func_name == "check_schedule":
                result = check_schedule(**args)
            elif func_name == "remove_task":
                result = remove_task(**args)
            elif func_name == "send_notification":
                result = send_notification(**args)
            
            print(f"✅ Result: {result}")

            # Send Result Back to Gemini
            # We must construct a specific FunctionResponse object
            function_response_part = content.Part(
                function_response=content.FunctionResponse(
                    name=func_name,
                    response={"result": result}
                )
            )
            
            final_response = chat.send_message([function_response_part])
            return final_response.text

        else:
            # No tool called, just text
            return response.text

    except Exception as e:
        traceback.print_exc()
        return f"⚠️ System Error: {str(e)}"
