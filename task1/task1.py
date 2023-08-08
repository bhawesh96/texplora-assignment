import SharedConstants as SC
import pandas
from datetime import datetime, timedelta
from Utils import DTUtils
import logging
import os
import time
import csv


##
# Method to configure logger for the script
def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(os.path.join(SC.log_dir, SC.log_filename.format(str(int(time.time()))))),
            logging.StreamHandler()
        ]
    )

try:
    configure_logging()
except:
    os.mkdir(SC.log_dir)
    configure_logging()

orig_df = pandas.read_csv('test_mastrini.csv')

accounts = orig_df[SC.BRANCH_CODE].unique()

LOG = logging.getLogger()

def write_to_csv(acc, dup_transactions):
    with open(SC.output_csv_filename, 'a') as f:
        writer = csv.writer(f)
        writer.writerow(SC.COL_HEADERS)

        for txn in dup_transactions:
            writer.writerow([acc,
                             dup_transactions[txn][0],
                             txn[0],
                             SC.DAILY,
                             txn[1],
                             txn[2]
                             ])

for acc in accounts:
    LOG.info('Iterating for Account (Branch Code): {}'.format(acc))
    df = orig_df[orig_df[SC.BRANCH_CODE] == acc]

    cols_to_check = [SC.REFERENCE, SC.PAYABLE, SC.RECEIVABLE]

    dup_mask = df.duplicated(cols_to_check, keep=False)

    dup_transactions = df[dup_mask].values

    dup_map = dict()

    for transaction in dup_transactions:
        dup_tuple_key = (transaction[4], transaction[5], transaction[6])  # key: (reference, payable, receivable)

        # if transaction value is < 1 Euro, ignore it
        if not DTUtils.is_considerable_txn(transaction):
            continue

        datetime_obj = DTUtils.convert_to_datetime(transaction[3], '%Y-%m-%d')

        if datetime_obj.weekday() in [5, 6]:  # if weekend, make it Monday
            datetime_obj = DTUtils.convert_weekend_to_Monday(datetime_obj)

        while datetime.strftime(datetime_obj, "%d-%m-%Y") in SC.holiday_dates_italy_2022:  # if holiday, skip to next day
            datetime_obj = datetime_obj + timedelta(1)

        try:
            dup_map[dup_tuple_key].append(datetime_obj)
            dup_map[dup_tuple_key] = sorted(dup_map[dup_tuple_key])
        except KeyError:
            dup_map[dup_tuple_key] = [datetime_obj]

    for transaction in dup_map:
        first_occurrence = dup_map[transaction][0]  # first time (date) the transaction has occurred
        ls = [first_occurrence.strftime('%d-%m-%Y')]
        # ls = [0]
        for i in range(1, len(dup_map[transaction])):
            ls.append((dup_map[transaction][i] - first_occurrence).days)
            # ls.append((dup_map[dup][i] -  dup_map[dup][i-1]).days)
        dup_map[transaction] = ls

    write_to_csv(acc, dup_map)
