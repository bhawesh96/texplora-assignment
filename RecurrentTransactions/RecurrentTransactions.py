import SharedConstants as SC
import pandas
from datetime import datetime, timedelta
from Utils import DTUtils, CSVUtils
import logging
import os
import time
from collections import Counter


# Class for a generic transaction
class Transaction:
    def __init__(self, transaction):
        self.industry_id = transaction[0]
        self.industry_name = transaction[1]
        self.branch_code = transaction[2]
        self.date_ = DTUtils.convert_to_datetime(transaction[3], '%Y-%m-%d')
        self.adjusted_date = self.date_
        self.reference = transaction[4]
        self.payable = transaction[5]
        self.receivable = transaction[6]

    # get the tuple which will be used to identify a unique recurrent transaction
    def get_key_tuple(self):
        return tuple([self.reference, self.payable, self.receivable])

    # check whether the transaction amount is significant for it to consider it a valid transaction
    def is_considerable_transaction(self):
        if float(self.payable) == 0.0:  # payable is 0, return true if receivable is > 1
            return float(self.receivable) > SC.MIN_TXN_AMT

        return True if float(self.payable) > SC.MIN_TXN_AMT else False  # payable > 1, so, return true

    # if the transaction is Recovery of previous year's balance, ignore it
    def is_recovery_transaction(self):
        return self.reference == "Ripresa saldo esercizio precedente"

    # check whether the transaction was held on a weekend
    def is_weekend(self):
        return self.adjusted_date.weekday() in [5, 6]  # 5, 6 are used for Saturday and Sunday

    # check whether the transaction was held on a holiday
    def is_holiday(self):
        return self.get_adjusted_display_date() in SC.holiday_dates_italy_2022

    # get display date for adjusted date
    def get_adjusted_display_date(self):
        return datetime.strftime(self.adjusted_date, "%d-%m-%Y")

    # get display date for original date
    def get_orig_display_date(self):
        return datetime.strftime(self.date_, "%d-%m-%Y")

    # set adjusted date
    def set_adjusted_date(self, adjusted_date):
        self.adjusted_date = adjusted_date


# Class for a duplicate transaction
class DuplicateTransaction:
    plan = None
    date_diff = None
    date_gaps = None

    def __init__(self, account, transaction, date_list):
        self.reference = transaction[0]
        self.payable = transaction[1]
        self.receivable = transaction[2]
        self.date_list = sorted(date_list)
        self.account = account
        self.first_occurrence = self.date_list[0]

    # iterate over the dates of occurrence of the duplicate transaction and find the frequency of occurrence
    def iterate_dates_and_find_frequency(self):
        self.date_diff = [(self.date_list[i + 1] - self.date_list[i]).days for i in range(len(self.date_list) - 1)]
        self.date_gaps = Counter(self.date_diff)

    # basis the frequency, find the Plan
    # Note: buffers have been added
    def set_plan_from_frequency(self):
        daily_gap = all(1 <= gap <= 3 for gap in self.date_gaps)
        weekly_gap = all(5 <= gap <= 9 for gap in self.date_gaps)
        monthly_gap = all(25 <= gap <= 35 for gap in self.date_gaps)

        if daily_gap:
            self.plan = SC.DAILY
        elif weekly_gap:
            self.plan = SC.WEEKLY
        elif monthly_gap:
            self.plan = SC.MONTHLY
        else:
            self.plan = SC.OTHER


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
except FileNotFoundError:
    os.mkdir(SC.log_dir)
    configure_logging()

LOG = logging.getLogger()

"""
Find all recurrent transactions based on reference, payable amt and receivable amt
:param account: the branch code
:param orig_df: the original dataframe read from the CSV
:return: map of duplicate transactions with the occurring dates
"""
def find_recurrent_transactions(account, orig_df):
    df = orig_df[orig_df[SC.BRANCH_CODE] == account]  # dataframe for this account

    cols_to_check = [SC.REFERENCE, SC.PAYABLE, SC.RECEIVABLE]  # the cols for filtering recurring transactions

    dup_mask = df.duplicated(cols_to_check, keep=False)  # apply the duplicate mask

    dup_transactions = df[dup_mask].values

    dup_map = dict()

    for transaction in dup_transactions:
        transaction_obj = Transaction(transaction)  # create a transaction object
        dup_tuple_key = transaction_obj.get_key_tuple()  # key: (reference, payable, receivable)

        # if transaction value is < 1 Euro, ignore it
        if not transaction_obj.is_considerable_transaction():
            LOG.info('{} - Skipping transaction as amount is < {} Euro (min transaction amount)'.format(transaction_obj.get_key_tuple(), SC.MIN_TXN_AMT))
            continue

        if transaction_obj.is_recovery_transaction():
            LOG.info('{} - Skipping transaction as it is a recovery transaction'.format(transaction_obj.get_key_tuple(), SC.MIN_TXN_AMT))
            continue

        # handle weekends and holidays
        while transaction_obj.is_weekend() or transaction_obj.is_holiday():
            if transaction_obj.is_weekend():  # if weekend, make it Monday
                day = 'Saturday' if transaction_obj.date_.weekday() == 5 else 'Sunday'
                LOG.info('{} - This transaction was held on {}. Converting it to Monday'.format(transaction_obj.get_key_tuple(), day))
                transaction_obj.set_adjusted_date(DTUtils.convert_weekend_to_monday(transaction_obj.date_))

            if transaction_obj.is_holiday():  # if holiday, make it next working day
                LOG.info('{} - This transaction was held on a holiday ({}). Converting it to the next working day'.
                         format(transaction_obj.get_key_tuple(), transaction_obj.get_adjusted_display_date()))
                transaction_obj.set_adjusted_date(transaction_obj.date_ + timedelta(1))

        try:  # append to date list in duplicate map
            dup_map[dup_tuple_key].append(transaction_obj.date_)
        except KeyError:  # new occurrence
            dup_map[dup_tuple_key] = [transaction_obj.date_]

    return dup_map


"""
Handle the duplicate transactions by finding the frequency and arriving at a recurrence plan
:param account: the branch code
:param dup_map: the duplicate transactions' map
:return: list of DuplicateTransaction objects
"""
def handle_duplicate_transactions(account, dup_map):
    duplicate_transactions = list()

    # the duplicate transactions are now available in the dup_map. Now, find the frequency of recurrence and set a plan
    for key_tuple, date_list in dup_map.items():
        dup_transaction_obj = DuplicateTransaction(account, key_tuple, date_list)

        dup_transaction_obj.iterate_dates_and_find_frequency()

        dup_transaction_obj.set_plan_from_frequency()

        duplicate_transactions.append(dup_transaction_obj)

    return duplicate_transactions


def main():
    orig_df = pandas.read_csv(SC.input_csv_filename)  # read the CSV into a Pandas dataframe

    accounts = orig_df[SC.BRANCH_CODE].unique()  # find unique accounts

    handled_duplicate_transactions_list = list()

    for account in accounts:
        LOG.info('Iterating for Account (Branch Code): {}'.format(account))
        bare_duplicate_transactions_map = find_recurrent_transactions(account, orig_df)  # find duplicate transactions

        handled_duplicate_transactions_list.extend(handle_duplicate_transactions(account, bare_duplicate_transactions_map))

    CSVUtils.write_to_csv(handled_duplicate_transactions_list)  # write to CSV


if __name__ == "__main__":
    main()
