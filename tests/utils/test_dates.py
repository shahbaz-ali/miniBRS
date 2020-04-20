import pytest
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


class TestDates():

    @pytest.mark.start
    def test_get_start_date(self):

        with pytest.raises(BadStartDatePreset):
            get_start_date("1xx")

    @pytest.mark.start_date
    def test_days_get_start_date(self):

        result1 = get_start_date("1day")
        print(f'{str(get_days(result1))}')

        assert get_days(get_start_date("1day")) == 1
        assert get_days(get_start_date("1days")) == 1
        assert get_days(get_start_date("100day")) == 100
        assert get_days(get_start_date("100days")) == 100
        assert get_days(get_start_date("2days")) == 2
        assert get_days(get_start_date("3days")) == 3
        assert get_days(get_start_date("-3days")) == 3
        assert get_days(get_start_date("10days")) == 10

        with pytest.raises(BadStartDatePreset):
            get_start_date("2xx")

        with pytest.raises(BadStartDatePreset):
            get_start_date("10months")

        with pytest.raises(BadStartDatePreset):
            get_start_date("10")

    @pytest.mark.days_ago
    def test_days_ago(self):
        
        assert isinstance(days_ago(2), datetime)
        with pytest.raises(TypeError):
            days_ago("2")

    @pytest.mark.skip
    def test_months_ago(self):

        assert isinstance(months_ago(2), int)
        with pytest.raises(ValueError):
            months_ago("2")

