import os
import datetime
import traceback
import warnings
import streamlit as st
from typing import Literal

import google.generativeai as genai
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

# --- SETUP & CONFIGURATION ---
# Silence warnings about the new SDK version to keep your terminal clean
warnings.simplefilter(action='ignore', category=FutureWarning)

# Load environment variables (API Key)
load_dotenv()

# !!! ACTION REQUIRED: PASTE YOUR ID HERE !!!
SPREADSHEET_ID = '1EP_K4RV5djXxtNmV25CwNV5Jk2v6LP89eNixceSKE0I' 

# !!! ACTION REQUIRED: PASTE YOUR EMAIL HERE !!!
CALENDAR_ID = 'c_fa9eefe809ded84d84f33c8b11369b569f78d88491d6595b5673ec98a6869fb6@group.calendar.google.com' 

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'credentials.json'

# --- AUTHENTICATION ---
# This block automatically detects if we are on the Cloud or Local
try:
    # Attempt to load from Streamlit Secrets (Cloud)
    # We will set this up in Step 4
    service_account_info = st.secrets["gcp_service_account"]
    creds = service_account.Credentials.from_service_account_info(
        service_account_info, scopes=SCOPES
    )
    # Also get the API Key from secrets
    api_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    # If that fails, we are running locally on your laptop
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    api_key = os.getenv("GOOGLE_API_KEY")

# Connect services
sheets_service = build('sheets', 'v4', credentials=creds)
calendar_service = build('calendar', 'v3', credentials=creds)

if not api_key:
    print("❌ Error: API Key not found.")
genai.configure(api_key=api_key)


# --- THE TOOL (THE HANDS) ---
# We define the function with specific "Type Hints" (Literal).
# Gemini reads these hints to know exactly what options are allowed in your dropdowns.
def add_to_schedule(
    summary: str,
    date_time: str,
    item_type: Literal["Assignment", "Meeting", "Research", "Exam", "To-Do Item"],
    category: Literal["Classes", "Combat Robotics", "Rocket Propulsion", "IEEE", "Research", "Personal"],
    notes: str = "",
    duration_hours: float = 1.0
):
    try:
        print(f"⚡ Tool Triggered: Adding '{summary}'...") 
        
        # 1. Add to Google Calendar
        start_time = datetime.datetime.fromisoformat(date_time)
        end_time = start_time + datetime.timedelta(hours=duration_hours)
        
        event = {
            'summary': f"[{category}] {summary}",
            'description': f"Type: {item_type}\nNotes: {notes}",
            'start': {'dateTime': start_time.isoformat(), 'timeZone': 'America/New_York'}, 
            'end': {'dateTime': end_time.isoformat(), 'timeZone': 'America/New_York'},
        }
        
        # Debug print to show exactly where we are writing
        print(f"📅 Attempting to write to Calendar ID: {CALENDAR_ID}")
        
        calendar_service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        print("✅ Calendar write successful.")

        # 2. Add to Google Sheets
        # FIX: Changed date format to MM/DD/YYYY HH:MM
        formatted_date = start_time.strftime("%m/%d/%Y %H:%M")
        
        values = [[formatted_date, summary, item_type, category, notes, False]]
        
        body = {'values': values}
        sheets_service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range="WeeklyOverhaul!A:F", 
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()

        return f"Success: Added '{summary}' to your schedule."

    except Exception as e:
        traceback.print_exc() 
        return f"Error executing tool: {str(e)}"

# --- REGISTER TOOLS ---
# We pass the function object directly. The library handles the JSON conversion.
tools = [add_to_schedule]

# --- AI BRAIN ---
def process_message(user_input):
    try:
        # Initialize Model with the tool
        model = genai.GenerativeModel(model_name='gemma-3-27b-it', tools=tools)
        
        # Start chat with automatic function calling enabled
        chat = model.start_chat(enable_automatic_function_calling=True)
        
        # Send message
        response = chat.send_message(user_input)
        
        # Return the final text (Gemini runs the tool internally now)
        return response.text

    except Exception:
        traceback.print_exc()
        return "⚠️ An error occurred. Check the terminal window for details."




