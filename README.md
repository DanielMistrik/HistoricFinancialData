# Historical Financial Data
A python library for historical financial data of publicly-traded companies using 
information provided by the SEC. The library can return major information from a 
companies financial statement such as revenue, net profit or eps (and much more).
The library returns data on a quarterly level of granularity, or as small a granularity
as possible for financial statements. The goal of this project was to provide a 
free resource for detailed and exact financial information on publicly traded companies.

Reliability goes roughly as far as the middle of 2009 FY. Before that the data 
gets very sparse because they had different rules and formats for storing financial 
statements as well as unique data presentation.

`
data_object = FinData()
`
Data courtesy of the SEC.