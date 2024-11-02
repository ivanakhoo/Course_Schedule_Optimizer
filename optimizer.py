import gurobipy as gp
from gurobipy import GRB
import pandas as pd

#TODO
# Course Conflict Group Population


# Load courses from Excel file
file_path = "Course.xlsx" 
data = pd.read_excel(file_path)

# Load specific columns (Courses, Days, BegTime) from the Excel file
data = pd.read_excel(args.file_path, usecols=["Courses", "Days", "BegTime"])

course_schedule = {
    row['Courses']: {
        'day': row['Days'],
        'beg_time': row['BegTime'].strftime('%-I:%M') if row['BegTime'] else '',  # Format to string (e.g., "9", "10", "12:30")
        'time_index': []  # Initialize time_index as an empty list
    }
    for index, row in data.iterrows()
}

# Define time slot mappings using strings for beg_time
time_slot_map = {
    'MWF': {'9:00': 0, '10:00': 1, '11:00': 2},  # Time formatted as "HH:MM"
    'TH': {'9:30': 3, '12:30': 4}                 # Time formatted as "HH:MM"
}

# Iterate through each course in course_schedule and update time_index
for course, details in course_schedule.items():
    day = details['day']
    beg_time = details['beg_time']
    
    # Check if the day matches either 'MWF' or 'TH' and assign time_index if there's a match
    if day in time_slot_map and beg_time in time_slot_map[day]:
        details['time_index'].append(time_slot_map[day][beg_time])

courses = len(course_schedule)

# Define time slots for specific days
time_slots = [
    "MWF 9:00 AM - 9:50 AM",  # MWF
    "MWF 10:00 AM - 10:50 AM", # MWF
    "MWF 11:00 AM - 11:50 PM", # MWF
    "TH 9:30 AM - 10:45 AM",  # TH
    "TH 12:30 PM - 1:45 PM",  # TH
]

# Initialize the score matrix with a base score of 1 for each course and time slot
score_matrix = [[1 for _ in range(len(time_slots))] for _ in range(len(courses))]

chairs_schedule = []

# Create the chairperson schedule based on course_schedule
for course_index, (course, details) in enumerate(course_schedule.items()):
    # Iterate through time_index of each course
    for time_index in details['time_index']:
        # Append (course_index, time_index) to chairs_schedule
        chairs_schedule.append((course_index, time_index))

# Augment the score matrix with the chair's schedule: set those scores to 10
for class_idx, time_slot_idx in chairs_schedule:
    if class_idx < len(score_matrix) and time_slot_idx < len(time_slots):  # Ensure indices are valid
        score_matrix[class_idx][time_slot_idx] = 10

# Create a new model
model = gp.Model("Class Scheduling")

# Decision variables: x[i][t] is 1 if course i is scheduled in time slot t, 0 otherwise
x = model.addVars(len(courses), len(time_slots), vtype=GRB.BINARY, name="x")

# Objective: maximize the total score based on the score matrix
model.setObjective(gp.quicksum(score_matrix[c][t] * x[c, t]
                                 for c in range(len(courses))
                                 for t in range(len(time_slots))), GRB.MAXIMIZE)

# Constraints:
# 1. Each course must be scheduled in exactly one time slot
for c in range(len(courses)):
    model.addConstr(gp.quicksum(x[c, t] for t in range(len(time_slots))) == 1,
                    name=f"class_{c}_once")

# Course Conflict Group Implementation
conflict_group = [(0, 1), (2, 4)]

for course1, course2 in conflict_group:
    for t in range(len(time_slots)):
        model.addConstr(x[course1, t] + x[course2, t] <= 1,
                        name=f"no_overlap_{course1}_{course2}_time{t}")

# Optimize the model
model.optimize()

# Output the results
if model.status == GRB.OPTIMAL:
    print("\nOptimal schedule:")
    for c in range(len(courses)):
        for t in range(len(time_slots)):
            if x[c, t].x > 0.5:  # If variable is selected
                print(f"{courses[c]} is scheduled in timeslot {time_slots[t]}")
    print("\nMaximum Score:", model.objVal)
else:
    print("No optimal solution found.")
