import requests
import json
import utils as ut
import numpy as np
from exceptions import *

"""
main.py - The public facing script which includes the main public class (FinData) and all the public, and useful, methods
"""


class FinData:
    # Defining fields to access and extract data from the SEC API
    _rev_jargon = ["SalesRevenueNet", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueGoodsNet",
                   "Revenues", "RevenueNet", "RevenuesNet", "RevenuesNetOfInterestExpense"]
    _cor_jargon = ["CostOfGoodsAndServicesSold", "CostOfRevenue", "CostOfGoodsSold", "CostOfServicesSold"]
    _g_profit_jargon, _n_profit_jargon = ["GrossProfit"], ["NetIncomeLoss"]
    _op_inc_jargon = ["OperatingIncomeLoss"]
    _eps_basic_jargon, _eps_diluted_jargon = ["EarningsPerShareBasic"], ["EarningsPerShareDiluted"]
    _t_assets_jargon, _t_liab_jargon = ["Assets"], ["Liabilities"]
    _cik_map_url = "https://www.sec.gov/files/company_tickers.json"
    _ticker_cik_map = {}
    _name_cik_map = {}
    _cik_ticker_map = {}

    def _fill_cik_map(self):
        """Helper function that fills in the various cik maps the SEC uses to classify company financials"""
        r = requests.get(self._cik_map_url)
        json_output = json.loads(r.content.decode('utf-8'))
        i = 0
        while str(i) in json_output:  # The SEC returns an output of a dictionary with string numbers as keys
            ticker = json_output[str(i)]["ticker"]
            company_cir = str(json_output[str(i)]["cik_str"])
            company_cir = "0" * (10 - len(company_cir)) + company_cir  # To make it compatible with SEC API calls
            self._ticker_cik_map[ticker] = company_cir
            self._cik_ticker_map[company_cir] = ticker
            i += 1

    def _get_data(self, ticker, jargon_terms, data_title, start_year, start_quarter, end_year, end_quarter,
                  allow_negatives=True, ignore_warnings=False):
        """Helper function to retrieve the actual data for the public facing functions"""
        cik = self._ticker_cik_map[ticker]
        data = None
        try:
            data = ut.get_data(cik, jargon_terms, data_title, start_year, start_quarter, end_year, end_quarter,
                               allow_negatives)
        except NotFoundError:
            if not ignore_warnings:
                print("WARNING: The company you searched for does not file the necessary documents, 10-Q/A/K, to the "
                      "SEC so this library cannot return any financial data for it")
        return data

    def __init__(self):
        # Fills in mapping from human-understandable tickers to SEC identification numbers
        self._fill_cik_map()

    def get_revenue(self, ticker, start_year=0, start_quarter=0, end_year=3000, end_quarter=5, ignore_warnings=False):
        """
        get_revenue - Returns the revenue for the provided ticker in the optional date bounds. Works off of SEC 10-Q/A
        and 10-K fillings so for some companies, notably banks, the function wont be able to return revenue
        :param ticker: The stock market ticker identifying your company of interest as a string.
        :param start_year: The company's financial year you want to start data collection from as an integer
        :param start_quarter: The company's financial quarter you want to start data collection from as an integer
        :param end_year: The company's financial year you want to end data collection with as an integer (inclusive)
        :param end_quarter: The company's financial quarter you want to end data collection with as an integer (inclusive)
        :param ignore_warnings: Whether the function should not print warning messages, default is False
        :return: A numpy array with the first row being column names and the remainder being revenue data by quarter
        according to the companies financial calendar which may greatly differ from the normal calendar
        """
        return self._get_data(ticker, self._rev_jargon, 'Revenue', start_year, start_quarter, end_year, end_quarter,
                              ignore_warnings=ignore_warnings)

    def get_dates(self, ticker, start_year=0, start_quarter=0, end_year=3000, end_quarter=5, ignore_warnings=False):
        """
        get_dates - Returns the exact dates each financial quarter, as defined by the company, falls into. Works off
        of SEC 10-Q/A and 10-K fillings so for some companies, notably banks, the function wont be able to return dates
        :param ticker: The stock market ticker identifying your company of interest as a string.
        :param start_year: The company's financial year you want to start data collection from as an integer
        :param start_quarter: The company's financial quarter you want to start data collection from as an integer
        :param end_year: The company's financial year you want to end data collection with as an integer (inclusive)
        :param end_quarter: The company's financial quarter you want to end data collection with as an integer (inclusive)
        :param ignore_warnings: Whether the function should not print warning messages, default is False
        :return: A numpy array with the first row being column names and the remainder being the start/end dates by
        quarter with the quarters being according to the companies financial calendar which may greatly differ from the
        normal calendar
        """
        # To maximize code re-use I am using the same set-up as with get_revenues and then deleting the revenues after
        raw_data = self._get_data(ticker, self._rev_jargon, None, start_year, start_quarter, end_year, end_quarter,
                                  ignore_warnings=ignore_warnings)
        filtered_data = np.delete(raw_data, 1, 1)
        return filtered_data

    def get_cost_of_revenue(self, ticker, start_year=0, start_quarter=0, end_year=3000, end_quarter=5,
                            ignore_warnings=False):
        """
        get_cost_of_revenue - Returns the company's cost of revenue, per company financial quarter, for the provided
        time bounds. Works off SEC 10-Q/A and 10-K fillings so for some companies, notably banks, the function won't be
        able to return anything. Additionally, due to some companies' financial practices, not everyone documents strict
        cost of revenue so the function's behaviour with these companies is undocumented
        :param ticker: The stock market ticker identifying your company of interest as a string.
        :param start_year: The company's financial year you want to start data collection from as an integer
        :param start_quarter: The company's financial quarter you want to start data collection from as an integer
        :param end_year: The company's financial year you want to end data collection with as an integer (inclusive)
        :param end_quarter: The company's financial quarter you want to end data collection with as an integer (inclusive)
        :param ignore_warnings: Whether the function should not print warning messages, default is False
        :return: A numpy array with the first row being column names and the remainder being the quarter data along with
        the cost of revenue according to the companies financial calendar which may greatly differ from the normal
        calendar
        """
        return self._get_data(ticker, self._cor_jargon, 'Cost of Revenue', start_year, start_quarter, end_year,
                              end_quarter, ignore_warnings=ignore_warnings)

    def get_gross_profit(self, ticker, start_year=0, start_quarter=0, end_year=3000, end_quarter=5,
                         ignore_warnings=False):
        """
        get_gross_profit - Returns the company's gross profit, per company financial quarter, for the provided time
        bounds. Works off SEC 10-Q/A and 10-K fillings so for some companies, notably banks, the function won't be able
        to return anything. Additionally, due to their financial practices, many companies don't record gross profit
        :param ticker: The stock market ticker identifying your company of interest as a string.
        :param start_year: The company's financial year you want to start data collection from as an integer
        :param start_quarter: The company's financial quarter you want to start data collection from as an integer
        :param end_year: The company's financial year you want to end data collection with as an integer (inclusive)
        :param end_quarter: The company's financial quarter you want to end data collection with as an integer (inclusive)
        :param ignore_warnings: Whether the function should not print warning messages, default is False
        :return: A numpy array with the first row being column names and the remainder being the quarter data along with
        the gross profit according to the companies financial calendar which may greatly differ from the normal calendar
        """
        return self._get_data(ticker, self._g_profit_jargon, 'Gross Profit', start_year, start_quarter, end_year,
                              end_quarter, ignore_warnings=ignore_warnings)

    def get_operating_income(self, ticker, start_year=0, start_quarter=0, end_year=3000, end_quarter=5,
                             ignore_warnings=False):
        """
        get_operating_income - Returns the company's operating income, per company financial quarter, for the provided
        time. Works off SEC 10-Q/A and 10-K fillings so for some companies, notably banks, the function won't be able to
        return valid data and its behaviour with these companies is undocumented
        :param ticker: The stock market ticker identifying your company of interest as a string.
        :param start_year: The company's financial year you want to start data collection from as an integer
        :param start_quarter: The company's financial quarter you want to start data collection from as an integer
        :param end_year: The company's financial year you want to end data collection with as an integer (inclusive)
        :param end_quarter: The company's financial quarter you want to end data collection with as an integer (inclusive)
        :param ignore_warnings: Whether the function should not print warning messages, default is False
        :return: A numpy array with the first row being column names and the remainder being the quarter data along with
        the operating income according to the companies financial calendar which may greatly differ from the normal
        calendar
        """
        return self._get_data(ticker, self._op_inc_jargon, 'Operating Income', start_year, start_quarter, end_year,
                              end_quarter, ignore_warnings=ignore_warnings)

    def get_net_profit(self, ticker, start_year=0, start_quarter=0, end_year=3000, end_quarter=5,
                       ignore_warnings=False):
        """
        get_net_profit - Returns the company's net profit, per company financial quarter, for the provided time. Works
        off SEC 10-Q/A and 10-K fillings so for some companies, notably banks, the function won't be able to return
        valid data and its behaviour with these companies is undocumented
        :param ticker: The stock market ticker identifying your company of interest as a string.
        :param start_year: The company's financial year you want to start data collection from as an integer
        :param start_quarter: The company's financial quarter you want to start data collection from as an integer
        :param end_year: The company's financial year you want to end data collection with as an integer (inclusive)
        :param end_quarter: The company's financial quarter you want to end data collection with as an integer (inclusive)
        :param ignore_warnings: Whether the function should not print warning messages, default is False
        :return: A numpy array with the first row being column names and the remainder being the quarter data along with
        the net profit according to the companies financial calendar which may greatly differ from the normal calendar
        """
        return self._get_data(ticker, self._n_profit_jargon, 'Net Profit', start_year, start_quarter, end_year,
                              end_quarter, ignore_warnings=ignore_warnings)

    def get_eps(self, ticker, start_year=0, start_quarter=0, end_year=3000, end_quarter=5, is_diluted=False,
                ignore_warnings=False):
        """
        get_net_profit - Returns the company's earning per share (basic or diluted), per company financial quarter, for
        the provided time. Works off SEC 10-Q/A and 10-K fillings so for some companies, notably banks, the function
        won't be able to return valid data and its behaviour with these companies is undocumented.
        :param ticker: The stock market ticker identifying your company of interest as a string.
        :param start_year: The company's financial year you want to start data collection from as an integer
        :param start_quarter: The company's financial quarter you want to start data collection from as an integer
        :param end_year: The company's financial year you want to end data collection with as an integer (inclusive)
        :param end_quarter: The company's financial quarter you want to end data collection with as an integer (inclusive)
        :param is_diluted: Whether the EPS data returned is diluted or basic, default is basic.
        :param ignore_warnings: Whether the function should not print warning messages, default is False
        :return: A numpy array with the first row being column names and the remainder being the quarter data along with
        the EPS data according to the companies financial calendar which may greatly differ from the normal calendar
        """
        jargon_list = self._eps_diluted_jargon if is_diluted else self._eps_basic_jargon
        e_type = "Diluted" if is_diluted else "Basic"
        data = self._get_data(ticker, jargon_list, 'EPS (' + e_type + ')', start_year, start_quarter, end_year,
                              end_quarter, ignore_warnings=ignore_warnings)
        # Round the data to 2 dp as the filling and floating point approx error can leave a weird number
        data[1:, 1] = [np.round(x, 2) for x in data[1:, 1]]
        return data

    def get_total_assets(self, ticker, start_year=0, start_quarter=0, end_year=3000, end_quarter=5,
                         ignore_warnings=False):
        """
        get_total_assets - Returns the company's total assets, per company financial quarter, for the provided time.
        Works off SEC 10-Q/A and 10-K fillings so for some companies, notably banks, the function won't be able to
        return valid data and its behaviour with these companies is undocumented
        :param ticker: The stock market ticker identifying your company of interest as a string.
        :param start_year: The company's financial year you want to start data collection from as an integer
        :param start_quarter: The company's financial quarter you want to start data collection from as an integer
        :param end_year: The company's financial year you want to end data collection with as an integer (inclusive)
        :param end_quarter: The company's financial quarter you want to end data collection with as an integer (inclusive)
        :param ignore_warnings: Whether the function should not print warning messages, default is False
        :return: A numpy array with the first row being column names and the remainder being the quarter data along with
        the total assets according to the companies financial calendar which may greatly differ from the normal calendar
        """
        return self._get_data(ticker, self._t_assets_jargon, 'Total Assets', start_year, start_quarter, end_year,
                              end_quarter, allow_negatives=False, ignore_warnings=ignore_warnings)

    def get_total_liabilities(self, ticker, start_year=0, start_quarter=0, end_year=3000, end_quarter=5,
                              ignore_warnings=False):
        """
        get_total_liabilities - Returns the company's total liabilities, per company financial quarter, for the provided
        time. Works off SEC 10-Q/A and 10-K fillings so for some companies, notably banks, the function won't be able to
        return valid data and its behaviour with these companies is undocumented
        :param ticker: The stock market ticker identifying your company of interest as a string.
        :param start_year: The company's financial year you want to start data collection from as an integer
        :param start_quarter: The company's financial quarter you want to start data collection from as an integer
        :param end_year: The company's financial year you want to end data collection with as an integer (inclusive)
        :param end_quarter: The company's financial quarter you want to end data collection with as an integer (inclusive)
        :param ignore_warnings: Whether the function should not print warning messages, default is False
        :return: A numpy array with the first row being column names and the remainder being the quarter data along with
        the total liabilities according to the companies financial calendar which may greatly differ from the normal
        calendar
        """
        return self._get_data(ticker, self._t_liab_jargon, 'Total Liabilities', start_year, start_quarter, end_year,
                              end_quarter, allow_negatives=False, ignore_warnings=ignore_warnings)
