import datetime
import pandas as pd
from datetime import datetime as dt
import requests
import json
import numpy as np
from exceptions import *

"""
utils.py - File for utility functions that largely originated as static methods in FinData. Not meant for use by the
           user. I guarantee no functionality or reliability for direct user.
"""
# Default API URL for SEC API
_sec_url = "https://data.sec.gov/api/xbrl/companyconcept/CIK{0}/us-gaap/{1}.json"

"Fills missing quarterly financial data given (complete) yearly data and (in-complete) quarterly data"
def fill_financial_data(yearly_revenue, quarterly_data):
    missng_qrtr_sum = {}
    # Find missing quarters:
    for quarter in quarterly_data:
        quarter_year = quarter[0][:4]
        if quarter_year in yearly_revenue:
            if quarter_year not in missng_qrtr_sum:
                missng_qrtr_sum[quarter_year] = 10  # 4+3+2+1 = 10
            missng_qrtr_sum[quarter_year] -= int(quarter[0][5])  # Subtract q-val so we can isolate missing quarter
            yearly_revenue[quarter_year] -= int(quarter[1])
    for year in yearly_revenue.keys():
        # Add quarter if it is the only one missing and all other quarters are accounted for in a given year
        if (yearly_revenue[year] >> 2) != 0 and year in missng_qrtr_sum and 0 < missng_qrtr_sum[year] < 5:
            new_quarter = np.array([str(year) + "Q" + str(missng_qrtr_sum[year]), yearly_revenue[year], None, None])
            quarterly_data = np.vstack([quarterly_data, new_quarter])
    # Re-sort the data so its sequential if non-empty and properly shaped
    if len(quarterly_data) > 0 and len(quarterly_data.shape) > 1:
        quarterly_data = quarterly_data[quarterly_data[:, 0].argsort()]
    return quarterly_data


"Retrieves SEC data given the complete URL in a json format"
def get_url_data(url):
    r = requests.get(url, headers={'User-Agent': 'Automated-Financial-Data-Library'})
    # Throw if the request was incorrect because of the revenue word
    match r.status_code:
        case 200:
            pass  # Everything is correct and we can proceed
        case 403:
            raise ForbiddenError("Request/URL was not found")
        case 404:
            raise NotFoundError("Request/URL was not found")
        case _:
            raise HttpError("Unknown error occured with request")
    json_output = json.loads(r.content.decode('utf-8'))
    return json_output


"Fills missing quarter dates, should be applied to the result of fill_financial_data which doesn't add dates"
def fill_dates(data):
    for i, quarter in enumerate(data):
        if data[i][2] is None and i != 0 and i != (len(data) - 1):
            data[i][2] = data[i - 1][3] + datetime.timedelta(days=1)
            data[i][3] = data[i + 1][2] - datetime.timedelta(days=1)
    return data


"The returned data is incredibly noisy with alot of incorrect inclusions, this makes the data correct and unique"
def unique(data):
    # It just so happens that the SEC data has alot of wrong (earlier) duplicates, the correct data is always last
    unique_quarter_data = {}
    for row in data:
        # We only want to keep the latest instance because of the above
        unique_quarter_data[row[0]] = row
    return np.array(list(unique_quarter_data.values()))


"Filter to clean data to the specifically requested bound"
def is_in_date_bound(string_date, min_year, min_quarter, max_year, max_quarter):
    given_yr = int(string_date[:4])
    given_qtr = int(string_date[5])
    return (min_year <= given_yr <= max_year) & (min_year < given_yr or min_quarter <= given_qtr) & \
            (given_yr < max_year or given_qtr <= max_quarter)


"Retrieves the financial data values from the url response from the start of the min_year up to the max_year"
def get_spec_data_given_url(url, min_year=0, max_year=3000):
    raw_output = get_url_data(url)
    # Filters for valid yearly and quarterly revenue
    def yr_is_valid(item):
        return item["form"] == "10-K" and "fy" in item and "fp" in item and min_year <= int(item["fy"]) <= max_year and\
        330 < (dt.fromisoformat(item["end"]) - dt.fromisoformat(item["start"])).days < 380
    def qr_is_valid(item):
        return item["form"] == "10-Q" and "fy" in item and "fp" in item and min_year <= int(item["fy"]) <= max_year and\
        60 < (dt.fromisoformat(item["end"]) - dt.fromisoformat(item["start"])).days < 100

    # Create tables of quarterly and yearly revenues by parsng the raw output
    yearly_revenue = {str(item["fy"]): item["val"] for item in raw_output["units"]["USD"] if yr_is_valid(item)}
    quarterly_data = np.array([[str(item["fy"]) + item["fp"], item["val"], dt.fromisoformat(item["start"]),
                      dt.fromisoformat(item["end"])] for item in raw_output["units"]["USD"] if qr_is_valid(item)])
    quarterly_data = unique(quarterly_data)
    # Fill gaps in the data
    quarterly_data = fill_financial_data(yearly_revenue, quarterly_data)
    quarterly_data = fill_dates(quarterly_data)
    return quarterly_data


"Gets data from the list of value tags for a particular company, given its cik"
def get_data(cik, value_tags, data_name, min_year=0, min_quarter=0, max_year=3000, max_quarter=5):
    values = np.array(['Time-Period', data_name, 'Start of Quarter', 'End of Quarter'])
    value_data = None
    # Some value tag words aren't found in certain company's income statements, so we cycle through possibilities
    for i in range(len(value_tags)):
        try:
            url = _sec_url.format(cik, value_tags[i])
            new_rev_data = get_spec_data_given_url(url, min_year, max_year)
            if new_rev_data is not None and len(new_rev_data) > 0 and len(new_rev_data.shape) > 1:
                value_data = new_rev_data if value_data is None else np.concatenate((value_data, new_rev_data))
        except HttpError:
            pass
    # Filter data and make it unique as the above can return double counts
    _, unique_indices = np.unique(value_data.astype(str)[:, 0], return_index=True, axis=0)
    value_data = np.take(value_data, unique_indices, 0)
    # Precisely filter value data according to given year and quarter constraints
    value_data = np.fromiter(
        (x for x in value_data if is_in_date_bound(x[0], min_year, min_quarter, max_year, max_quarter)), dtype=value_data.dtype)
    values = np.hstack([values, value_data])

    return values