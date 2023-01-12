import datetime
from unittest import TestCase
from main import FinData


class TestFinData(TestCase):
    fin_data_test_subject = None

    def __init__(self, *args, **kwargs):
        super(TestFinData, self).__init__(*args, **kwargs)
        self.fin_data_test_subject = FinData()

    def test_get_revenue(self):
        revenue_data = self.fin_data_test_subject.get_revenue('AAPL', 2010, 1, 2022, 4)
        self.assertEqual(revenue_data.shape, (53, 4), "52 quarters between SOY 2010 and EOY 2022 plus the column names")
        # Relying on data from https://www.apple.com/newsroom/2017/01/apple-reports-record-first-quarter-results/ and
        # https://www.apple.com/newsroom/2016/10/apple-reports-fourth-quarter-results/
        # Quarter picked at random
        particular_quarter = revenue_data[revenue_data[:, 0] == "2017Q1"][0]
        self.assertAlmostEqual(particular_quarter[1]/1e9, 78.4, 1, "Checking revenue is as reported by Apple")
        self.assertEqual(particular_quarter[2], datetime.datetime(2016, 9, 25), "Checking start date for quarter")
        self.assertEqual(particular_quarter[3], datetime.datetime(2016, 12, 31), "Checking end date for quarter")

    def test_get_dates(self):
        date_data = self.fin_data_test_subject.get_dates('MSFT', 2011, 1, 2017, 4)
        self.assertEqual(date_data.shape, (29, 3), "28 quarters between SOY 2011 and EOY 2017 plus the column names")
        # Relying on data from:
        # https://www.microsoft.com/en-us/Investor/earnings/FY-2010-Q4/press-release-webcast
        # https://www.microsoft.com/en-us/Investor/earnings/FY-2011-Q1/press-release-webcast
        # https://www.microsoft.com/en-us/Investor/earnings/FY-2013-Q3/press-release-webcast
        # https://www.microsoft.com/en-us/Investor/earnings/FY-2013-Q4/press-release-webcast
        # https://www.microsoft.com/en-us/Investor/earnings/FY-2017-Q3/press-release-webcast
        # https://www.microsoft.com/en-us/Investor/earnings/FY-2017-Q4/press-release-webcast
        self.assertEqual(date_data[1][1], datetime.datetime(2010, 7, 1), "Checking the start of the array")
        self.assertEqual(date_data[1][2], datetime.datetime(2010, 9, 30), "Checking the start of the array")
        self.assertEqual(date_data[12][1], datetime.datetime(2013, 4, 1), "Checking the middle of the array")
        self.assertEqual(date_data[12][2], datetime.datetime(2013, 6, 30), "Checking the middle of the array")
        self.assertEqual(date_data[-1][1], datetime.datetime(2017, 4, 1), "Checking the end of the array")
        self.assertEqual(date_data[-1][2], datetime.datetime(2017, 6, 30), "Checking the end of the array")

    def test_get_cost_of_revenue(self):
        cor_data = self.fin_data_test_subject.get_cost_of_revenue('WMT', 2013, 2, 2019, 4)
        self.assertEqual(cor_data.shape, (28, 4), "27 quarters between 2013Q2 and EOY 2019 plus the column names")
