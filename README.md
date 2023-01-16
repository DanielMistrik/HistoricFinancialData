# Historical Financial Data
# Introduction
A python library for historical financial data of publicly-traded companies using 
information provided by the SEC. The library can return important information from a 
companies financial statement such as revenue, net profit or eps (and much more).
The library returns data by quarter, as small a granularity
as possible for financial statements. The goal of this project was to provide a 
free resource for detailed and exact financial information on publicly traded companies
that stretch more than just a few quarters/years, like yfinance provides.

Reliability goes roughly as far as the middle of 2009 FY. Before that the data 
gets very sparse because they had different rules and formats for storing financial 
statements as well as unique data presentation.

# Rationale

## Quick Start (How-to-Guide)
```python
import HistoricalFinanceData as hfd

data_object = hfd.FinData()
```

# Limitations

# Future of the project (How you can help)

# Citations
Data courtesy of the SEC.