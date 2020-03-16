import unittest
from plugins.mbrs.utils.dates import get_start_date,days_ago,months_ago
from plugins.mbrs.utils.exceptions import BadStartDatePreset
from datetime import datetime


def get_days(result):
    '''
     current_date-result gives 100 days, 12:13:24.504118, but we only need 100.
     So we split the string and get the 100 only
    '''
    current_date = datetime.now()
    return  int(str(current_date-result).split(" ")[0])

def get_days_in_months(result):
    '''
     current_date-result gives 100 days, 12:13:24.504118, but we only need 100.
     So we split the string and get the 100 only
    '''
    current_date = datetime.now()
    return  str(current_date-result)


class TestDates(unittest.TestCase):

    #test case for months
    def test_get_start_date(self):

        result1 = get_start_date("4mo")
        print(f'###result {result1}')
        print(f'###DinM {str(get_days_in_months(result1))}')

        # self.assertEqual(get_start_date("1mo"), 30)
        # self.assertEqual(get_start_date("2mo"), 60)
        # self.assertEqual(get_start_date("3mo"), 90)
        # self.assertEqual(get_start_date("-1mo"), 30)
        # self.assertEqual(get_start_date("-2mo"), 60)
        # self.assertEqual(get_start_date("-3mo"), 90)

        with self.assertRaises(BadStartDatePreset):
            get_start_date("1xx")

    #test case for days
    def test_days_get_start_date(self):

        result1=get_start_date("1da")
        print(f'{str(get_days(result1))}')

        self.assertEqual(get_days(get_start_date("1da")), 1)
        self.assertEqual(get_days(get_start_date("2da")), 2)
        self.assertEqual(get_days(get_start_date("3da")), 3)
        self.assertEqual(get_days(get_start_date("-3da")), 3)
        self.assertEqual(get_days(get_start_date("-10da")), 10)
        self.assertEqual(get_days(get_start_date("10da")), 10)

        with self.assertRaises(BadStartDatePreset):
            get_start_date("2xx")

    def test_days_ago(self):
        
        self.assertIsInstance(days_ago(2), datetime, msg=None)

        with self.assertRaises(ValueError):
            days_ago("2")

    def test_months_ago(self):

        self.assertIsInstance(months_ago(2), int, msg=None)

        with self.assertRaises(ValueError):
            months_ago("2")


if __name__ == '__main__':
    unittest.main()
