from unittest import TestCase
from main import FinData


class TestFinData(TestCase):
    fin_data_test_subject = None

    def __init__(self, *args, **kwargs):
        super(TestFinData, self).__init__(*args, **kwargs)
        self.fin_data_test_subject = FinData()

    def test_get_revenue(self):
        revenue_data = self.fin_data_test_subject.get_revenue('AAPL',2010,1,2022,4)
        self.assertEqual(len(revenue_data), 51, "50 quarters between 2010 and 2022 plus the column names")
