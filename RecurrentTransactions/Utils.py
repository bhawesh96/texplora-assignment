from datetime import datetime, timedelta
import csv

import openpyxl

import SharedConstants as SC


class DTUtils:
    @staticmethod
    def convert_weekend_to_monday(datetime_obj):
        return datetime_obj + timedelta(7 - datetime_obj.weekday())

    @staticmethod
    def convert_to_datetime(date_str, format_string):
        return datetime.strptime(date_str, format_string)


class CSVUtils:
    @staticmethod
    def write_to_csv(dup_transaction_list):
        with open(SC.output_csv_filename, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(SC.COL_HEADERS)

            for txn in dup_transaction_list:
                writer.writerow([txn.account,
                                 datetime.strftime(txn.first_occurrence, "%d-%m-%Y"),
                                 txn.reference,
                                 txn.plan,
                                 txn.payable,
                                 txn.receivable,
                                 ])
