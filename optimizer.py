import gurobipy as gp
from gurobipy import GRB
import pandas as pd

# Load courses from Excel file
file_path = "CourseOptimizerExcel.xlsx"

# Load specific columns (Courses, Days, BegTime) from the Excel file
data = pd.read_excel(file_path, usecols=["Courses", "Days", "BegTime"])

# Dictionary with courses as keys, with each course having a dictionary filled with days, beginning times, and time index
course_schedule = {
    row['Courses']: {
        'day': row['Days'],
        'beg_time': row['BegTime'].strftime('%-I:%M') if row['BegTime'] else '',  # Format to string
        'time_index': []  # Initialize time_index as an empty list
    }
    for index, row in data.iterrows()
}

# Define time slot mappings using strings for beg_time
time_slot_map = {
    'MWF': {'9:00': 0, '10:00': 1, '11:00': 2},  # Time formatted as "HH:MM"
    'TH': {'9:30': 3, '12:30': 4}                 # Time formatted as "HH:MM"
}

# Update time_index for each course
for course, details in course_schedule.items():
    day = details['day']
    beg_time = details['beg_time']
    
    # Check if the day matches either 'MWF' or 'TH' and assign time_index if there's a match
    if day in time_slot_map and beg_time in time_slot_map[day]:
        details['time_index'].append(time_slot_map[day][beg_time])

# Define time slots for specific days
time_slots = [
    "MWF 9:00 AM - 9:50 AM",  # Time Index 0
    "MWF 10:00 AM - 10:50 AM", # Time Index 1
    "MWF 11:00 AM - 11:50 AM", # Time Index 2
    "TH 9:30 AM - 10:45 AM",  # Time Index 3
    "TH 12:30 PM - 1:45 PM",  # Time Index 4
]

# Initialize the score matrix with 1
score_matrix = [[1 for _ in range(len(time_slots))] for _ in range(len(course_schedule))]

chairs_schedule = []

# Chairs schedule - create the chairperson schedule based on course_schedule
for course_index, (course, details) in enumerate(course_schedule.items()):
    # Iterate through time_index of each course
    for time_index in details['time_index']:
        # Append (course_index, time_index) to chairs_schedule
        chairs_schedule.append((course_index, time_index))

# Set score for chair's schedule to 10
for class_idx, time_slot_idx in chairs_schedule:
    if class_idx < len(score_matrix) and time_slot_idx < len(time_slots):  # Ensure indices are valid
        score_matrix[class_idx][time_slot_idx] = 10

# Create a new model
model = gp.Model("Class Scheduling")

# Decision variables: x[i][t] is 1 if course i is scheduled in time slot t, 0 otherwise
x = model.addVars(len(course_schedule), len(time_slots), vtype=GRB.BINARY, name="x")

# Objective: maximize the total score based on the score matrix
model.setObjective(gp.quicksum(score_matrix[c][t] * x[c, t]
                                 for c in range(len(course_schedule))
                                 for t in range(len(time_slots))), GRB.MAXIMIZE)

# Constraints:
# Each course must be scheduled in exactly one time slot
for c in range(len(course_schedule)):
    model.addConstr(gp.quicksum(x[c, t] for t in range(len(time_slots))) == 1,
                    name=f"class_{c}_once")

# Conflict Group Implementation
conflict_group = [
    (0, 6),  
    (2, 4),
    (6, 7)
]

# Courses in the same conflict group may not be scheduled in the same time slot
for course1, course2 in conflict_group:
    for t in range(len(time_slots)):
            model.addConstr(x[course1, t] + x[course2, t] <= 1,
                            name=f"course_conflict_between_{course1}_{course2}_time{t}")

# Time slots that Course 6 is allowed to move to
allowed_time_slots_for_course_6 = [0,2,4]

# Course 6 may only move into one of the time slots included in allowed_time_slots_for_course_6
for t in range(len(time_slots)):
    if t not in allowed_time_slots_for_course_6:
        model.addConstr(x[6,t] == 0, name=f"course_6_excluded_slot_{t}")

# Optimize the model
model.optimize()

# Output the results
if model.status == GRB.OPTIMAL:
    print("\nOptimal schedule:")
    for c in range(len(course_schedule)):
        for t in range(len(time_slots)):
            if x[c, t].x > 0.5:  
                course_name = list(course_schedule.keys())[c]
                print(f"{course_name} is scheduled in timeslot {time_slots[t]}")
    print("\nMaximum Score:", model.objVal)
else:
    print("No optimal solution found.")
