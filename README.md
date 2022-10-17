
# Restaurant Analysis Dashboard with Streamlit 

In this project I have done some sort of analysis using python on restaurant data available in the 
format sqlite3 database. The tables has all detail of customer, order date, etc. I have
calculated aggregate metrics and individual customer analysis. And finally deploy this analysis using streamlit.

Live - https://manish-singh12-restaurant-dashboard-restaurant-ioruoi.streamlitapp.com/

 


## Project Organization

- .streamlit/config.toml : app page configuration
- restaurant.db : restaurant database (sqlite3)
- restaurant.py : python file (streamlit app)
- requirements.txt : libraries and packages 
## Restaurant Analysis

A restaurant is a business that prepares and serves food and drinks to customers. Meals are generally served and eaten on the premises, but nowadays, many restaurants also offer take-out and food delivery services.

Restaurants vary greatly in appearance and offerings, including a wide variety of cuisines and service models ranging from inexpensive fast-food restaurants and cafeterias to mid-priced family restaurants, to high-priced luxury establishments.

In this dashboard I have done analysis based on all cutomers collectively (Aggregate metrics) as well as individually (Individual customer analysis). 
## Overview

Aggregate metrics (First page): 

Select sidebar 'Aggregate metrics' to get the following insights.

- Basic Insights
- Monthly Insights
- Quarterly Insights
- Yearly Insights

Individual reader analysis (Second page):

Select sidebar 'Individual customer analysis' to get the insights about 
all individual readers.

- Click on plus to switch forward to next cusromer and minus to switch back to previous customer.


## Data available

- restaurant.db actually contains 9 tables but in this project I have taken use of 4 tables with the following schema:

![App Screenshot](https://github.com/Manish-Singh12/restaurant_dashboard/blob/main/restaurant_schema.png)


## Steps

- sqlite3.connect to connect the database.
- Python for filtering data.
- plotly.express for making charts.
- Streamlit for deployment.




## Libraries mostly used

- Streamlit
- Plotly
- sqlite3
- Pandas




## Screenshots

![App Screenshot](https://github.com/Manish-Singh12/restaurant_dashboard/blob/main/Screenshot%201.png)

![App Screenshot](https://github.com/Manish-Singh12/restaurant_dashboard/blob/main/Screenshot%202.png)


## Author

- [@manish](https://github.com/Manish-Singh12)
- LinkedIn - https://www.linkedin.com/in/manish-singh-pokhariya/

