import gurobipy as gp
from gurobipy import GRB

# Create a Gurobi model
model = gp.Model("Course Schedule Optimization")

# Define matrix dimensions (days and courses)
days = 5
courses = 5

# Conflict list: Define pairs of courses that cannot be scheduled on the same day
conflicts = [(2, 4), (1, 3)]  # Example conflict pair

# Initialize continuous variables for each day-course slot
x = model.addVars(days, courses, vtype=GRB.CONTINUOUS, name="x")

# Initialize specific courses that are originally scheduled with value 10
initial_schedule = {
    (0, 1): 10,
    (1, 2): 10,
    (1, 4): 10,
    (2, 3): 10,
    (3, 0): 10
}

# Store the initial values separately for printing later
initial_values = {}

# Set the initial values for the scheduled courses using the start attribute
for (day, course), value in initial_schedule.items():
    x[day, course].start = value  # Set initial value to 10 for scheduled courses
    initial_values[(day, course)] = value  # Save initial values

# Set the value for unused slots to 0.5 using the start attribute
for day in range(days):
    for course in range(courses):
        if (day, course) not in initial_schedule:
            x[day, course].start = 0.5  # Set initial value to 0.5 for unused slots
            initial_values[(day, course)] = 0.5  # Save initial value

# Function to print the scheduling matrix
def print_schedule_matrix(initial_values, optimized=False):
    print("\nSchedule Matrix:")
    for i in range(days):
        row = []
        for j in range(courses):
            if (i, j) in initial_values:
                value = initial_values[(i, j)]
                row.append(f"{value:.1f}" if not optimized else f"{x[i, j].X:.1f}")
            else:
                row.append(f"{0.5:.1f}")  # Default for unused slots
        print(" | ".join(row))
    print("\n")

# Print the initial matrix
print_schedule_matrix(initial_values, optimized=False)

# Conflict management: penalize if two conflicting courses are scheduled on the same day
for day in range(days):
    for course1, course2 in conflicts:
        # Allow either course to be scheduled or have a penalty
        model.addConstr(x[day, course1] + x[day, course2] <= 10, f"conflict_{course1}_{course2}_day_{day}")

# Movement penalties: if a course moves to a different day, decrease its value by 1
for day in range(days):
    for course in range(courses):
        for conflict_course1, conflict_course2 in conflicts:
            if course in [conflict_course1, conflict_course2]:
                # Move the course to another day
                for new_day in range(days):
                    if new_day != day:
                        # Allow moving to a new day and apply a penalty of 1
                        model.addConstr(x[new_day, course] <= x[day, course] - 1, f"penalty_{course}_day_{new_day}")

# Objective: Maximize the total score of the schedule
model.setObjective(gp.quicksum(x[i, j] for i in range(days) for j in range(courses)), GRB.MAXIMIZE)

# Optimize the model
model.optimize()

# Print the optimized schedule (if optimal)
if model.status == GRB.OPTIMAL:
    print("Optimized course schedule:")
    print_schedule_matrix(initial_values, optimized=True)  # Print the final schedule
else:
    print("The model is infeasible or has an issue.")
