import random
from typing import List
import matplotlib.pyplot as plt

class WorkforceScheduler:
    def __init__(self, employees: List[dict], shifts: List[str], population_size=50, generations=100, mutation_rate=0.01, elite_size=5):
        self.employees = employees
        self.shifts = shifts
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.elite_size = elite_size

    def create_initial_population(self):
      population = []
      for _ in range(self.population_size):
        schedule = {}
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            # Randomly assign employees to morning and evening shifts
            morning_shift = f"{day} Morning"
            evening_shift = f"{day} Evening"

            available_employees = self.employees[:]
            morning_employees = random.sample(available_employees, 2)
            schedule[morning_shift] = morning_employees

            # Remove morning employees from the pool for the evening shift
            available_employees = [emp for emp in available_employees if emp not in morning_employees]
            evening_employees = random.sample(available_employees, 2)
            schedule[evening_shift] = evening_employees

        population.append(schedule)
      return population


    def calculate_fitness(self, schedule):
      # Count shifts for each employee
      shift_count = {emp["name"]: 0 for emp in self.employees}
      for assigned_employees in schedule.values():
        for employee in assigned_employees:
            shift_count[employee["name"]] += 1

      # Penalize if any employee is assigned to two shifts on the same day
      fitness = 0
      days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
      for day in days:
        morning_shift = f"{day} Morning"
        evening_shift = f"{day} Evening"
        morning_employees = schedule[morning_shift]
        evening_employees = schedule[evening_shift]

        for employee in self.employees:
            if employee in morning_employees and employee in evening_employees:
                fitness -= 5  # Significant penalty for same-day double shifts

      # Penalize imbalance in shift distribution
      counts = list(shift_count.values())
      imbalance = sum(abs(count - (len(self.shifts) * 2 / len(self.employees))) for count in counts)
      fitness -= imbalance  # Lower imbalance = Higher fitness

      # Ensure gender constraint: At least 1 man per shift
      for shift, assigned_employees in schedule.items():
        if not any(emp["gender"] == "Male" for emp in assigned_employees):
            fitness -= 5  # Significant penalty for missing gender constraint

      return fitness

    def rank_population(self, population):
        ranked = [(schedule, self.calculate_fitness(schedule)) for schedule in population]
        return sorted(ranked, key=lambda x: x[1], reverse=True)

    def selection(self, ranked_population):
        selected = [schedule for schedule, _ in ranked_population[:self.elite_size]]
        while len(selected) < self.population_size:
            tournament = random.sample(ranked_population, 3)
            winner = max(tournament, key=lambda x: x[1])[0]
            selected.append(winner)
        return selected

    def crossover(self, parent1, parent2):
        child = {}
        for shift in self.shifts:
            child[shift] = parent1[shift] if random.random() > 0.5 else parent2[shift]
        return child

    def mutate(self, schedule):
        for shift in self.shifts:
            if random.random() < self.mutation_rate:
                schedule[shift] = random.sample(self.employees, 2)  # Randomly reassign 2 employees
        return schedule

    def breed_population(self, selected_population):
        children = selected_population[:self.elite_size]
        for _ in range(self.population_size - self.elite_size):
            parent1, parent2 = random.sample(selected_population, 2)
            child = self.crossover(parent1, parent2)
            child = self.mutate(child)
            children.append(child)
        return children

    def optimize(self):
        population = self.create_initial_population()
        for _ in range(self.generations):
            ranked_population = self.rank_population(population)
            selected_population = self.selection(ranked_population)
            population = self.breed_population(selected_population)
        best_schedule = self.rank_population(population)[0][0]
        return best_schedule

# Function to count shifts assigned to each employee
def count_shifts(schedule, employees):
    shift_count = {emp["name"]: 0 for emp in employees}
    for assigned_employees in schedule.values():
        for employee in assigned_employees:
            shift_count[employee["name"]] += 1
    return shift_count

# Function to visualize shift distribution
def visualize_shift_distribution(shift_count):
    names = list(shift_count.keys())
    counts = list(shift_count.values())

    plt.bar(names, counts, color='skyblue')
    plt.xlabel('Employees')
    plt.ylabel('Number of Shifts')
    plt.title('Shift Distribution')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# Function to collect user input
def get_user_input():
    print("Welcome to Workforce Scheduler!")

    # Get employees with gender
    employees = []
    num_employees = int(input("Enter the number of employees: "))
    for _ in range(num_employees):
        name = input("Enter employee name: ").strip()
        gender = input(f"Enter gender for {name} (Male/Female): ").strip()
        employees.append({"name": name, "gender": gender})

    # Generate 14 shifts: 7 days × 2 shifts/day
    shifts = []
    for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
        shifts.append(f"{day} Morning")
        shifts.append(f"{day} Evening")

    return employees, shifts

# Main program
if __name__ == "__main__":
    # Collect user input
    employees, shifts = get_user_input()

    # Initialize scheduler
    scheduler = WorkforceScheduler(
    employees, shifts, population_size=100, generations=200, mutation_rate=0.02, elite_size=10)


    # Optimize schedule
    optimal_schedule = scheduler.optimize()

    # Display optimal schedule
    print("\nOptimal Schedule:")
    for shift, assigned_employees in optimal_schedule.items():
        print(f"{shift}: {', '.join(emp['name'] for emp in assigned_employees)}")

    # Count shifts for each employee
    shift_count = count_shifts(optimal_schedule, employees)

    # Visualize shift distribution
    visualize_shift_distribution(shift_count)
