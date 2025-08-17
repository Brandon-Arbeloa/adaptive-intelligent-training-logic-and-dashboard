#!/usr/bin/env python3
"""
Complete Adaptive Logic System
Reads ranges from Logic sheets, resolves to specific values, writes to training sheets
"""

import gspread
from config import CRED_PATH, SPREADSHEET_URL
import math

# ============= RANGE PARSING UTILITIES =============

def parse_range_or_int(s: str):
    """
    Returns (lo:int, hi:int) if s is a range; or (n, n) if s is a single int; or (None, None) if not parseable.
    Accepts hyphen '-' or en dash '–'. Ignores spaces. Rejects obvious dates like '3/5'.
    """
    if not s: return (None, None)
    txt = str(s).strip()
    if "/" in txt:  # looks like a date; not a valid range for our logic
        return (None, None)
    # normalize hyphens
    txt = txt.replace("–", "-")
    # remove spaces around dash
    txt = txt.replace(" - ", "-").replace(" -", "-").replace("- ", "-")
    # simple int?
    if txt.isdigit():
        n = int(txt)
        return (n, n)
    # range?
    if "-" in txt:
        parts = txt.split("-", 1)
        if all(p.strip().isdigit() for p in parts):
            lo = int(parts[0].strip())
            hi = int(parts[1].strip())
            if lo <= hi:
                return (lo, hi)
    return (None, None)

def pick_value_from_range(lo: int, hi: int, week: int, total_weeks: int, mode: str = "progressive"):
    """
    Choose a deterministic target inside [lo, hi].
    mode:
      - 'low'         -> lo
      - 'mid'         -> round midpoint
      - 'high'        -> hi
      - 'progressive' -> ramps from low→high as week increases, clamps into [lo,hi]
    """
    if lo is None or hi is None:
        return None
    if lo == hi:
        return lo
    mode = (mode or "progressive").lower()
    if mode == "low":
        return lo
    if mode == "high":
        return hi
    if mode == "mid":
        return int(round((lo + hi) / 2))
    # progressive: map week 1..total_weeks onto lo..hi
    if total_weeks is None or total_weeks < 1:
        total_weeks = 8
    idx = max(1, min(week, total_weeks))
    frac = (idx - 1) / max(1, (total_weeks - 1))  # 0 at week1, 1 at last week
    val = lo + frac * (hi - lo)
    return int(round(val))

def resolve_final_number(value_str: str, week: int, total_weeks: int, bias: str = "progressive"):
    """
    Turn a rule value string ('4' or '6-8' / '6–8') into the final integer we will write.
    """
    if not value_str:
        return None
    v = value_str.strip()
    # adjustments like +1 / -2 are handled elsewhere
    if v.startswith(("+", "-")) and v[1:].isdigit():
        return v
    lo, hi = parse_range_or_int(v)
    if lo is None:
        # couldn't parse -> return original
        return v
    return pick_value_from_range(lo, hi, week, total_weeks, bias)

# ============= MAIN LOGIC ENGINE =============

class CompleteAdaptiveLogic:
    def __init__(self):
        self.gc = gspread.service_account(filename=CRED_PATH)
        self.ss = self.gc.open_by_url(SPREADSHEET_URL)
        
        self.logic_engine = {}
        self.category_logic = {}
        self.exercise_list = {}
        self.goal_type = "Max Strength"
        self.total_weeks = 8
        
    def load_all_logic(self):
        """Load all logic rules from sheets"""
        print("📚 Loading Adaptive Logic Rules...")
        
        # Load Logic Engine
        try:
            sheet = self.ss.worksheet("Logic Engine")
            data = sheet.get_all_values()
            
            for row in data[1:]:  # Skip header
                if len(row) >= 6:
                    goal = row[0]
                    week = row[1]
                    exercise = row[2]
                    sets = row[3]
                    reps = row[4]
                    rest = row[5]
                    
                    key = f"{exercise}_{week}"
                    self.logic_engine[key] = {
                        'goal': goal,
                        'sets': sets,
                        'reps': reps,
                        'rest': rest
                    }
            
            print(f"  ✅ Loaded {len(self.logic_engine)} exercise-specific rules")
            
        except Exception as e:
            print(f"  ⚠️ Logic Engine: {e}")
        
        # Load CategoryLogic
        try:
            sheet = self.ss.worksheet("CategoryLogic")
            data = sheet.get_all_values()
            
            for row in data[1:]:  # Skip header
                if len(row) >= 6:
                    week = row[0]
                    goal_type = row[1]
                    muscle_group = row[2]
                    sets = row[3]
                    reps = row[4]
                    rest = row[5]
                    
                    key = f"{week}_{goal_type}_{muscle_group}"
                    self.category_logic[key] = {
                        'sets': sets,
                        'reps': reps,
                        'rest': rest
                    }
            
            print(f"  ✅ Loaded {len(self.category_logic)} category rules")
            
        except Exception as e:
            print(f"  ⚠️ CategoryLogic: {e}")
        
        # Load ExerciseList
        try:
            sheet = self.ss.worksheet("ExerciseList")
            data = sheet.get_all_values()
            
            for row in data[1:]:
                if len(row) >= 2:
                    muscle_group = row[0]
                    exercise = row[1]
                    
                    if muscle_group not in self.exercise_list:
                        self.exercise_list[muscle_group] = []
                    self.exercise_list[muscle_group].append(exercise)
            
            total_exercises = sum(len(exs) for exs in self.exercise_list.values())
            print(f"  ✅ Loaded {total_exercises} exercises")
            
        except Exception as e:
            print(f"  ⚠️ ExerciseList: {e}")
        
        # Get goal type from Workout Setup
        try:
            sheet = self.ss.worksheet("Workout Setup")
            data = sheet.get("B2:B2")
            if data and data[0]:
                self.goal_type = data[0][0]
                print(f"  ✅ Goal Type: {self.goal_type}")
        except:
            print(f"  ℹ️ Using default goal: {self.goal_type}")
    
    def get_logic_for_exercise(self, week_num, muscle_group, exercise):
        """Get sets/reps/rest for an exercise (as ranges)"""
        
        # Priority 1: Specific exercise rule
        specific_key = f"{exercise}_{week_num}"
        if specific_key in self.logic_engine:
            rule = self.logic_engine[specific_key]
            return rule['sets'], rule['reps'], rule['rest'], "exercise-specific"
        
        # Priority 2: Category rule
        category_key = f"{week_num}_{self.goal_type}_{muscle_group}"
        if category_key in self.category_logic:
            rule = self.category_logic[category_key]
            return rule['sets'], rule['reps'], rule['rest'], "category"
        
        # Priority 3: Default periodization
        if week_num <= 2:
            return "3", "10-12", "60-90", "default"
        elif week_num <= 4:
            return "4", "8-10", "90-120", "default"
        elif week_num <= 6:
            return "4-5", "6-8", "120-180", "default"
        elif week_num == 7:
            return "3", "3-5", "180-240", "default"
        else:
            return "2-3", "12-15", "60", "default"
    
    def process_all_weeks(self, force=False):
        """Process all weeks and apply adaptive logic"""
        
        print("\n🔧 APPLYING ADAPTIVE LOGIC TO ALL WEEKS")
        print("="*60)
        
        self.load_all_logic()
        
        print("\n📊 Processing each week...")
        
        total_updated = 0
        
        for week_num in range(1, 9):
            try:
                sheet = self.ss.worksheet(f"Week {week_num}")
                data = sheet.get("A2:F100")
                
                if not data:
                    print(f"  Week {week_num}: No data")
                    continue
                
                updates = []
                exercises_processed = 0
                
                for row_idx, row in enumerate(data, start=2):
                    if len(row) < 3:
                        continue
                    
                    day = row[0] if len(row) > 0 else ""
                    muscle_group = row[1] if len(row) > 1 else ""
                    exercise = row[2] if len(row) > 2 else ""
                    existing_sets = row[3] if len(row) > 3 else ""
                    existing_reps = row[4] if len(row) > 4 else ""
                    existing_rest = row[5] if len(row) > 5 else ""
                    
                    # Skip empty exercises
                    if not exercise or exercise == "Exercise":
                        continue
                    
                    # Check if needs update
                    needs_update = (
                        force or 
                        not existing_sets or 
                        not existing_reps or 
                        not existing_rest or
                        existing_sets in ["3-5", "Sets"] or
                        existing_reps in ["3-6", "Reps"]
                    )
                    
                    if needs_update:
                        # Get logic rules (as ranges)
                        sets_range, reps_range, rest_range, source = self.get_logic_for_exercise(
                            week_num, muscle_group, exercise
                        )
                        
                        # Resolve ranges to specific values
                        # Sets: progressive (increase over weeks)
                        # Reps: low (if strength focus) or mid (for consistency)
                        # Rest: mid (stable)
                        
                        sets_final = resolve_final_number(sets_range, week_num, self.total_weeks, "progressive")
                        
                        # Reps bias based on week (strength weeks = lower reps)
                        reps_bias = "low" if week_num >= 5 else "mid"
                        reps_final = resolve_final_number(reps_range, week_num, self.total_weeks, reps_bias)
                        
                        rest_final = resolve_final_number(rest_range, week_num, self.total_weeks, "mid")
                        
                        # Only update if we have valid values
                        if sets_final and (force or not existing_sets or existing_sets in ["3-5", "Sets"]):
                            updates.append({'range': f'D{row_idx}', 'values': [[str(sets_final)]]})
                        
                        if reps_final and (force or not existing_reps or existing_reps in ["3-6", "Reps"]):
                            updates.append({'range': f'E{row_idx}', 'values': [[str(reps_final)]]})
                        
                        if rest_final and (force or not existing_rest):
                            updates.append({'range': f'F{row_idx}', 'values': [[str(rest_final)]]})
                        
                        if updates:
                            exercises_processed += 1
                
                # Apply updates
                if updates:
                    sheet.batch_update(updates)
                    print(f"  Week {week_num}: Updated {exercises_processed} exercises")
                    total_updated += exercises_processed
                else:
                    print(f"  Week {week_num}: No updates needed")
                    
            except Exception as e:
                print(f"  Week {week_num}: Error - {e}")
        
        print("\n" + "="*60)
        print(f"✅ COMPLETE! Updated {total_updated} exercises")
        print("\nYour training program now has:")
        print("  • Specific values (not ranges) for execution")
        print("  • Progressive overload built in")
        print("  • Based on YOUR Logic Engine rules")
        print("  • No Apps Script lag!")

def main():
    import sys
    
    logic = CompleteAdaptiveLogic()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "force":
            print("Force mode: Will overwrite existing values")
            logic.process_all_weeks(force=True)
        elif sys.argv[1] == "test":
            # Test the range parsing
            test_values = ["3-5", "6-8", "10-12", "3", "180-240", "3/5", "3–6"]
            print("Testing range parser:")
            for v in test_values:
                lo, hi = parse_range_or_int(v)
                if lo is not None:
                    for week in [1, 4, 7]:
                        result = pick_value_from_range(lo, hi, week, 8, "progressive")
                        print(f"  '{v}' -> Week {week}: {result}")
                else:
                    print(f"  '{v}' -> Cannot parse")
    else:
        logic.process_all_weeks(force=False)

if __name__ == "__main__":
    main()