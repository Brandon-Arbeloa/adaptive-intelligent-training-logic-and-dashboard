#!/usr/bin/env python3
"""
Fill Sets and Reps based on periodization principles
Week 1-2: Hypertrophy (3 sets, 10-12 reps)
Week 3-4: Strength/Hypertrophy (4 sets, 8-10 reps)  
Week 5-6: Strength (4-5 sets, 6-8 reps)
Week 7: Peak (3 sets, 3-5 reps)
Week 8: Deload (2-3 sets, 12-15 reps)
"""

import gspread
from config import CRED_PATH, SPREADSHEET_URL

def get_periodization(week_num):
    """Get sets, reps, and rest based on week number"""
    if week_num <= 2:
        return "3", "10-12", "60-90"
    elif week_num <= 4:
        return "4", "8-10", "90-120"
    elif week_num <= 6:
        return "4-5", "6-8", "120-180"
    elif week_num == 7:
        return "3", "3-5", "180-240"
    else:  # Week 8 - deload
        return "2-3", "12-15", "60"

def fill_sets_reps():
    gc = gspread.service_account(filename=CRED_PATH)
    ss = gc.open_by_url(SPREADSHEET_URL)
    
    print("🔄 FILLING SETS/REPS BASED ON PERIODIZATION")
    print("="*60)
    
    for week_num in range(1, 9):
        sheet = ss.worksheet(f"Week {week_num}")
        sets, reps, rest = get_periodization(week_num)
        
        print(f"\nWeek {week_num}: Sets={sets}, Reps={reps}, Rest={rest}s")
        
        # Get all data to find exercises
        data = sheet.get("A2:F100")
        
        updates = []
        exercises_filled = 0
        
        for row_idx, row in enumerate(data, start=2):
            if len(row) >= 3:
                exercise = row[2] if len(row) > 2 else ""
                
                if exercise and exercise.strip():  # Has exercise
                    current_sets = row[3] if len(row) > 3 else ""
                    current_reps = row[4] if len(row) > 4 else ""
                    current_rest = row[5] if len(row) > 5 else ""
                    
                    # Only fill if empty
                    if not current_sets:
                        updates.append({'range': f'D{row_idx}', 'values': [[sets]]})
                    if not current_reps:
                        updates.append({'range': f'E{row_idx}', 'values': [[reps]]})
                    if not current_rest:
                        updates.append({'range': f'F{row_idx}', 'values': [[rest]]})
                    
                    if not current_sets or not current_reps or not current_rest:
                        exercises_filled += 1
        
        # Batch update
        if updates:
            sheet.batch_update(updates)
            print(f"  ✅ Filled {exercises_filled} exercises")
        else:
            print(f"  ℹ️ No updates needed")
    
    print("\n" + "="*60)
    print("✅ PERIODIZATION COMPLETE!")
    print("Now run backend_rotation.py to analyze rotation needs")

if __name__ == "__main__":
    fill_sets_reps()