#!/usr/bin/env python3
"""
Debug script to see the actual structure of Logic sheets
"""

import gspread
from config import CRED_PATH, SPREADSHEET_URL

gc = gspread.service_account(filename=CRED_PATH)
ss = gc.open_by_url(SPREADSHEET_URL)

print("="*60)
print("DEBUGGING LOGIC SHEETS STRUCTURE")
print("="*60)

# Check Logic Engine
print("\n📊 LOGIC ENGINE:")
print("-"*40)
try:
    sheet = ss.worksheet("Logic Engine")
    data = sheet.get("A1:J5")  # Get first 5 rows, 10 columns
    
    for i, row in enumerate(data, 1):
        print(f"Row {i}: {row}")
except Exception as e:
    print(f"Error: {e}")

# Check CategoryLogic
print("\n📋 CATEGORY LOGIC:")
print("-"*40)
try:
    sheet = ss.worksheet("CategoryLogic")
    data = sheet.get("A1:J5")
    
    for i, row in enumerate(data, 1):
        print(f"Row {i}: {row}")
except Exception as e:
    print(f"Error: {e}")

# Check ExerciseList
print("\n💪 EXERCISE LIST:")
print("-"*40)
try:
    sheet = ss.worksheet("ExerciseList")
    data = sheet.get("A1:F10")  # First 10 rows
    
    for i, row in enumerate(data, 1):
        print(f"Row {i}: {row}")
except Exception as e:
    print(f"Error: {e}")

# Check Adaptive Logic
print("\n🧠 ADAPTIVE LOGIC:")
print("-"*40)
try:
    sheet = ss.worksheet("Adaptive Logic")
    data = sheet.get("A1:J5")
    
    for i, row in enumerate(data, 1):
        print(f"Row {i}: {row}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*60)
print("Now I can see the actual column structure!")