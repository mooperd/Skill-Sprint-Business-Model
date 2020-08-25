from business_class import run_model
import copy

# TODO: Are these variables "Real" KPIs that can be measured?

conditions = {
    'scenario_name': 'optimist',
    'business_cost_max': 15000,
    'business_cost_min': 5000,
    'capital': 250000,
    'completed_jobs': 0,
    'customer_acquisition_cost': 10000,
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
    }

months = [
        "Meow 21","Feb 21","Mar 21","Apr 21",
        "May 21","Jun 21","Jul 21","Aug 21",
        "Sep 21","Oct 21","Nov 21","Dec 21",
        "Jan 22","Feb 22","Mar 22","Apr 22",
        "May 22","Jun 22","Jul 22","Aug 22",
        "Sep 22","Oct 22","Nov 22","Dec 22"
        ]

input_datas = []
costs = [2000,4000,6000,8000,10000]

for i in costs:
    _conditions_ = copy.deepcopy(conditions)
    _conditions_["customer_acquisition_cost"] = i
    _conditions_["scenario_name"] = str(i)
    input_datas.append(_conditions_)

run_model(input_datas, months)