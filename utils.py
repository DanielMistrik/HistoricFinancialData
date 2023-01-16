import datetime
from datetime import datetime as dt
from math import isclose
from ratelimit import limits
import requests
import json
import numpy as np
from exceptions import *

"""
utils.py - File for utility functions that largely originated as static methods in FinData. Not meant for use by the
           user. I guarantee no functionality or reliability for the direct user.
"""
# Default API URL for SEC API
sec_url = "https://data.sec.gov/api/xbrl/companyconcept/CIK{0}/us-gaap/{1}.json"
# Constants
ONE_DAY_DATETIME = datetime.timedelta(days=1)

"Fills missing quarterly financial data given (complete) yearly data and (in-complete) quarterly data"
def fill_financial_data(yearly_data, quarterly_data, allow_negatives):
    missng_qrtr_sum = {}
    # Find missing quarters:
    for quarter in quarterly_data:
        quarter_year = quarter[0][:4]
        if quarter_year in yearly_data:
            if quarter_year not in missng_qrtr_sum:
                missng_qrtr_sum[quarter_year] = 10  # 4+3+2+1 = 10
            missng_qrtr_sum[quarter_year] -= int(quarter[0][5])  # Subtract q-val so we can isolate missing quarter
            yearly_data[quarter_year] -= int(quarter[1]) if isinstance(quarter[1], int) else float(quarter[1])
    for year in yearly_data.keys():
        # Add quarter if it is the only one missing and all other quarters are accounted for in a given year
        if not isclose(yearly_data[year], 0, abs_tol=0.2) and year in missng_qrtr_sum \
                and 0 < missng_qrtr_sum[year] < 5 and (allow_negatives or yearly_data[year] > 0):
            new_quarter = np.array([str(year) + "Q" + str(missng_qrtr_sum[year]), yearly_data[year], None, None])
            quarterly_data = np.vstack([quarterly_data, new_quarter])
    # Re-sort the data so its sequential if non-empty and properly shaped
    if len(quarterly_data) > 0 and len(quarterly_data.shape) > 1:
        quarterly_data = quarterly_data[quarterly_data[:, 0].argsort()]
    return quarterly_data


"Retrieves SEC data given the complete URL in a json format"
@limits(calls=10, period=1)
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
            raise HttpError("Unknown error occurred with request")
    json_output = json.loads(r.content.decode('utf-8'))
    return json_output


"Fills missing quarter dates, should be applied to the result of fill_financial_data which doesn't add dates"
def fill_dates(data):
    for i, quarter in enumerate(data):
        if data[i][2] is None:
            data[i][2] = data[i - 1][3] + ONE_DAY_DATETIME if i != 0 else data[i][2]
            data[i][3] = data[i + 1][2] - ONE_DAY_DATETIME if i != (len(data) - 1) else data[i][3]
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


"""Sometimes the SEC reports financial quarters that are too late in the calendar year to be valid and
    and as such conflict with company data"""
def is_fy_date_frontrunning(start, fy, fp):
    if start.year > fy:
        return True
    if start.year == fy:
        latest_start = {"Q1":1, "Q2":4, "Q3":7, "Q4":10}
        if latest_start[fp] < start.month or (latest_start[fp] == start.month and start.day > 7):
            return True
        return False
    return False


"Filter for valid yearly and quarterly revenue data"
def yr_is_valid(item, min_year, max_year):
    return item["form"] == "10-K" and "fy" in item and "fp" in item and min_year <= int(item["fy"]) <= max_year and \
           ("start" not in item or 330 < (dt.fromisoformat(item["end"]) - dt.fromisoformat(item["start"])).days < 380)


def qr_is_valid(item, min_year, max_year):
    return "fp" in item and item["form"] in "10-Q/A" and min_year <= int(item["fy"]) <= max_year and "fy" in item \
           and ("start" not in item or \
                (60 < (dt.fromisoformat(item["end"]) - dt.fromisoformat(item["start"])).days < 100 and \
                not is_fy_date_frontrunning(dt.fromisoformat(item["start"]), item["fy"], item["fp"])))


"Return quarters marked by frame rather than year and quarter"
def get_frame_quarter_data(raw_output, min_year, max_year, found_qrtrs, value_list_name):
        frame_quarter_data = np.array([[item["frame"][2:8], item["val"],(dt.fromisoformat(item["start"])
                                if "start" in item else None), dt.fromisoformat(item["end"])]
                                for item in raw_output["units"][value_list_name] if "frame" in item and
                                "Q" in item["frame"] and item["frame"][2:] not in found_qrtrs and "fy" in item
                                and min_year <= int(item["frame"][2:6]) <= max_year])
        return frame_quarter_data


"Return quarters marked by year and quarter explicitly"
def get_explicit_quarter_data(raw_output, min_year, max_year, value_list_name):
    return np.array([[str(item["fy"]) + item["fp"], item["val"], (dt.fromisoformat(item["start"]) if "start" in item
                    else None), dt.fromisoformat(item["end"])] for item in raw_output["units"][value_list_name] if
                    qr_is_valid(item, min_year, max_year)])


"Function that appends 2d np arrays which can be None"
def safe_np_append(main_data, additional_data):
    if additional_data is not None and len(additional_data):
        main_data = additional_data if main_data is None or not len(main_data) else \
            np.vstack([main_data, additional_data])
    return main_data


"Given a sorted value data 2d np array it returns the missing time periods"
def get_missing_time_periods(data):
    missing_time_periods, last_date = None, None
    average_quarter_length = None
    # Iterate over quarters and record the gaps between them, a missing time period which is likely a missing quarter
    for quarter_info in data:
        if last_date is not None and quarter_info[2] is not None and (quarter_info[2] - last_date).days > 1:
            new_data = np.array([last_date+ONE_DAY_DATETIME, quarter_info[2]-ONE_DAY_DATETIME])
            missing_time_periods = safe_np_append(missing_time_periods, new_data)
        if last_date is not None and (quarter_info[3] - last_date).days < 95 and average_quarter_length is None:
            average_quarter_length = (quarter_info[3] - last_date - ONE_DAY_DATETIME).days
        last_date = quarter_info[3]
    # Add a last date as the function calling this will always work on whole years and as such ignore the last Q4
    if last_date is not None:
        end_of_latest_quarter = last_date + datetime.timedelta(days=average_quarter_length)
        latest_quarter = np.array([last_date+ONE_DAY_DATETIME, end_of_latest_quarter])
        missing_time_periods = safe_np_append(missing_time_periods, latest_quarter)
    return missing_time_periods


"Returns quarterly data that matches the time periods and most of the qr_is_valid() conditions except the form req"
def get_quarterly_data_from_time_periods(raw_output, time_periods, value_list_name, end_date_to_new_start_date_map):
    missing_data = None
    for item in raw_output["units"][value_list_name]:
        end_date = dt.fromisoformat(item["end"])
        # Skip data we can't find a start date for
        if "start" not in item and end_date not in end_date_to_new_start_date_map:
            continue
        start_date = dt.fromisoformat(item["start"]) if "start" in item else end_date_to_new_start_date_map[end_date]
        if np.array([start_date, end_date]) in time_periods and 'fy' in item \
                and 60 < (end_date - start_date).days < 100 and 'fp' in item \
                and not is_fy_date_frontrunning(start_date, item["fy"], "Q4"):
            new_data = [np.array([str(end_date.year)+"Q4", item["val"], start_date, end_date])]
            # Sometimes we only find a date that fills a part of a larger whole so we re-adapt the missing interval
            if len(time_periods[time_periods != np.array([start_date, end_date])])%2:
                time_periods = safe_np_append(time_periods, np.array([start_date, end_date + ONE_DAY_DATETIME]))
            time_periods = np.sort(time_periods[time_periods != np.array([start_date, end_date])]).reshape(-1,2)
            missing_data = safe_np_append(missing_data, new_data)
    # Return the found missing data as well as the time periods we couldn't find data for
    return unique(missing_data) if missing_data is not None else None, time_periods if len(time_periods) else None


"Fill in start dates if they are not provided, assumes end date always provided"
def fill_start_dates(data):
    average_quarter_length, last_date = None, None
    end_date_to_new_start_date_map = {}
    # Iterate over quarters and finds the quarter length
    for quarter_info in data:
        if last_date is not None and quarter_info[2] is None and (quarter_info[3] - last_date).days < 95:
            average_quarter_length = (quarter_info[3] - last_date - ONE_DAY_DATETIME).days
            quarter_info[2] = last_date + ONE_DAY_DATETIME
            end_date_to_new_start_date_map[quarter_info[3]] = quarter_info[2]
        last_date = quarter_info[3]
    # Add start dates that couldn't be added above because of missing Q4's or because it is the first quarter reported
    for quarter_info in data:
        if quarter_info[2] is None and average_quarter_length is not None:
            is_leap_year = (quarter_info[3].year % 400 == 0) and (quarter_info[3].year % 100 == 0)
            is_leap_year = is_leap_year or ((quarter_info[3].year % 4 ==0) and (quarter_info[3].year % 100 != 0))
            quarter_info[2] = quarter_info[3] - datetime.timedelta(days=average_quarter_length - 2 + is_leap_year)
            end_date_to_new_start_date_map[quarter_info[3]] = quarter_info[2]
    return data, end_date_to_new_start_date_map


"Retrieves the financial data values from the url response from the start of the min_year up to the max_year"
def get_spec_data_given_url(url, min_year=0, max_year=3000, found_qrtrs=None, missing_time_periods = None, raw_data=None):
    raw_output = get_url_data(url) if raw_data is None else raw_data
    value_list_name = list(raw_output["units"].keys())[0] # Always only one key so order/indicies don't matter
    # Create tables of quarterly and yearly revenues by parsing the raw output
    yearly_revenue = {str(item["fy"]): item["val"] for item in raw_output["units"][value_list_name] if
                      yr_is_valid(item, min_year, max_year)}
    # Do we do an additional scrape of the data finding just quarter we couldn't before, if so found_qrtrs exists
    if found_qrtrs is None:
        quarterly_data = get_explicit_quarter_data(raw_output, min_year, max_year, value_list_name)
        quarterly_data = unique(quarterly_data)
        quarterly_data, end_date_to_new_start_date_map = fill_start_dates(quarterly_data)
        new_missing_time_periods = get_missing_time_periods(quarterly_data)
        missing_time_periods = safe_np_append(missing_time_periods, new_missing_time_periods)
        if missing_time_periods is not None:
            missing_data, missing_time_periods = get_quarterly_data_from_time_periods(raw_output, missing_time_periods,
                                                                    value_list_name, end_date_to_new_start_date_map)
            if missing_data is not None:
                quarterly_data = safe_np_append(quarterly_data, missing_data)
                quarterly_data = quarterly_data[quarterly_data[:, 0].argsort()]
    else:
        quarterly_data = get_frame_quarter_data(raw_output, min_year, max_year, found_qrtrs, value_list_name)
        quarterly_data, _ = fill_start_dates(quarterly_data)
        quarterly_data = unique(quarterly_data)
    return quarterly_data, yearly_revenue, missing_time_periods, raw_output


"Fill the quarterly data given its own information, as a list, and information from the yearly data, a dictionary"
def fill_data(yearly_data, quarterly_data, allow_negatives):
    # Filter data and make it unique as the above can return double counts
    _, unique_indices = np.unique(quarterly_data.astype(str)[:, 0], return_index=True, axis=0)
    value_data = np.take(quarterly_data, unique_indices, 0)
    # Fill in missing data
    value_data = fill_financial_data(yearly_data, value_data, allow_negatives)
    value_data = fill_dates(value_data)
    return value_data


"Given value tags, it returns the quarterly and yearly data"
def get_value_and_yearly_data(cik, value_tags, min_year, max_year, found_qrtrs = None, raw_data = None):
    value_data, missing_time_periods, yearly_data, cur_raw_data = None, None, {}, {}
    # If we don't have the raw data from the SEC then we need to do the whole process of retrieving it
    if raw_data is None:
        # Some value tag words aren't found in certain company's income statements, so we cycle through possibilities
        for i in range(len(value_tags)):
            try:
                url = sec_url.format(cik, value_tags[i])
                new_qtr_data, new_yr_data, missing_time_periods, new_raw_data = \
                    get_spec_data_given_url(url, min_year-1, max_year+1, found_qrtrs, missing_time_periods)
                cur_raw_data = cur_raw_data | new_raw_data
                if new_qtr_data is not None and len(new_qtr_data) > 0 and len(new_qtr_data.shape) > 1:
                    value_data = new_qtr_data if value_data is None else np.concatenate((value_data, new_qtr_data))
                yearly_data = yearly_data | new_yr_data
            except HttpError:
                pass
    # As we have the data we just parse it. As we only use this to find isolated data, yearly info isn't needed
    else:
        # No need for try-except block as we aren't hitting an API like above
        new_qtr_data, _, _, _ = \
            get_spec_data_given_url(None, min_year - 1, max_year + 1, found_qrtrs, None, raw_data)
        if new_qtr_data is not None and len(new_qtr_data) > 0 and len(new_qtr_data.shape) > 1:
            value_data = new_qtr_data

    return value_data, yearly_data, cur_raw_data


"Returns the number of quarters necessary for the given start and end dates in FY terms"
def get_number_of_quarters_necessary(start_year, start_quarter, end_year, end_quarter):
    return (end_year - start_year - 1)*4 + (5-start_quarter) + (end_quarter)


"Corrects the shape and cleans the array given the exact start and end dates"
def correct_output(value_data, min_year, min_quarter, max_year, max_quarter):
    value_data = np.fromiter(
        (x for x in value_data if is_in_date_bound(x[0], min_year, min_quarter, max_year, max_quarter)),
        dtype=value_data.dtype)
    return np.stack(value_data)


"Gets data from the list of value tags for a particular company, given its cik"
def get_data(cik, value_tags, data_name, min_year=0, min_quarter=0, max_year=3000, max_quarter=5, allow_negatives=True):
    values = np.array(['Time-Period', data_name, 'Start of Quarter', 'End of Quarter'])
    value_data, yearly_data, raw_data = get_value_and_yearly_data(cik, value_tags, min_year, max_year)
    if value_data is None: # No data was found (Some companies, primarily non-US, like Toyota)
        raise NotFoundError()
    relevant_value_data = correct_output(value_data, min_year, min_quarter, max_year, max_quarter)
    found_qrtrs = dict(zip(relevant_value_data[:, 0].flatten(), [1]*len(relevant_value_data[:, 0].flatten())))
    # Find any remaining data, add it and sort the result if something is missing
    if len(found_qrtrs) < get_number_of_quarters_necessary(min_year, min_quarter, max_year, max_quarter):
        new_value_data, _, _ = get_value_and_yearly_data(cik, value_tags, min_year, max_year, found_qrtrs, raw_data)
        if new_value_data is not None:
            value_data = np.vstack([value_data, new_value_data])
            value_data = value_data[value_data[:, 0].argsort()]
    # Fill data - Last step (even though not as slow) because here we are approximating and calculating ourselves so we
    # first want to fill any data that actually comes from the SEC
    value_data = fill_data(yearly_data, value_data, allow_negatives)
    # Precisely filter value data according to given year and quarter constraints
    value_data = correct_output(value_data, min_year, min_quarter, max_year, max_quarter)
    values = np.vstack([values, value_data])
    return values
