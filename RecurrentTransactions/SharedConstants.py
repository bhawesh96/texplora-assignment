holiday_dates_italy_2022 = [
    "04-01-2022",
    "06-01-2022",
    "25-04-2022",
    "01-05-2022",
    "02-06-2022",
    "15-08-2022",
    "01-11-2022",
    "08-12-2022",
    "25-12-2022",
    "26-12-2022"
]

log_dir = './Logs'
log_filename = 'RecurrentTransactions_{}.log'
input_csv_filename = 'test_mastrini.csv'
output_csv_filename = 'output.csv'

# Column names
INDUSTRY_ID = 'Industry ID'
INDUSTRY_NAME = 'Industry Name'
BRANCH_CODE = 'Branch Code'
DATE = 'Date'
REFERENCE = 'Reference'
PAYABLE = 'Payable'
RECEIVABLE = 'Receivable'
PLAN = 'Plan'

COL_HEADERS = [BRANCH_CODE, DATE, REFERENCE, PLAN, PAYABLE, RECEIVABLE]

# Recurrent Plans
DAILY = 'Daily'
WEEKLY = 'Weekly'
MONTHLY = 'Monthly'
OTHER = 'Other'

MIN_TXN_AMT = 1  # 1 Euro
