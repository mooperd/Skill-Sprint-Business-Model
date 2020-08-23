import json
import pprint
import csv
import copy
import random
import base64
import arrow
from math import floor
import gspread

# Do bigger customers cost more to acquire?
# Model Big, Medium and Small customers.

# Can we model the pipeline? 
# How many leads do we need to create this many sales?
# What is the conversion rate?

starting_conditions = {   
    'business_cost_max': 15000,
    'business_cost_min': 5000,
    'capital': 250000,
    'completed_jobs': 0,
    'customer_acquisition_cost': 0,
    'customer_acquisition_spend': 10000,
    'customer_count': 0,
    'customers': [],
    'employee_max_jobs_per_month': 4,
    'employee_min_jobs_per_month': 2,
    'founder_salaries': 10000,
    'founder_stress': 0,
    'job_backlog': 0,
    'job_price': 7500,
    'max_jobs_per_customer': 2,
    'month': 'Jan 21',
    'monthly_balance': 0,
    'monthly_costs': {},
    'new_jobs': 2,
    'number_of_employees': 1,
    'per_employee_monthly_cost': 5000,
    'revenue': 0,
    'total_monthly_costs': 0
    }

# TODO: Are these variables "Real" KPIs that can be measured?
scenario_list = [{
    "scenario_name": "optimist",
    "initial_customer_acquisition_cost": 3000,
    "customer_acquisition_cost": -0.025,
    "customer_acquisition_spend": 0,
    "max_jobs_per_customer": 0.05, # Not a real KPI
    "per_employee_monthly_cost": 0.01,
    "price_per_skill_sprint": 0.00
},{
    "scenario_name": "realist",
    "initial_customer_acquisition_cost": 4000,
    "customer_acquisition_cost": -0.02,
    "customer_acquisition_spend": 0,
    "max_jobs_per_customer": 0.05,
    "per_employee_monthly_cost": 0.01,
    "price_per_skill_sprint": 0.01
},{
    "scenario_name": "pessimist",
    "initial_customer_acquisition_cost": 5000,
    "customer_acquisition_cost": -0.015,
    "customer_acquisition_spend": 0,
    "max_jobs_per_customer": 0.05,
    "per_employee_monthly_cost": 0.01,
    "price_per_skill_sprint": 0.01
}]

months = [
        "Jan 21","Feb 21","Mar 21","Apr 21",
        "May 21","Jun 21","Jul 21","Aug 21",
        "Sep 21","Oct 21","Nov 21","Dec 21",
        "Jan 22","Feb 22","Mar 22","Apr 22",
        "May 22","Jun 22","Jul 22","Aug 22",
        "Sep 22","Oct 22","Nov 22","Dec 22"
        ]

monthy_output = []

def createcustomer(max_jobs_per_customer):
    customer = {}
    customer["name"] = base64.b64encode(arrow.utcnow().format('SSSSSSSSS').encode('ascii')).decode("utf-8") 

    customer["max_jobs"] = max_jobs_per_customer
    customer["jobs_put_in_backlog"] = 0
    customer["chance_of_job"] = random.randint(0,10)
    return customer

def 

def run_month(conditions, month):    
    conditions["month"] = month
    conditions["new_jobs"] = 0


    # if customer_acquisition_cost is zero then we know we are at the start
    # of the simulation or something has gone horribly wrong.
    if conditions["customer_acquisition_cost"] == 0:
        conditions["customer_acquisition_cost"] = variables["initial_customer_acquisition_cost"]

    # Calculate how many new customers we get and add them to customer list 
    # after adding their first job to the backlog.
    new_customers = floor(conditions["customer_acquisition_spend"] / conditions["customer_acquisition_cost"])
    # Charge customer acquisition to the monthly account.
    conditions["monthly_costs"]["customer_acquisition_spend"] = conditions["customer_acquisition_spend"]

    while new_customers > 0:
        customer = createcustomer(conditions["max_jobs_per_customer"])
        new_customers -= 1

        # Add first job to the backlog
        # TODO: Function me?
        conditions["new_jobs"] += 1
        customer["jobs_put_in_backlog"] += 1
        conditions["customers"].append(customer)

    # Count customers
    conditions["customer_count"] = len(conditions["customers"])

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


    while job_capacity >= 1 and conditions["job_backlog"] >= 1:
        job_capacity -= 1
        conditions["job_backlog"] -= 1
        revenue += conditions["job_price"]
        completed_jobs += 1

    conditions["revenue"] = revenue
    conditions["completed_jobs"] = completed_jobs

    # Calculate new jobs from existing customers
    for customer in conditions["customers"]:
        # Throw the dice
        random_int = random.randint(0,10)
        if floor(customer["max_jobs"]) > customer["jobs_put_in_backlog"]:
            if customer["chance_of_job"] >= random_int:
                conditions["new_jobs"] += 1
                customer["jobs_put_in_backlog"] += 1

    # Hire new employees
    # TODO: is this really working properly?
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

    # work our increments so increases and decreases are not exponential.
    value = {}
    value["customer_acquisition_cost"] = conditions["customer_acquisition_cost"] * variables["customer_acquisition_cost"]
    value["customer_acquisition_spend"] = conditions["customer_acquisition_spend"] * variables["customer_acquisition_spend"]
    value["max_jobs_per_customer"] = conditions["max_jobs_per_customer"] * variables["max_jobs_per_customer"]
    value["per_employee_monthly_cost"] = conditions["per_employee_monthly_cost"] * variables["per_employee_monthly_cost"]
    
    print("customer_acquisition_cost = {}".format(value["customer_acquisition_cost"]))
    print("customer_acquisition_spend = {}".format(value["customer_acquisition_spend"]))
    print("max_jobs_per_customer = {}".format(value["max_jobs_per_customer"]))
    print("per_employee_monthly_cost = {}".format(value["per_employee_monthly_cost"]))
    
    # add / minus our values to our conditions.
    conditions["customer_acquisition_cost"] += value["customer_acquisition_cost"]
    conditions["customer_acquisition_spend"] += value["customer_acquisition_spend"]
    conditions["max_jobs_per_customer"] += value["max_jobs_per_customer"]
    conditions["per_employee_monthly_cost"] += value["per_employee_monthly_cost"]
    # Add new jobs this month
    # into the backlog
    conditions["job_backlog"] += conditions["new_jobs"]

    """
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(conditions)
    """
    return conditions

output = {}
for variables in scenario_list:
    input_conditions = copy.deepcopy(starting_conditions)
    output[variables["scenario_name"]] = []
    for month in months:
        input_conditions = run_month(input_conditions, month)
        output[variables["scenario_name"]].append(copy.deepcopy(input_conditions))

gc = gspread.service_account(filename='otters-cc-2795e33c4250.json')
sheet = gc.open("skill_sprint_growth_model")

for scenario, data in output.items():
    headers = list(data[0].keys())
    row_list_of_lists = []
    for row in data:
        row["customers"] = str(json.dumps(row["customers"]))
        row["monthly_costs"] = str(json.dumps(row["monthly_costs"]))
        row_list_of_lists.append(list(row.values()))
    worksheet = sheet.worksheet(scenario)
    # worksheet.update('A1:W1', [ headers ])
    worksheet.update('A2:W25', row_list_of_lists)



"""
    output_filename = '/Volumes/GoogleDrive/My Drive/business_forecast_csv/{}.csv'.format(
        scenario)
    with open(output_filename, 'w', encoding='utf8', newline='') as output_file:
        fc = csv.DictWriter(output_file, fieldnames=data[0].keys())
        fc.writeheader()
        fc.writerows(data)
"""  