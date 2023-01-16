# Historical Financial Data

<table border=1 cellpadding=20><tr><td>

####  IMPORTANT LEGAL DISCLAIMER 

---

 **HistoricalFinancialData is not affiliated, endorsed, or vetted by the U.S Securities
 and Exchange Comission.** 
It's meant to be an open-source tool where projects can access detailed financial
information without having to pay for an external service.

As SEC data is considered **public information** it is free to use and dis-semintate, which
this project does.
For a more detailed description of the SEC's data-use policy please refer to their
**[website](https://www.sec.gov/privacy#dissemination)**

</td></tr></table>

## Introduction
A python library for historical financial data of publicly-traded companies using 
information provided by the SEC. The library can return important information from a 
companies financial statement such as revenue, net profit or eps (and much more).
The library returns data by quarter, as small a granularity
as possible for financial statements. The goal of this project was to provide a 
free resource for detailed and exact financial information on publicly traded companies
that stretch more than just a few quarters/years, like yfinance provides.

## Rationale

This project was started because while working on a trading side-project I noticed
barely any free sources of historical financial data I could use to backtest on. The
resources I could find were either paid, limited or only provided very broad data, i.e.
yearly revenue. 

Searching for a free resource I stumbled on the SEC's API which, through alot of reading
of 10-Q fillings, can be called on to return detailed financial information. This information, 
however, is returned in a very large and difficult to read json file and so I decided
to make a library that made the process simpler.

## Installation
To install the library you can either pip install it and then import it in 
your project like so:

`pip install HistoricalFinanceData`

Or you can clone this repository. You do so by going through the terminal to the
file location where you wish to store the library and then, after making sure git
is installed and initialized, run the following command:

`git clone https://github.com/DanielMistrik/HistoricFinancialData.git`
## Quick Start (How-to-Guide)
```python
import HistoricalFinanceData as hfd

# Always define a data object from which you can retrieve financial data
data_object = hfd.FinData()

# You can now call methods in the data object to retrieve historical financial information
data_object.get_revenue('AAPL', 2022, 1, 2022, 4, mute_warnings=False)

# Every method has roughly the same arguments. For their detailed description please refer to the documentation

# Only the first argument, the ticker, is required. With no time bound the function returns as much data as it can
data_object.get_revenue('AAPL')

# The other functions have the same arguments, and so I will ignore that part in their presentation
# Get other financial information
data_object.get_dates # As companies' financial quarters can differ dramatically from a normal calendar
data_object.get_cost_of_revenue
data_object.get_gross_profit
data_object.get_net_profit
data_object.get_total_assets
data_object.get_total_liabilities

# get_eps has the same arguments as the above but also includes one that determines which type, basic or diluted, is returned
data_object.get_eps('AAPL', is_diluted=True)

# All methods return a labeled 2d numpy array or None if no data is available 
```

## Limitations
Reliability only goes roughly as far as the middle of 2009 FY. Before that the data 
gets very sparse because they had different rules and formats for storing financial 
statements as well as unique data presentation.

Additionally, as this library exclusively uses data found in SEC 10-Q/A/K fillings, 
it can only return data for the companies that file these documents. Many companies,
notably non-US corporations like Toyota, do not submit these fillings and as such
the library will not return anything for them.

## Future of the project (How you can help)
This project only collects some of the financial data the SEC offers. Finding new 
types of financial data, which involves finding the US-GAAP tag for it and figuring
out whether the current library's data collection works for it, is a great way to 
expand the project, and I encourage you to reach out if you want to help with this.

While creating this library I have noticed that companies often have distinct corner-cases
with their data and patching any bugs caused by this is an ongoing battle so if you
notice any weird behaviour please document it as an issue on the project's github.

## Citations
Realized thanks to the numpy, datetime, requests, json, math and ratelimit libraries.

Data courtesy of the SEC.