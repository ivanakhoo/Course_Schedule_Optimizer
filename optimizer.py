import gurobipy as gp
from gurobipy import GRB

# Sample data (classes x days x time slots)
num_classes = 5
num_days = 5  
num_timeslots_per_day = 5  

# Initialize the score matrix with a base score of 1
score_matrix = [[[1 for _ in range(num_timeslots_per_day)] for _ in range(num_days)] for _ in range(num_classes)]

# Chairs' schedule (class_idx, day_idx, timeslot_idx)
chairs_schedule = [(0, 0, 0),  # Class 0 on Day 0, Time slot 0
                   (1, 1, 2),  # Class 1 on Day 1, Time slot 2
                   (2, 2, 3),  # Class 2 on Day 2, Time slot 3
                   (3, 3, 3),  # Class 3 on Day 3, Time slot 3
                   (4, 2, 3)]  # Class 4 on Day 4, Time slot 4

# Augment the score matrix with the chair's schedule: set those scores to 10
for class_idx, day_idx, timeslot_idx in chairs_schedule:
    score_matrix[class_idx][day_idx][timeslot_idx] = 10

# Create a new model
model = gp.Model("Class Scheduling")

# Decision variables: x[i][d][t] is 1 if class i is scheduled on day d in timeslot t, 0 otherwise
x = model.addVars(num_classes, num_days, num_timeslots_per_day, vtype=GRB.BINARY, name="x")

# Objective: maximize the total score based on the score matrix
model.setObjective(gp.quicksum(score_matrix[i][d][t] * x[i, d, t]
                               for i in range(num_classes)
                               for d in range(num_days)
                               for t in range(num_timeslots_per_day)), GRB.MAXIMIZE)

# Constraints:
# 1. Each class must be scheduled in exactly one time slot across all days
for i in range(num_classes):
    model.addConstr(gp.quicksum(x[i, d, t] for d in range(num_days) for t in range(num_timeslots_per_day)) == 1,
                    name=f"class_{i}_once")

# 2. No two classes can be scheduled in the same time slot on the same day
# for d in range(num_days):
#     for t in range(num_timeslots_per_day):
#         model.addConstr(gp.quicksum(x[i, d, t] for i in range(num_classes)) <= 1, name=f"time_{d}_{t}_non_overlap")

# Course Conflict Group Implementation
conflict_group = [(0,1), (2,4)]

for course1, course2 in conflict_group:
    for d in range(num_days):
        for t in range(num_timeslots_per_day):
            model.addConstr(x[course1, d, t] + x[course2, d, t] <= 1, name=f"no_overlap_{course1}_{course2}_day{d}_time{t}")

# Optimize the model
model.optimize()

# Output the results
if model.status == GRB.OPTIMAL:
    print("\nOptimal schedule:")
    for i in range(num_classes):
        for d in range(num_days):
            for t in range(num_timeslots_per_day):
                if x[i, d, t].x > 0.5:  # If variable is selected
                    print(f"Class {i} is scheduled on Day {d} in timeslot {t}")
    print("\nMaximum Score:", model.objVal)
else:
    print("No optimal solution found.")
