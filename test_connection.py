#!/usr/bin/env python3
"""
Test Google Sheets connection
"""

import gspread
import json

# Load credentials from the secrets file
def test_connection():
    with open('.streamlit/secrets.toml', 'r') as f:
        content = f.read()
    
    # Parse the TOML manually (simple parsing)
    lines = content.split('\n')
    creds = {}
    for line in lines:
        if '=' in line and not line.startswith('['):
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip().strip('"')
            # Handle multiline private key
            if key == 'private_key':
                value = value.replace('\\n', '\n')
            creds[key] = value
    
    print("Testing Google Sheets connection...")
    print(f"Using service account: {creds.get('client_email')}")
    
    try:
        # Test connection
        gc = gspread.service_account_from_dict(creds)
        print("✅ Service account authentication successful!")
        
        # Test opening the specific sheet
        SPREADSHEET_URL = 'https://docs.google.com/spreadsheets/d/1Js2s7s95miuUzdn44guWnGuML2kxYzN3kG_jsEdWu68/edit'
        print(f"Attempting to open sheet: {SPREADSHEET_URL}")
        ss = gc.open_by_url(SPREADSHEET_URL)
        print("✅ Successfully opened the Google Sheet!")
        
        # List all worksheets
        worksheets = ss.worksheets()
        print(f"Available worksheets: {[ws.title for ws in worksheets]}")
        
        # Test reading a worksheet
        sheet = ss.worksheet("Week 1")
        data = sheet.get_all_values()
        print(f"✅ Successfully read Week 1 sheet! Found {len(data)} rows.")
        
        if len(data) > 1:
            print(f"Headers: {data[0]}")
            print(f"First data row: {data[1] if len(data) > 1 else 'No data'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection()
