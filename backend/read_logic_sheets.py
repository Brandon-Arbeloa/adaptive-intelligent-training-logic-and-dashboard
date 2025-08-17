#!/usr/bin/env python3
"""
Read the Logic Engine, Adaptive Logic, and CategoryLogic sheets
to understand the actual intelligence of the system
"""

import gspread
from config import CRED_PATH, SPREADSHEET_URL

gc = gspread.service_account(filename=CRED_PATH)
ss = gc.open_by_url(SPREADSHEET_URL)

print("="*60)
print("READING YOUR ADAPTIVE LOGIC SYSTEM")
print("="*60)

# Check Logic Engine
try:
    logic_engine = ss.worksheet("Logic Engine")
    print("\n📊 LOGIC ENGINE SHEET:")
    print("-"*40)
    data = logic_engine.get("A1:Z10")  # Get first 10 rows, all columns
    for i, row in enumerate(data[:5], 1):
        if any(row):
            print(f"Row {i}: {row[:8]}")  # First 8 columns
except Exception as e:
    print(f"Logic Engine not found: {e}")

# Check Adaptive Logic
try:
    adaptive = ss.worksheet("Adaptive Logic")
    print("\n🧠 ADAPTIVE LOGIC SHEET:")
    print("-"*40)
    data = adaptive.get("A1:Z10")
    for i, row in enumerate(data[:5], 1):
        if any(row):
            print(f"Row {i}: {row[:8]}")
except Exception as e:
    print(f"Adaptive Logic not found: {e}")

# Check CategoryLogic
try:
    category = ss.worksheet("CategoryLogic")
    print("\n📋 CATEGORY LOGIC SHEET:")
    print("-"*40)
    data = category.get("A1:Z10")
    for i, row in enumerate(data[:5], 1):
        if any(row):
            print(f"Row {i}: {row[:8]}")
except Exception as e:
    print(f"CategoryLogic not found: {e}")

# Check ExerciseList for categories
try:
    exercise_list = ss.worksheet("ExerciseList")
    print("\n💪 EXERCISE LIST (with categories):")
    print("-"*40)
    data = exercise_list.get("A1:F20")  # Get first 20 exercises
    
    # Show headers
    if data:
        print(f"Headers: {data[0]}")
        print("\nSample exercises with their categories:")
        for row in data[1:11]:  # Show 10 examples
            if any(row):
                print(f"  {row}")
except Exception as e:
    print(f"ExerciseList not found: {e}")

print("\n" + "="*60)
print("Now I can see your actual logic system!")
print("="*60)