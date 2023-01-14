import requests
import json
import utils as ut
import numpy as np

"""
main.py - The public facing script which includes the main public class (FinData) and all the public, and useful, methods
"""


class FinData:
    # Defining fields to access and extract data from the SEC API
    _rev_jargon = ["SalesRevenueNet", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueGoodsNet",
                   "Revenues", "RevenueNet", "RevenuesNet"]
    _cor_jargon = ["CostOfGoodsAndServicesSold", "CostOfRevenue", "CostOfGoodsSold", "CostOfServicesSold"]
    _g_profit_jargon = ["GrossProfit"]
    _op_inc_jargon = ["OperatingIncomeLoss"]
    _cik_map_url = "https://www.sec.gov/files/company_tickers.json"
    _ticker_cik_map = {}
    _name_cik_map = {}
    _cik_ticker_map = {}

    "Helper function that fills in the various cik maps the SEC uses to classify company financials"
    def _fill_cik_map(self):
        r = requests.get(self._cik_map_url)
        json_output = json.loads(r.content.decode('utf-8'))
        i = 0
        while str(i) in json_output:  # The SEC returns an output of a dictionary with string numbers as keys
            ticker = json_output[str(i)]["ticker"]
            company_cir = str(json_output[str(i)]["cik_str"])
            company_cir = "0"*(10-len(company_cir))+company_cir # To make it compatible with SEC API calls
            self._ticker_cik_map[ticker] = company_cir
            self._cik_ticker_map[company_cir] = ticker
            i += 1

    def __init__(self):
        # Fills in mapping from human-understandable tickers to SEC identification numbers
        self._fill_cik_map()

    def get_revenue(self, ticker, start_year=0, start_quarter=0, end_year=3000, end_quarter=5):
        """
        get_revenue - Returns the revenue for the provided ticker in the optional date bounds. Works off of SEC 10-Q/A
        and 10-K fillings so for some companies, notably banks, the function wont be able to return revenue
        :param ticker: The stock market ticker identifying your company of interest as a string.
        :param start_year: The company's financial year you want to start data collection from as an integer
        :param start_quarter: The company's financial quarter you want to start data collection from as an integer
        :param end_year: The company's financial year you want to end data collection with as an integer (inclusive)
        :param end_quarter: The company's financial quarter you want to end data collection with as an integer (inclusive)
        :return: A numpy array with the first row being column names and the remainder being revenue data by quarter
        with the quarters being according to the companies financial calendar and may greatly differ from the normal
        calendar
        """
        cik = self._ticker_cik_map[ticker]
        return ut.get_data(cik, self._rev_jargon, 'Revenue', start_year, start_quarter, end_year, end_quarter)

    def get_dates(self, ticker, start_year=0, start_quarter=0, end_year=3000, end_quarter=5):
        """
        get_dates - Returns the exact dates each financial quarter, as defined by the company, falls into. Works off
        of SEC 10-Q/A and 10-K fillings so for some companies, notably banks, the function wont be able to return dates
        :param ticker: The stock market ticker identifying your company of interest as a string.
        :param start_year: The company's financial year you want to start data collection from as an integer
        :param start_quarter: The company's financial quarter you want to start data collection from as an integer
        :param end_year: The company's financial year you want to end data collection with as an integer (inclusive)
        :param end_quarter: The company's financial quarter you want to end data collection with as an integer (inclusive)
        :return: A numpy array with the first row being column names and the remainder being the start/end dates by
        quarter with the quarters being according to the companies financial calendar and may greatly differ from the
        normal calendar
        """
        cik = self._ticker_cik_map[ticker]
        # To maximize code re-use I am using the same set-up as with get_revenues and then deleting the revenues after
        raw_data = ut.get_data(cik, self._rev_jargon, None, start_year, start_quarter, end_year, end_quarter)
        filtered_data = np.delete(raw_data, 1, 1)
        return filtered_data

    def get_cost_of_revenue(self, ticker, start_year=0, start_quarter=0, end_year=3000, end_quarter=5):
        """
        get_cost_of_revenue - Returns the exact dates each financial quarter, as defined by the company, falls into.
        Works off SEC 10-Q/A and 10-K fillings so for some companies, notably banks, the function won't be able to
        return dates. Additionally, due to some companies' financial practices, not everyone documents strict cost of
        revenue
        :param ticker: The stock market ticker identifying your company of interest as a string.
        :param start_year: The company's financial year you want to start data collection from as an integer
        :param start_quarter: The company's financial quarter you want to start data collection from as an integer
        :param end_year: The company's financial year you want to end data collection with as an integer (inclusive)
        :param end_quarter: The company's financial quarter you want to end data collection with as an integer (inclusive)
        :return: A numpy array with the first row being column names and the remainder being the quarter data along with
        the cost of revenue with the quarters being according to the companies financial calendar and may greatly differ
        from the normal calendar
        """
        cik = self._ticker_cik_map[ticker]
        return ut.get_data(cik, self._cor_jargon, 'Cost of Revenue', start_year, start_quarter, end_year, end_quarter)

    def get_gross_profit(self, ticker, start_year=0, start_quarter=0, end_year=3000, end_quarter=5):
        """
        get_gross_profit - Returns the exact dates each financial quarter, as defined by the company, falls into. Works
        off SEC 10-Q/A and 10-K fillings so for some companies, notably banks, the function won't be able to return
        dates. Additionally, due to their financial practices, many companies don't record gross profit
        :param ticker: The stock market ticker identifying your company of interest as a string.
        :param start_year: The company's financial year you want to start data collection from as an integer
        :param start_quarter: The company's financial quarter you want to start data collection from as an integer
        :param end_year: The company's financial year you want to end data collection with as an integer (inclusive)
        :param end_quarter: The company's financial quarter you want to end data collection with as an integer (inclusive)
        :return: A numpy array with the first row being column names and the remainder being the quarter data along with
        the gross profit with the quarters being according to the companies financial calendar and may greatly differ
        from the normal calendar
        """
        cik = self._ticker_cik_map[ticker]
        return ut.get_data(cik, self._g_profit_jargon, 'Gross Profit', start_year, start_quarter, end_year, end_quarter)

    def get_operating_income(self, ticker, start_year=0, start_quarter=0, end_year=3000, end_quarter=5):
        cik = self._ticker_cik_map[ticker]
        return ut.get_data(cik, self._op_inc_jargon, 'Operating Income', start_year, start_quarter, end_year, end_quarter)

