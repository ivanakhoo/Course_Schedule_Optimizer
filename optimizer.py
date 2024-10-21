import gurobipy as gp
from gurobipy import GRB

# Sample data (classes x time slots)
num_classes = 5
num_timeslots = 5

# Initialize the score matrix with a base score of 1
score_matrix = [[1 for _ in range(num_timeslots)] for _ in range(num_classes)]

# Chairs' schedule (this is just an example, assume [(class_idx, timeslot_idx)] format)
chairs_schedule = [(0, 0), (1, 2), (2, 3), (3, 3), (4, 4)]

# Augment the score matrix with the chair's schedule: set those scores to 10
for class_idx, timeslot_idx in chairs_schedule:
    score_matrix[class_idx][timeslot_idx] = 10

# Create a new model
model = gp.Model("Class Scheduling")

# Decision variables: x[i][j] is 1 if class i is scheduled in timeslot j, 0 otherwise
x = model.addVars(num_classes, num_timeslots, vtype=GRB.BINARY, name="x")

# Objective: maximize the total score based on the score matrix
model.setObjective(gp.quicksum(score_matrix[i][j] * x[i, j]
                               for i in range(num_classes)
                               for j in range(num_timeslots)), GRB.MAXIMIZE)

# Constraints:
# 1. Each class must be scheduled in exactly one timeslot
for i in range(num_classes):
    model.addConstr(gp.quicksum(x[i, j] for j in range(num_timeslots)) == 1, name=f"class_{i}_once")

# 2. No two classes can be scheduled in the same timeslot
for j in range(num_timeslots):
    model.addConstr(gp.quicksum(x[i, j] for i in range(num_classes)) <= 1, name=f"time_{j}_non_overlap")

# Optimize the model
model.optimize()

# Output the results
if model.status == GRB.OPTIMAL:
    print("\nOptimal schedule:")
    for i in range(num_classes):
        for j in range(num_timeslots):
            if x[i, j].x > 0.5:  # If variable is selected
                print(f"Class {i} is scheduled in timeslot {j}")
    print("\nMaximum Score:", model.objVal)
else:
    print("No optimal solution found.")
