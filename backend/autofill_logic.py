#!/usr/bin/env python3
"""
Port of the original Apps Script auto-fill logic
Fills Sets/Reps/Rest based on week and muscle group
WITHOUT the lag of onEdit()
"""

import gspread
from config import CRED_PATH, SPREADSHEET_URL
import time

def get_sets_reps_rest(week_num, muscle_group, exercise):
    """
    Calculate sets, reps, rest based on the original Apps Script logic
    This replaces the onEdit() auto-fill functionality
    """
    
    # Base logic from original Apps Script
    if week_num <= 2:
        # Weeks 1-2: Volume/Hypertrophy phase
        sets = "3"
        reps = "10-12"
        rest = "60-90"
    elif week_num <= 4:
        # Weeks 3-4: Strength/Hypertrophy
        sets = "4"
        reps = "8-10"
        rest = "90-120"
    elif week_num <= 6:
        # Weeks 5-6: Strength phase
        sets = "4-5"
        reps = "6-8"
        rest = "120-180"
    elif week_num == 7:
        # Week 7: Peak/Intensity
        sets = "3"
        reps = "3-5"
        rest = "180-240"
    else:
        # Week 8: Deload
        sets = "2-3"
        reps = "12-15"
        rest = "60"
    
    # Adjust based on muscle group (from original logic)
    if muscle_group in ['Arms', 'Calves', 'Abs', 'Core']:
        # Smaller muscle groups - more reps, less rest
        if week_num <= 6:
            reps = "12-15"
            rest = "60"
    elif muscle_group in ['Back', 'Legs', 'Glutes_Hamstrings']:
        # Large muscle groups - may need more rest
        if week_num >= 5:
            rest = "180-240"
    
    # Exercise-specific adjustments (from original)
    if 'Deadlift' in exercise or 'Squat' in exercise:
        # Heavy compounds need more rest
        rest = "180-240" if week_num <= 6 else "120"
    elif 'Curl' in exercise or 'Raise' in exercise or 'Fly' in exercise:
        # Isolation exercises
        if week_num <= 6:
            sets = "3"
            reps = "12-15"
            rest = "60"
    
    return sets, reps, rest

def auto_fill_training_data():
    """
    Main function to auto-fill all weeks with proper sets/reps/rest
    Replaces the laggy onEdit() from Apps Script
    """
    
    gc = gspread.service_account(filename=CRED_PATH)
    ss = gc.open_by_url(SPREADSHEET_URL)
    
    print("🔄 AUTO-FILLING TRAINING DATA")
    print("="*60)
    print("This replaces the laggy Apps Script onEdit()")
    print()
    
    total_updates = 0
    
    for week_num in range(1, 9):
        try:
            sheet = ss.worksheet(f"Week {week_num}")
            print(f"\n📊 Processing Week {week_num}...")
            
            # Get all data from the sheet
            data = sheet.get("A2:F100")  # Day, Muscle Group, Exercise, Sets, Reps, Rest
            
            if not data:
                print(f"  ⚠️ No data in Week {week_num}")
                continue
            
            updates = []
            row_count = 0
            
            for row_idx, row in enumerate(data, start=2):
                # Need at least muscle group and exercise
                if len(row) < 3:
                    continue
                
                muscle_group = row[1] if len(row) > 1 else ""
                exercise = row[2] if len(row) > 2 else ""
                current_sets = row[3] if len(row) > 3 else ""
                current_reps = row[4] if len(row) > 4 else ""
                current_rest = row[5] if len(row) > 5 else ""
                
                # Skip if no exercise
                if not exercise or not exercise.strip():
                    continue
                
                # Calculate what should be there
                sets, reps, rest = get_sets_reps_rest(week_num, muscle_group, exercise)
                
                # Only update if empty
                if not current_sets:
                    updates.append({
                        'range': f'D{row_idx}',
                        'values': [[sets]]
                    })
                    
                if not current_reps:
                    updates.append({
                        'range': f'E{row_idx}',
                        'values': [[reps]]
                    })
                    
                if not current_rest:
                    updates.append({
                        'range': f'F{row_idx}',
                        'values': [[rest]]
                    })
                
                if not current_sets or not current_reps or not current_rest:
                    row_count += 1
            
            # Batch update all at once (faster than individual updates)
            if updates:
                sheet.batch_update(updates)
                print(f"  ✅ Updated {row_count} exercises ({len(updates)} cells)")
                total_updates += len(updates)
            else:
                print(f"  ℹ️ All exercises already have sets/reps/rest")
                
        except Exception as e:
            print(f"  ❌ Error processing Week {week_num}: {e}")
    
    print("\n" + "="*60)
    print(f"✅ AUTO-FILL COMPLETE!")
    print(f"   Total cells updated: {total_updates}")
    print("\nYour training data now has proper sets/reps/rest")
    print("WITHOUT the Apps Script lag!")
    print("\nNext: Run backend_rotation.py for rotation analysis")

def monitor_and_autofill():
    """
    Monitor mode - watches for changes and auto-fills
    Like onEdit() but runs externally
    """
    
    gc = gspread.service_account(filename=CRED_PATH)
    ss = gc.open_by_url(SPREADSHEET_URL)
    
    print("👁️ MONITORING MODE")
    print("="*60)
    print("Watching for new exercises to auto-fill sets/reps/rest")
    print("Press Ctrl+C to stop")
    print()
    
    last_state = {}
    
    while True:
        try:
            for week_num in range(1, 9):
                sheet = ss.worksheet(f"Week {week_num}")
                
                # Get current data
                data = sheet.get("B2:F20")  # Just check first 20 rows for efficiency
                
                # Create a simple hash of the data
                data_str = str(data)
                
                # Check if changed
                if last_state.get(f"Week{week_num}") != data_str:
                    print(f"🔄 Change detected in Week {week_num}")
                    
                    # Process the changes
                    updates = []
                    for row_idx, row in enumerate(data, start=2):
                        if len(row) >= 2:
                            muscle_group = row[0] if len(row) > 0 else ""
                            exercise = row[1] if len(row) > 1 else ""
                            current_sets = row[2] if len(row) > 2 else ""
                            current_reps = row[3] if len(row) > 3 else ""
                            current_rest = row[4] if len(row) > 4 else ""
                            
                            if exercise and not current_sets:
                                sets, reps, rest = get_sets_reps_rest(week_num, muscle_group, exercise)
                                
                                if not current_sets:
                                    updates.append({'range': f'D{row_idx}', 'values': [[sets]]})
                                if not current_reps:
                                    updates.append({'range': f'E{row_idx}', 'values': [[reps]]})
                                if not current_rest:
                                    updates.append({'range': f'F{row_idx}', 'values': [[rest]]})
                    
                    if updates:
                        sheet.batch_update(updates)
                        print(f"  ✅ Auto-filled {len(updates)} cells")
                    
                    last_state[f"Week{week_num}"] = data_str
            
            time.sleep(5)  # Check every 5 seconds
            
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped")
            break
        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "monitor":
        monitor_and_autofill()
    else:
        auto_fill_training_data()