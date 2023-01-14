import datetime
from unittest import TestCase
from main import FinData

"""
main.py - Testing script containing unit tests for all the public facing methods in main.py
"""


class TestFinData(TestCase):
    fin_data_test_subject = None

    def __init__(self, *args, **kwargs):
        super(TestFinData, self).__init__(*args, **kwargs)
        self.fin_data_test_subject = FinData()

    def _check_quarter_data(self, quarter_data, quarter_fy_date, expected_length, expected_width, size_msg,
                            quarter_value, value_accuracy, value_msg, quarter_start, quarter_end, divide_value=True):
        """Internal function to check the reported quarter by the library and actual quarter are the same"""
        self.assertEqual(quarter_data.shape, (expected_length, expected_width), size_msg)
        particular_quarter = quarter_data[quarter_data[:, 0] == quarter_fy_date][0]
        parsed_value = particular_quarter[1] / 1e9 if divide_value else particular_quarter[1]
        self.assertAlmostEqual(parsed_value, quarter_value, value_accuracy, value_msg)
        self.assertEqual(particular_quarter[2], quarter_start, "Checking start date for quarter")
        self.assertEqual(particular_quarter[3], quarter_end, "Checking end date for quarter")

    def test_get_revenue(self):
        revenue_data = self.fin_data_test_subject.get_revenue('AAPL', 2010, 1, 2022, 4)
        # Relying on data from https://www.apple.com/newsroom/2017/01/apple-reports-record-first-quarter-results/ and
        # https://www.apple.com/newsroom/2016/10/apple-reports-fourth-quarter-results/
        self._check_quarter_data(revenue_data, "2017Q1", 53, 4,
                                 "52 quarters between SOY 2010 and EOY 2022 plus the column names", 78.4, 1,
                                 "Checking revenue is as reported by Apple", datetime.datetime(2016, 9, 25),
                                 datetime.datetime(2016, 12, 31))

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
        # Relying on data from:
        # https://s201.q4cdn.com/262069030/files/doc_financials/2016/q4/Q4-FY16-press-release-final.pdf
        # https://s201.q4cdn.com/262069030/files/doc_financials/2016/q3/Press-Release.pdf
        self._check_quarter_data(cor_data, "2016Q4", 28, 4,
                                 "27 quarters between 2013Q2 and EOY 2019 plus the column names", 96.999, 3,
                                 "Checking Cost of Revenue is as reported by Walmart", datetime.datetime(2015, 11, 1),
                                 datetime.datetime(2016, 1, 31))

    def test_get_gross_profit(self):
        gp_data = self.fin_data_test_subject.get_gross_profit('TSLA', 2014, 1, 2021, 3)
        # Relying on data from:
        # https://tesla-cdn.thron.com/static/R3GJMT_TSLA_Q1_2021_Update_5KJWZA.pdf
        # https://www.sec.gov/ix?doc=/Archives/edgar/data/815097/000081509720000030/ccl-20200229.htm
        self._check_quarter_data(gp_data, "2020Q1", 32, 4,
                                 "31 quarters between SOY 2014 and 2021Q3 plus the column names", 1.234, 3,
                                 "Checking Gross Profit as reported by Tesla", datetime.datetime(2020, 1, 1),
                                 datetime.datetime(2020, 3, 31))

    def test_get_operating_income(self):
        oi_data = self.fin_data_test_subject.get_operating_income('CCL', 2012, 1, 2022, 1)
        # Relying on data from:
        # https://www.carnivalcorp.com/static-files/ed3fc7f1-5159-4cb8-8a04-c50fe937f589
        # https://www.carnivalcorp.com/static-files/edb95ca0-1883-4bb8-84c7-28ce4ed0f37d
        # https://www.carnivalcorp.com/static-files/65a2aae3-7fc1-4e9b-b5ed-ea730210984b
        self._check_quarter_data(oi_data, "2013Q3", 42, 4,
                                 "41 quarters between SOY 2012 and 2022Q1 plus the column names", 0.951, 3,
                                 "Checking Operating Income as reported by Carnival", datetime.datetime(2013, 6, 1),
                                 datetime.datetime(2013, 8, 31))

    def test_get_net_income(self):
        np_data = self.fin_data_test_subject.get_net_profit('NFLX', 2015, 1, 2019, 4)
        # Relying on data from:
        # https://www.cnbc.com/2019/01/16/netflix-earnings-q4-2018.html
        # http://q4live.s22.clientfiles.s3-website-us-east-1.amazonaws.com/959853165/files/doc_financials/quarterly_reports/2018/q4/01/FINAL-Q4-18-Shareholder-Letter.pdf
        # https://www.sec.gov/Archives/edgar/data/1065280/000106528018000538/nflx-093018x10qxdoc.htm
        self._check_quarter_data(np_data, "2018Q4", 21, 4, "20 quarters between SOY 2015 and 2019 EOY plus column names"
                                 , 0.134, 3, "Checking Net Profit as reported by Netflix",
                                 datetime.datetime(2018, 10, 1), datetime.datetime(2018, 12, 31))

    def test_get_eps(self):
        eps_basic_data = self.fin_data_test_subject.get_eps('MA', 2021, 1, 2021, 4)
        eps_diluted_data = self.fin_data_test_subject.get_eps('MA', 2020, 1, 2021, 4, is_diluted=True)
        # Relying on data from:
        # https://s25.q4cdn.com/479285134/files/doc_financials/2021/q2/2Q21-Mastercard-Earnings-Release.pdf
        # https://s25.q4cdn.com/479285134/files/doc_financials/2021/q2/Mastercard-06.30.2021-10-Q-as-filed-w-Exhibits.pdf
        self._check_quarter_data(eps_basic_data, "2021Q2", 5, 4, "4 quarters in one year plus column names"
                                 , 2.09, 2, "Checking Basic EPS as reported by Mastercard",
                                 datetime.datetime(2021, 4, 1), datetime.datetime(2021, 6, 30), divide_value=False)
        self._check_quarter_data(eps_diluted_data, "2021Q2", 9, 4, "8 quarters in two years plus column names"
                                 , 2.08, 2, "Checking Diluted EPS as reported by Mastercard",
                                 datetime.datetime(2021, 4, 1), datetime.datetime(2021, 6, 30), divide_value=False)

    def test_get_assets(self):
        asset_data = self.fin_data_test_subject.get_total_assets('F', 2009, 2, 2022, 2)
        # Relying on data from:
        # https://www.annualreports.com/HostedData/AnnualReportArchive/f/NYSE_F_2016.pdf
        self._check_quarter_data(asset_data, "2015Q4", 54, 4, "53 quarters from 2009Q2 to 2022Q2 plus column names"
                                 , 224.925, 3, "Checking Diluted EPS as reported by Mastercard",
                                 datetime.datetime(2015, 10, 1), datetime.datetime(2015, 12, 31))

    def test_get_liabilities(self):
        liab_data = self.fin_data_test_subject.get_total_liabilities('F', 2009, 3, 2022, 2)
        # Relying on data from:
        # https://www.annualreports.com/HostedData/AnnualReportArchive/f/NYSE_F_2016.pdf
        self._check_quarter_data(liab_data, "2015Q4", 53, 4, "52 quarters from 2009Q3 to 2022Q2 plus column names"
                                 , 196.174, 3, "Checking Diluted EPS as reported by Mastercard",
                                 datetime.datetime(2015, 10, 1), datetime.datetime(2015, 12, 31))

