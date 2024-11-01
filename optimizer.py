import gurobipy as gp
from gurobipy import GRB

# TODO
# Define time slot as "xTTTT" where x is a day 1-5 and TTTT is the beginning time of the course
# 

# Sample data
courses = ["Course 1", "Course 2", "Course 3", "Course 4", "Course 5"]
days = 5  # Number of days available
time_slots = 5  # Number of time slots available

# Initialize the score matrix with a base score of 1 for each course and time slot
score_matrix = [[1 for _ in range(time_slots)] for _ in range(len(courses))]

# Chairs' schedule - using specific courses and their corresponding time slots
# (class_idx, time_slot_idx)
chairs_schedule = [(0, 0),  # Course 1 in Time slot 0
                   (1, 2),  # Course 2 in Time slot 2
                   (2, 3),  # Course 3 in Time slot 3
                   (3, 3),  # Course 4 in Time slot 3
                   (4, 3)]  # Course 5 in Time slot 3

# Augment the score matrix with the chair's schedule: set those scores to 10
for class_idx, time_slot_idx in chairs_schedule:
    if class_idx < len(score_matrix) and time_slot_idx < time_slots:  # Ensure indices are valid
        score_matrix[class_idx][time_slot_idx] = 10

# Create a new model
model = gp.Model("Class Scheduling")

# Decision variables: x[i][t] is 1 if course i is scheduled in time slot t, 0 otherwise
x = model.addVars(len(courses), time_slots, vtype=GRB.BINARY, name="x")

# Objective: maximize the total score based on the score matrix
model.setObjective(gp.quicksum(score_matrix[c][t] * x[c, t]
                                 for c in range(len(courses))
                                 for t in range(time_slots)), GRB.MAXIMIZE)

# Constraints:
# 1. Each course must be scheduled in exactly one time slot
for c in range(len(courses)):
    model.addConstr(gp.quicksum(x[c, t] for t in range(time_slots)) == 1,
                    name=f"class_{c}_once")

# 2. No two classes can be scheduled in the same time slot on the same day
for t in range(time_slots):
    model.addConstr(gp.quicksum(x[c, t] for c in range(len(courses))) <= 1,
                    name=f"time_slot_{t}_non_overlap")

# Course Conflict Group Implementation
conflict_group = [(0, 1), (2, 4)]

for course1, course2 in conflict_group:
    for t in range(time_slots):
        model.addConstr(x[course1, t] + x[course2, t] <= 1,
                        name=f"no_overlap_{course1}_{course2}_time{t}")

# Optimize the model
model.optimize()

# Output the results
if model.status == GRB.OPTIMAL:
    print("\nOptimal schedule:")
    for c in range(len(courses)):
        for t in range(time_slots):
            if x[c, t].x > 0.5:  # If variable is selected
                print(f"{courses[c]} is scheduled in timeslot {t}")
    print("\nMaximum Score:", model.objVal)
else:
    print("No optimal solution found.")
