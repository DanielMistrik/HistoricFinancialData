import datetime
from unittest import TestCase
from main import FinData


class TestFinData(TestCase):
    fin_data_test_subject = None

    def __init__(self, *args, **kwargs):
        super(TestFinData, self).__init__(*args, **kwargs)
        self.fin_data_test_subject = FinData()

    def test_get_revenue(self):
        revenue_data = self.fin_data_test_subject.get_revenue('AAPL',2010,1,2022,4)
        self.assertEqual(revenue_data.shape, (53, 4), "52 quarters between 2010 and 2022 plus the column names")
        # Relying on data from https://www.apple.com/newsroom/2017/01/apple-reports-record-first-quarter-results/ and
        # https://www.apple.com/newsroom/2016/10/apple-reports-fourth-quarter-results/
        # Quarter picked at random
        particular_quarter = revenue_data[revenue_data[:, 0] == "2017Q1"][0]
        self.assertAlmostEqual(particular_quarter[1]/1e9, 78.4, 1, "Checking revenue is as reported by Apple")
        self.assertEqual(particular_quarter[2], datetime.datetime(2016, 9, 25), "Checking start date for quarter")
        self.assertEqual(particular_quarter[3], datetime.datetime(2016, 12, 31), "Checking end date for quarter")
