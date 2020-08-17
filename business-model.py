import json
import csv
import copy
import random
from math import floor

starting_conditions = {
    "capital": 250000,
    "number_of_employees": 1,
    "customer_acquisition_cost": 10000,
    "customer_acquisition_spend": 10000,
    "jobs_per_acquired_customer": 1,
    "per_employee_monthly_cost": 5000,
    "employee_min_jobs_per_month": 2,
    "employee_max_jobs_per_month": 4,
    "new_customers": 0,
    "job_price": 7500,
    "job_backlog": 0,
    "founder_stress": 0,
    "total_monthly_costs": 0,
    "monthly_costs": {},
    "monthly_balance": 0,
    "revenue": 0,
    "completed_jobs": 0,
    "month": "",
    "founder_salaries": 10000, # Two founders; 5000 each
    "business_cost_min": 5000, 
    "business_cost_max": 15000,
}

variables = {
    "customer_acquisition_cost": 0.85,  # 0.9 is the lowest sensible value
    "customer_acquisition_spend": 0,
    "jobs_per_acquired_customer": 1.01,
    "per_employee_monthly_cost": 1.01,
    "price_per_skill_sprint": 1.01
}

months = [
        "Jan 21","Feb 21","Mar 21","Apr 21",
        "May 21","Jun 21","Jul 21","Aug 21",
        "Sep 21","Oct 21","Nov 21","Dec 21",
        "Jan 22","Feb 22","Mar 22","Apr 22",
        "May 22","Jun 22","Jul 22","Aug 22",
        "Sep 22","Oct 22","Nov 22","Dec 22"
        ]

monthy_output = []

def run_month(conditions, month):    
    conditions["month"] = month
    
    # Calculate how many new customers we get and add them to the backlog
    new_customers = conditions["customer_acquisition_spend"] / conditions["customer_acquisition_cost"]
    conditions["new_customers"] = new_customers
    conditions["monthly_costs"]["customer_acquisition_spend"] = conditions["customer_acquisition_spend"]

    # Calculate how many jobs go into the backlog
    conditions["new_jobs"] = conditions["new_customers"] * conditions["jobs_per_acquired_customer"]
    conditions["job_backlog"] += conditions["new_jobs"]

    # Calculate the cost of employees
    employee_cost = conditions["number_of_employees"] * conditions["per_employee_monthly_cost"]
    conditions["monthly_costs"]["employee_cost"] = employee_cost
    conditions["monthly_costs"]["founder_salaries"] = conditions["founder_salaries"]

    # Calculate business expense.
    business_cost = random.randint(conditions["business_cost_min"], conditions["business_cost_max"])
    conditions["monthly_costs"]["business_cost"] = business_cost

    # Put the employees to work and calculate revenue
    job_capacity = conditions["number_of_employees"] * conditions["employee_max_jobs_per_month"]
    revenue = 0
    completed_jobs = 0
    print(conditions)
    print(job_capacity, conditions["job_backlog"])

    while job_capacity >= 1 and conditions["job_backlog"] >= 1:
        job_capacity -= 1
        conditions["job_backlog"] -= 1
        revenue += conditions["job_price"]
        completed_jobs += 1
        print(job_capacity, conditions["job_backlog"], completed_jobs)

    conditions["revenue"] = revenue
    conditions["completed_jobs"] = completed_jobs

    # Hire new employees
    if conditions["job_backlog"] > conditions["employee_min_jobs_per_month"]:
        required_employees = floor(conditions["job_backlog"] / conditions["employee_min_jobs_per_month"])
        conditions["number_of_employees"] += required_employees
    
    # Calculate monthly costs
    total_monthly_costs = 0
    for cost in conditions["monthly_costs"].values():
        total_monthly_costs += cost
    conditions["total_monthly_costs"] = total_monthly_costs

    # Financial Adjustments
    conditions["monthly_balance"] = conditions["revenue"] - conditions["total_monthly_costs"]
    conditions["capital"] += conditions["monthly_balance"]

    # conditions["number_of_employees"]
    conditions["customer_acquisition_cost"] *= variables["customer_acquisition_cost"]
    conditions["customer_acquisition_spend"] *= variables["customer_acquisition_spend"]
    conditions["jobs_per_acquired_customer"] *= variables["jobs_per_acquired_customer"]
    conditions["per_employee_monthly_cost"] *= variables["per_employee_monthly_cost"]
    # conditions["employee_min_jobs_per_month"]
    # conditions["employee_max_jobs_per_month"]
    # conditions["new_customers"]
    # conditions["price_per_skill_sprint"]
    # conditions["job_backlog"]
    # conditions["founder_stress"]
    # conditions["monthly_costs"]
    # conditions["month"]
    # print(print(json.dumps(conditions, indent=4, sort_keys=True)))
    return conditions

output = []
input_conditions = starting_conditions
for month in months:
    input_conditions = run_month(input_conditions, month)
    output.append(copy.deepcopy(input_conditions))

with open('/Volumes/GoogleDrive/My Drive/business_forecast_csv/output.csv', 'w', encoding='utf8', newline='') as output_file:
    fc = csv.DictWriter(output_file, fieldnames=output[0].keys())
    fc.writeheader()
    fc.writerows(output)