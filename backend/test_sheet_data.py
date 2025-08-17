#!/usr/bin/env python3
"""
Test what data is actually in the sheet
"""

import gspread
from config import CRED_PATH, SPREADSHEET_URL

gc = gspread.service_account(filename=CRED_PATH)
ss = gc.open_by_url(SPREADSHEET_URL)

print("="*60)
print("ANALYZING YOUR SHEET")
print("="*60)

total_exercises = 0

for week_num in range(1, 9):
    sheet = ss.worksheet(f"Week {week_num}")
    
    # Get data from columns A through E (Day, Muscle Group, Exercise, Sets, Reps)
    data = sheet.get("A2:E100")  # Skip header, get up to 100 rows
    
    week_exercises = 0
    exercises_list = []
    
    for row in data:
        if len(row) >= 3:  # Need at least columns A, B, C
            exercise = row[2] if len(row) > 2 else ""
            if exercise and exercise.strip():  # If there's an exercise name
                week_exercises += 1
                muscle_group = row[1] if len(row) > 1 else "Unknown"
                sets = row[3] if len(row) > 3 else ""
                reps = row[4] if len(row) > 4 else ""
                exercises_list.append(f"    - {exercise} ({muscle_group}) Sets:{sets} Reps:{reps}")
    
    if week_exercises > 0:
        print(f"\nWeek {week_num}: {week_exercises} exercises")
        for ex in exercises_list[:5]:  # Show first 5
            print(ex)
        if len(exercises_list) > 5:
            print(f"    ... and {len(exercises_list)-5} more")
        total_exercises += week_exercises
    else:
        print(f"\nWeek {week_num}: EMPTY")

print("\n" + "="*60)
print(f"TOTAL EXERCISES ACROSS ALL WEEKS: {total_exercises}")
print("="*60)

if total_exercises == 0:
    print("\n⚠️ NO EXERCISE DATA FOUND!")
    print("Make sure you have exercises entered in Column C")
    print("with muscle groups in Column B")