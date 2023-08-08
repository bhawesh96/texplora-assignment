import datetime
import SharedConstants as SC


class DTUtils:
    @staticmethod
    def convert_weekend_to_Monday(datetime_obj):
        return datetime_obj + datetime.timedelta(7 - datetime_obj.weekday())

    @staticmethod
    def convert_to_datetime(date_str, format_string):
        return datetime.datetime.strptime(date_str, format_string)

    @staticmethod
    def is_considerable_txn(transaction):
        if float(transaction[5]) == 0.0:   # payable is 0, return true if receivable is > 1
            return float(transaction[6]) > 1

        return True  # payable > 1, so, return true
