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


class Customer:
    def __init__(self, max_jobs_per_customer, month):
        self.name = base64.b64encode(arrow.utcnow().format('SSSSSSSSS').encode('ascii')).decode("utf-8") 
        self.max_jobs = floor(max_jobs_per_customer)
        # Customers are created when we sell the first job.
        self.jobs_put_in_backlog = 1
        # The percentage chance that a customer will produce a job each month.
        self.chance_of_job = random.randint(0,100)
        self.jobs = [[month, 50]]

    
    def job_sell(self, month):
        # Do we sell a job to this customer?
        random_dice = random.randint(0,100)
        if (self.max_jobs > self.jobs_put_in_backlog and 
                    random_dice < self.chance_of_job):
            self.jobs_put_in_backlog += 1
            self.jobs.append([month, random_dice])
            return True
        else:
            return False

class Business:
    def __init__(self, init_data):
        self.business_cost_max = init_data["business_cost_max"]
        self.business_cost_min = init_data["business_cost_min"]
        self.capital = init_data["capital"]
        self.customer_acquisition_cost = init_data["customer_acquisition_cost"]
        self.customer_acquisition_spend = init_data["customer_acquisition_spend"]
        self.customer_count = init_data["customer_count"]
        self.employee_max_jobs_per_month = init_data["employee_max_jobs_per_month"]
        self.employee_min_jobs_per_month = init_data["employee_min_jobs_per_month"]
        self.founder_salaries = init_data["founder_salaries"]    
        self.job_price = init_data["job_price"]
        self.max_jobs_per_customer = init_data["max_jobs_per_customer"]
        self.monthly_pc_adjustments = init_data["monthly_pc_adjustments"]
        self.per_employee_monthly_cost = init_data["per_employee_monthly_cost"]
        self.monthly_simple_adjustments = {}
        self.monthly_pc_adjustments = init_data["monthly_pc_adjustments"]
        self.number_of_employees = init_data["number_of_employees"]
        self.month = ""
        self.customers = []
        self.job_backlog = 0
        self.total_completed_jobs = 0
        

        # Zero some stuff and calculate initial changes.
        self.calculate_simple_adjustment_values()
        self.zero_monthly_counters()
        
        
    def zero_monthly_counters(self):
        self.new_customers_this_month = 0
        self.new_jobs_this_month = 0
        self.monthly_revenue = 0
        self.jobs_completed_this_month = 0
        self.monthly_balance = 0
        self.monthly_costs = {}
        self.monthly_costs_total = 0


    def calculate_new_customers(self):
        # Calculate how many new customers we get. 
        new_customers_this_month = floor(
            self.customer_acquisition_spend / 
            self.customer_acquisition_cost
            )
        self.new_customers_this_month = copy.deepcopy(new_customers_this_month)                 
        # Charge customer acquisition to the monthly account.
        self.monthly_costs["customer_acquisition_spend"] = self.customer_acquisition_spend

        # Create and add our new customers to the list.
        while new_customers_this_month > 0:
            self.customers.append(Customer(self.max_jobs_per_customer, month))
            new_customers_this_month -= 1
            # A customer is created with a job.
            self.new_jobs_this_month += 1

        # Count customers in the customer list.
        self.customer_count = len(self.customers)

    def calculate_business_cost(self):
        # Business expense is a random number 
        # between business_cost_min & business_cost_max
        business_cost = random.randint(
            self.business_cost_min, 
            self.business_cost_max
            )
        self.monthly_costs["business_cost"] = business_cost
    
    def calculate_employee_cost(self):
        # Calculate the cost of employees.
        self.monthly_costs["employee_cost"] = (
            self.number_of_employees * self.per_employee_monthly_cost
        )
        self.monthly_costs["founder_salaries"] = self.founder_salaries

    def hire_new_employees(self):
        # Hire new employees to cover remaining job backlog.
        # this calculation should be done AFTER doing the monthly work
        new_employees = floor(self.job_backlog / self.employee_min_jobs_per_month)
        self.number_of_employees += new_employees
            

    def put_employees_to_work(self):
        # Put the employees to work and calculate revenue
        self.job_capacity = (
            self.number_of_employees * 
            self.employee_max_jobs_per_month
            )
        while self.job_capacity >= 1 and self.job_backlog >= 1:
            self.job_capacity -= 1
            self.job_backlog -= 1
            self.monthly_revenue += self.job_price
            self.jobs_completed_this_month += 1
            print(self.job_capacity, self.job_backlog, self.monthly_revenue, self.jobs_completed_this_month )
        self.total_completed_jobs += self.jobs_completed_this_month
        # We want to pay our employees before hiring new ones
        # or we will have to pay our new employees a month early.
        self.calculate_employee_cost()
        self.hire_new_employees()
        


    def collect_new_jobs(self):
        # Calculate new jobs from existing customers
        for customer in self.customers:
            # If the customer produces job add it to the backlog.
            # Pass in a month so we can keep a record of when customers made orders.
            if customer.job_sell(self.month):
                self.new_jobs_this_month += 1
                # Add new jobs this month
        # add new jobs to the backlog
        self.job_backlog += self.new_jobs_this_month


    def calculate_monthly_balance(self):
        # Calculate monthly costs
        for cost in self.monthly_costs.values():
            self.monthly_costs_total += cost
        # Deduct costs from revenue
        self.monthly_balance = (
            self.monthly_revenue - self.monthly_costs_total
        )
        # Add / Subtract from capital
        self.capital += self.monthly_balance 
    

    def calculate_simple_adjustment_values(self):
        sim = self.monthly_simple_adjustments
        pc = self.monthly_pc_adjustments

        sim["customer_acquisition_cost"] = pc["customer_acquisition_cost"] * self.customer_acquisition_cost
        sim["customer_acquisition_spend"] = pc["customer_acquisition_spend"] * self.customer_acquisition_spend
        sim["max_jobs_per_customer"] = pc["max_jobs_per_customer"] * self.max_jobs_per_customer
        sim["per_employee_monthly_cost"] = pc["per_employee_monthly_cost"] * self.per_employee_monthly_cost
        
    
    def adjust_conditions(self):
        self.calculate_simple_adjustment_values()
        sim = self.monthly_simple_adjustments

        # add / minus our values to our conditions.
        self.customer_acquisition_cost += sim["customer_acquisition_cost"]
        self.customer_acquisition_spend += sim["customer_acquisition_spend"]
        self.max_jobs_per_customer += sim["max_jobs_per_customer"]
        self.per_employee_monthly_cost += sim["per_employee_monthly_cost"]
    
    def dump_dict(self):
        output_dict = copy.deepcopy(self.__dict__)
        customer_list = []
        for customer in output_dict["customers"]:
            customer_list.append(customer.__dict__)
        output_dict["customers"] = customer_list
        return output_dict



def write_data_to_sheet(data, condition):

    gc = gspread.service_account(
        filename='otters-cc-2795e33c4250.json'
        )
    sheet = gc.open("skill_sprint_model")
    # Get the column headers
    headers = list(data[0].keys())
    # We have to make everything a list of lists.
    row_list_of_lists = []
    # Iterate through everything and turn embedded
    # lists or dicts into json str.
    for row in data:
        for key, value in row.items():
            if isinstance(value, (dict, list)):
                row[key] = str(json.dumps(row[key]))

        row_list_of_lists.append(list(row.values()))

    try:
        sheet.add_worksheet(title=condition, rows="100", cols="20")
    except: # Lazy
        pass
    worksheet = sheet.worksheet(condition)
    worksheet.update('A1:AA1', [ headers ])    
    worksheet.update('A2:AA25', row_list_of_lists)


# TODO: Are these variables "Real" KPIs that can be measured?

conditions = [{
    'scenario_name': 'optimist',
    'business_cost_max': 15000,
    'business_cost_min': 5000,
    'capital': 250000,
    'completed_jobs': 0,
    'customer_acquisition_cost': 2000,
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
    'total_monthly_costs': 0,
    'monthly_pc_adjustments': {
        "customer_acquisition_cost": -0.025,
        "customer_acquisition_spend": 0,
        "max_jobs_per_customer": 0.05, # Not a real KPI
        "per_employee_monthly_cost": 0.01,
        "price_per_skill_sprint": 0.00
        }
    }]

months = [
        "Jan 21","Feb 21","Mar 21","Apr 21",
        "May 21","Jun 21","Jul 21","Aug 21",
        "Sep 21","Oct 21","Nov 21","Dec 21",
        "Jan 22","Feb 22","Mar 22","Apr 22",
        "May 22","Jun 22","Jul 22","Aug 22",
        "Sep 22","Oct 22","Nov 22","Dec 22"
        ]


def run_month(business, month):
    # The order that we do things here is probably very important.
    # Zero monthly counters. Seems better to do this here - explicitly.
    business.zero_monthly_counters()
    # Do the work, pay salaries then hire new employees.
    business.put_employees_to_work()
    # collect new jobs from old customers.
    business.collect_new_jobs()
    # How many customers do we get this month?
    business.calculate_new_customers()
    # Revenue minus costs
    business.calculate_monthly_balance()
    ### After the months business is concluded we can
    ### make decisions and adjust conditions.
    business.adjust_conditions()


output_list = []

for condition in conditions:
    business = Business(condition)
    for month in months:
        business.month = month
        run_month(business, month)
        output_list.append(business.dump_dict())
    write_data_to_sheet(output_list, condition["scenario_name"])
    


    """
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(business.dump_dict())
    """






"""
    output_filename = '/Volumes/GoogleDrive/My Drive/business_forecast_csv/{}.csv'.format(
        scenario)
    with open(output_filename, 'w', encoding='utf8', newline='') as output_file:
        fc = csv.DictWriter(output_file, fieldnames=data[0].keys())
        fc.writeheader()
        fc.writerows(data)
"""  
