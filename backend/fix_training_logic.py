#!/usr/bin/env python3
"""
Proper Adaptive Logic Engine that reads YOUR actual system
"""

import gspread
from config import CRED_PATH, SPREADSHEET_URL

class ProperAdaptiveLogic:
    def __init__(self):
        self.gc = gspread.service_account(filename=CRED_PATH)
        self.ss = self.gc.open_by_url(SPREADSHEET_URL)
        
        # Store the logic rules
        self.logic_engine = {}  # Specific exercise progressions
        self.category_logic = {}  # Goal/muscle group rules
        self.exercise_list = {}  # Exercise database
        self.adaptive_rules = {}  # RPE adjustments
        
    def load_all_logic(self):
        """Load all logic sheets properly"""
        
        print("📚 Loading YOUR Actual Logic System...")
        
        # Load Logic Engine (specific exercise progressions)
        try:
            sheet = self.ss.worksheet("Logic Engine")
            data = sheet.get_all_values()
            
            for row in data[1:]:  # Skip header
                if len(row) >= 7:
                    goal = row[0]
                    week = row[1]
                    exercise = row[2]
                    sets = row[3]
                    reps = row[4]
                    rest = row[5]
                    load_pattern = row[6] if len(row) > 6 else ""
                    
                    key = f"{exercise}_{week}"
                    self.logic_engine[key] = {
                        'goal': goal,
                        'sets': sets,
                        'reps': reps,
                        'rest': rest,
                        'load_pattern': load_pattern
                    }
            
            print(f"  ✅ Loaded {len(self.logic_engine)} specific exercise progressions")
            
        except Exception as e:
            print(f"  ❌ Logic Engine error: {e}")
        
        # Load CategoryLogic (muscle group rules by week/goal)
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
                    load_pattern = row[6] if len(row) > 6 else ""
                    
                    key = f"{week}_{goal_type}_{muscle_group}"
                    self.category_logic[key] = {
                        'sets': sets,
                        'reps': reps,
                        'rest': rest,
                        'load_pattern': load_pattern
                    }
            
            print(f"  ✅ Loaded {len(self.category_logic)} category rules")
            
        except Exception as e:
            print(f"  ❌ CategoryLogic error: {e}")
        
        # Load ExerciseList
        try:
            sheet = self.ss.worksheet("ExerciseList")
            data = sheet.get_all_values()
            
            for row in data[1:]:  # Skip header
                if len(row) >= 2:
                    muscle_group = row[0]
                    exercise = row[1]
                    
                    if muscle_group not in self.exercise_list:
                        self.exercise_list[muscle_group] = []
                    self.exercise_list[muscle_group].append(exercise)
            
            total_exercises = sum(len(exs) for exs in self.exercise_list.values())
            print(f"  ✅ Loaded {total_exercises} exercises across {len(self.exercise_list)} muscle groups")
            
        except Exception as e:
            print(f"  ❌ ExerciseList error: {e}")
    
    def get_logic_for_exercise(self, week_num, muscle_group, exercise, goal_type="Max Strength"):
        """
        Get the proper sets/reps/rest for an exercise
        Priority: Specific exercise > Category > Default
        """
        
        # 1. Check for specific exercise progression
        specific_key = f"{exercise}_{week_num}"
        if specific_key in self.logic_engine:
            rule = self.logic_engine[specific_key]
            return rule['sets'], rule['reps'], rule['rest']
        
        # 2. Check category logic
        category_key = f"{week_num}_{goal_type}_{muscle_group}"
        if category_key in self.category_logic:
            rule = self.category_logic[category_key]
            return rule['sets'], rule['reps'], rule['rest']
        
        # 3. Fallback to sensible defaults based on week
        if week_num <= 2:
            return "3", "10-12", "60"
        elif week_num <= 4:
            return "4", "8-10", "90"
        elif week_num <= 6:
            return "4", "6-8", "120"
        elif week_num == 7:
            return "3", "3-5", "180"
        else:  # Week 8 - deload
            return "2", "12-15", "60"
    
    def fix_all_sets_reps(self):
        """Fix the incorrect 3-5 sets and 3-6 reps with proper values"""
        
        print("\n🔧 FIXING INCORRECT SETS/REPS")
        print("="*60)
        
        # First load the logic
        self.load_all_logic()
        
        # Get goal type from Workout Setup if it exists
        goal_type = "Max Strength"  # Default
        try:
            setup_sheet = self.ss.worksheet("Workout Setup")
            setup_data = setup_sheet.get("B2")  # Assuming goal is in B2
            if setup_data:
                goal_type = setup_data[0][0] if setup_data else "Max Strength"
                print(f"  📎 Goal Type: {goal_type}")
        except:
            print(f"  📎 Using default goal: {goal_type}")
        
        print("\n📊 Processing each week...")
        
        total_fixed = 0
        
        for week_num in range(1, 9):
            try:
                sheet = self.ss.worksheet(f"Week {week_num}")
                data = sheet.get("A2:F100")
                
                if not data:
                    continue
                
                updates = []
                exercises_to_fix = 0
                
                for row_idx, row in enumerate(data, start=2):
                    if len(row) < 3:
                        continue
                    
                    muscle_group = row[1] if len(row) > 1 else ""
                    exercise = row[2] if len(row) > 2 else ""
                    current_sets = row[3] if len(row) > 3 else ""
                    current_reps = row[4] if len(row) > 4 else ""
                    current_rest = row[5] if len(row) > 5 else ""
                    
                    # Skip empty rows or header-like rows
                    if not exercise or exercise == "Exercise":
                        continue
                    
                    # Check if it has the wrong values (3-5 sets, 3-6 reps)
                    needs_fix = (current_sets == "3-5" or current_reps == "3-6" or 
                                current_sets == "Sets" or current_reps == "Reps")
                    
                    if needs_fix:
                        # Get proper values from logic
                        proper_sets, proper_reps, proper_rest = self.get_logic_for_exercise(
                            week_num, muscle_group, exercise, goal_type
                        )
                        
                        updates.append({'range': f'D{row_idx}', 'values': [[proper_sets]]})
                        updates.append({'range': f'E{row_idx}', 'values': [[proper_reps]]})
                        updates.append({'range': f'F{row_idx}', 'values': [[proper_rest]]})
                        
                        exercises_to_fix += 1
                
                # Apply updates
                if updates:
                    sheet.batch_update(updates)
                    print(f"  Week {week_num}: Fixed {exercises_to_fix} exercises")
                    total_fixed += exercises_to_fix
                else:
                    print(f"  Week {week_num}: No fixes needed")
                    
            except Exception as e:
                print(f"  Week {week_num}: Error - {e}")
        
        print("\n" + "="*60)
        print(f"✅ FIXED {total_fixed} EXERCISES!")
        print("\nYour training program now has PROPER sets/reps/rest")
        print("Based on YOUR Logic Engine and CategoryLogic rules!")
        
    def show_sample_logic(self):
        """Show a sample of what logic was loaded"""
        
        self.load_all_logic()
        
        print("\n📋 SAMPLE OF YOUR LOGIC RULES")
        print("="*60)
        
        print("\n🎯 Specific Exercise Progressions (Logic Engine):")
        for key, rule in list(self.logic_engine.items())[:5]:
            exercise, week = key.rsplit('_', 1)
            print(f"  {exercise} Week {week}: {rule['sets']} sets × {rule['reps']} reps, {rule['rest']}s rest")
        
        print("\n💪 Category Rules (by Week/Goal/Muscle):")
        for key, rule in list(self.category_logic.items())[:5]:
            week, goal, muscle = key.split('_', 2)
            print(f"  Week {week} {goal} {muscle}: {rule['sets']} sets × {rule['reps']} reps")
        
        print("\n📊 Exercise Database:")
        for muscle, exercises in list(self.exercise_list.items())[:3]:
            print(f"  {muscle}: {len(exercises)} exercises")

def main():
    logic = ProperAdaptiveLogic()
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "show":
        logic.show_sample_logic()
    else:
        logic.fix_all_sets_reps()

if __name__ == "__main__":
    main()