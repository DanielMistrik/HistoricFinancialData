import datetime
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
        if data[i][2] is None:
            data[i][2] = data[i - 1][3] + datetime.timedelta(days=1) if i != 0 else data[i][2]
            data[i][3] = data[i + 1][2] - datetime.timedelta(days=1) if i != (len(data) - 1) else data[i][3]
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


"Filter for valid yearly and quarterly revenue data"
def yr_is_valid(item, min_year, max_year):
    return item["form"] == "10-K" and "fy" in item and "fp" in item and min_year <= int(item["fy"]) <= max_year and\
        330 < (dt.fromisoformat(item["end"]) - dt.fromisoformat(item["start"])).days < 380


def qr_is_valid(item, min_year, max_year):
    return "fp" in item and item["form"] in "10-Q/A" and min_year <= int(item["fy"]) <= max_year and "fy" in item\
                    and 60 < (dt.fromisoformat(item["end"]) - dt.fromisoformat(item["start"])).days < 100


"Return quarters marked by frame rather than year and quarter"
def get_frame_quarter_data(raw_output, min_year, max_year, found_qrtrs):
        frame_quarter_data = np.array([[item["frame"][2:], item["val"], dt.fromisoformat(item["start"]),
                            dt.fromisoformat(item["end"])] for item in raw_output["units"]["USD"] if "frame" in item \
                            and "Q" in item["frame"] and item["frame"][2:] not in found_qrtrs and "fy" in item \
                            and min_year <= int(item["frame"][2:6]) <= max_year])
        return frame_quarter_data


"Return quarters marked by year and quarter explicitly"
def get_explicit_quarter_data(raw_output, min_year, max_year):
    return np.array([[str(item["fy"]) + item["fp"], item["val"], dt.fromisoformat(item["start"]),
                      dt.fromisoformat(item["end"])] for item in raw_output["units"]["USD"] if
                     qr_is_valid(item, min_year, max_year)])


"Retrieves the financial data values from the url response from the start of the min_year up to the max_year"
def get_spec_data_given_url(url, min_year=0, max_year=3000, found_qrtrs=None):
    raw_output = get_url_data(url)
    # Create tables of quarterly and yearly revenues by parsng the raw output
    yearly_revenue = {str(item["fy"]): item["val"] for item in raw_output["units"]["USD"] if
                      yr_is_valid(item, min_year, max_year)}
    # Do we do an additional scrape of the data finding just quarter we couldn't before, if so found_qrtrs exists
    if found_qrtrs is None:
        quarterly_data = get_explicit_quarter_data(raw_output, min_year, max_year)
    else:
        quarterly_data = get_frame_quarter_data(raw_output, min_year, max_year, found_qrtrs)

    quarterly_data = unique(quarterly_data)
    return quarterly_data, yearly_revenue


"Fill the quarterly data given its own information, as a list, and information from the yearly data, a dictionary"
def fill_data(yearly_data, quarterly_data):
    # Filter data and make it unique as the above can return double counts
    _, unique_indices = np.unique(quarterly_data.astype(str)[:, 0], return_index=True, axis=0)
    value_data = np.take(quarterly_data, unique_indices, 0)
    # Fill in missing data
    value_data = fill_financial_data(yearly_data, value_data)
    value_data = fill_dates(value_data)
    return value_data


def get_value_and_yearly_data(cik, value_tags, min_year, max_year, found_qrtrs = None):
    value_data, yearly_data = None, {}
    # Some value tag words aren't found in certain company's income statements, so we cycle through possibilities
    for i in range(len(value_tags)):
        try:
            url = _sec_url.format(cik, value_tags[i])
            new_qtr_data, new_yr_data = get_spec_data_given_url(url, min_year-1, max_year+1, found_qrtrs)
            if new_qtr_data is not None and len(new_qtr_data) > 0 and len(new_qtr_data.shape) > 1:
                value_data = new_qtr_data if value_data is None else np.concatenate((value_data, new_qtr_data))
            yearly_data = yearly_data | new_yr_data
        except HttpError:
            pass
    return value_data, yearly_data


"Returns the number of quarters necessary for the given start and end dates in FY terms"
def get_number_of_quarters_necessary(start_year, start_quarter, end_year, end_quarter):
    return max(0, (end_year - start_year - 1)*4) + (5-start_quarter) + (end_quarter)


"Corrects the shape and cleans the array given the exact start and end dates"
def correct_output(value_data, min_year, min_quarter, max_year, max_quarter):
    value_data = np.fromiter(
        (x for x in value_data if is_in_date_bound(x[0], min_year, min_quarter, max_year, max_quarter)),
        dtype=value_data.dtype)
    return np.stack(value_data)


"Gets data from the list of value tags for a particular company, given its cik"
def get_data(cik, value_tags, data_name, min_year=0, min_quarter=0, max_year=3000, max_quarter=5):
    values = np.array(['Time-Period', data_name, 'Start of Quarter', 'End of Quarter'])
    value_data, yearly_data = get_value_and_yearly_data(cik, value_tags, min_year, max_year)
    # Fill data
    value_data = fill_data(yearly_data, value_data)
    value_data = correct_output(value_data, min_year, min_quarter, max_year, max_quarter)
    found_qrtrs = dict(zip(value_data[:, 0].flatten(), [1]*len(value_data[:, 0].flatten())))
    # Find any remaining data, add it and sort the result if something is missing
    if len(found_qrtrs) < get_number_of_quarters_necessary(min_year, min_quarter, max_year, max_quarter):
        new_value_data, _ = get_value_and_yearly_data(cik, value_tags, min_year, max_year, found_qrtrs)
        if new_value_data is not None:
            value_data = np.vstack([value_data, new_value_data])
            value_data = value_data[value_data[:, 0].argsort()]
    # Precisely filter value data according to given year and quarter constraints
    value_data = correct_output(value_data, min_year, min_quarter, max_year, max_quarter)
    values = np.vstack([values, value_data])
    return values
