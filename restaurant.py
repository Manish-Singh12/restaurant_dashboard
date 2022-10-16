# Import libraries
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import sqlite3 as sql

# Set dashboard page configuration
st.set_page_config(page_title='Restaurant analysis',page_icon='🍽️',layout='wide')

# Load Data
@st.cache(allow_output_mutation=True)
def load_data():
    try:
        global conn
        conn = sql.connect('restaurant.db')
        df_restro = pd.read_sql_query('select c.CustomerID,c.FirstName,c.LastName,c.Email,c.Address,c.City,c.State,c.Phone,c.Birthday,\
                                       c.FavoriteDish,o.OrderDate,od.DishID,d.Name as "Dish Name",d.Description,d.Price,d.Type\
                                       from Customers c\
                                       inner join Orders o\
                                       on c.CustomerID = o.CustomerID\
                                       inner join OrdersDishes od\
                                       on o.OrderID = od.OrderID\
                                       inner join Dishes d\
                                       on od.DishID = d.DishID;',conn)
        df_restro['Customer Name'] = df_restro['FirstName'] + ' ' + df_restro['LastName']
        df_restro.drop(columns=['FirstName','LastName'],inplace=True)

        df_dishes = pd.read_sql_query('select * from Dishes;',conn)

        df_two_customers = pd.read_sql_query('SELECT * FROM Customers\
                                            WHERE FirstName IN\
                                                (SELECT FirstName FROM Customers\
                                                 GROUP BY FirstName\
                                                 HAVING COUNT(*) > 1);',conn)

        df_customer_fav = pd.read_sql_query('select c.CustomerID,c.FirstName,c.LastName, c.Email,c.Address,c.City,c.State,c.Phone,c.Birthday,\
                                            c.FavoriteDish,d.Name as "Dish Name",d.Description,d.Price,d.Type\
                                            from Customers c\
                                            inner join Dishes d\
                                            on c.FavoriteDish = d.DishID;',conn)
        df_customer_fav['Customer Name'] = df_customer_fav['FirstName'] + ' ' + df_customer_fav['LastName']
        df_customer_fav.drop(columns=['FirstName','LastName'],inplace=True)

        return df_restro, df_dishes, df_two_customers, df_customer_fav

    except Exception as e:
        return e

df_restro, df_dishes, df_two_customers, df_customer_fav = load_data()

# Checking datatypes
#df_restro.dtypes

# Converting datatypes of date columns to date format
try:
    df_restro['Birthday'] = pd.to_datetime(df_restro['Birthday'])
    df_restro['OrderDate'] = pd.to_datetime(df_restro['OrderDate'])

except Exception as e:
    print(e)

# Checking missing values, if any
# df_restro.isnull().sum() 

# No missing values found.

# Engineer Data
@st.cache(allow_output_mutation=True)
def engineer_data():
    try:
        df_orders = df_restro[['OrderDate']].groupby([df_restro.OrderDate.dt.month,df_restro.OrderDate.dt.year]).count()
        s = df_orders.squeeze()
        s.index = ['{}_{}'.format(i,j) for i,j in s.index]
        df_orders_new = s.to_frame()
        df_orders_new.rename(columns={'OrderDate':'Numbers of orders'},inplace=True)

        df_order_quarter = df_restro.copy()
        df_order_quarter['OrderDate quarter'] = df_order_quarter['OrderDate'].dt.to_period('Q')
        quarter_orders = df_order_quarter[['Dish Name','OrderDate quarter']].groupby(['OrderDate quarter']).count()
        quarter_orders.rename(columns={'Dish Name':'Number of orders'},inplace=True)
        quarter_orders.reset_index(inplace=True)
        quarter_orders['OrderDate quarter'] = quarter_orders['OrderDate quarter'].astype(str)

        df_order_year = df_restro.copy()
        df_order_year['OrderDate year'] = df_order_year['OrderDate'].dt.isocalendar().year
        year_orders = df_order_year[['Dish Name','OrderDate year']].groupby(['OrderDate year']).count()
        year_orders.rename(columns={'Dish Name':'Number of orders'},inplace=True)
        year_orders.reset_index(inplace=True)
        year_orders['OrderDate year'] = year_orders['OrderDate year'].astype(str)

        df_customer = df_restro.copy()
        s1 = df_customer.groupby(['CustomerID','Customer Name'])['OrderDate'].diff(1).tolist()
        df_customer.insert(df_customer.shape[1],'Gap between order dates',s1)
        df_customer_1 = df_customer.copy()
        df_customer_1.replace('0 days 00:00:00',np.nan,inplace=True)

        return df_orders_new, quarter_orders, year_orders, df_customer, df_customer_1

    except Exception as e:
        return e

df_orders_new, quarter_orders, year_orders, df_customer, df_customer_1 = engineer_data()


# Build dashboard
# Add sidebar
try:
    add_sidebar = st.sidebar.selectbox('Aggregate or Individual customer',('Aggregate metrics', 'Individual customer analysis'))

except Exception as e:
    print(e)

try:
    if add_sidebar == 'Aggregate metrics':
        tab1, tab2, tab3, tab4 = st.tabs(['Basic Insights', 'Monthly Insights', 'Quarterly Insights', 'Yearly Insights'])

        with tab1:
            most_ordered_dish = df_restro[['Dish Name']].mode().iloc[0].values.tolist()
            most_ordered_dish.append(df_restro['Dish Name'].value_counts()[0])
            most_ordered_dish.append(df_restro[df_restro['Dish Name'] == df_restro['Dish Name'].mode()[0]]['Type'].unique()[0])
            most_ordered_dish.append(df_dishes[df_dishes['Name'] == most_ordered_dish[0]]['Price'].iloc[0])
            least_ordered_dish = []
            least_ordered_dish.append(df_restro['Dish Name'].value_counts().index[-1])
            least_ordered_dish.append(df_restro['Dish Name'].value_counts()[-1])
            least_ordered_dish.append(df_restro[df_restro['Dish Name'] == df_restro['Dish Name'].value_counts().index[-1]]['Type'].unique()[0])
            least_ordered_dish.append(df_dishes[df_dishes['Name'] == least_ordered_dish[0]]['Price'].iloc[0])
            dish_never_sold = []
            for i in df_dishes['Name'].to_list():
                if i not in df_restro[['Price','Dish Name']].groupby('Dish Name').first()['Price'].sort_values().index:
                    dish_never_sold.append(i)
                else:
                    continue

            dish_never_sold.append(df_dishes[df_dishes['Name'] == dish_never_sold[0]]['Type'].iloc[0])
            dish_never_sold.append(df_dishes[df_dishes['Name'] == dish_never_sold[0]]['Price'].iloc[0])
            dish_never_sold.append('_______________________')
            ordered_dishes = most_ordered_dish + least_ordered_dish + dish_never_sold
            most_and_least = pd.Series(ordered_dishes,index=['Most ordered dish','Most ordered dish count','Most ordered dish type',\
                                                             'Most ordered dish price', 'Least ordered dish','Least ordered dish count',\
                                                             'Least ordered dish type', 'Least ordered dish price', 'Dish never sold',\
                                                             'Dish never sold type', 'Dish never sold price', ' '])

            col1, col2, col3, col4 = st.columns(4)
            columns = [col1, col2, col3, col4]

            count = 0
            for i in most_and_least.index:
                with columns[count]:
                    st.metric(label=i,value=most_and_least[i])
                    count += 1
                    if count == 4:
                        count = 0
        

            with col1:
                fig2 = px.bar(x=df_restro[df_restro['Type'] == 'Main'].groupby('Dish Name')['Type'].count().sort_values(ascending=False).index,\
                             y=df_restro[df_restro['Type'] == 'Main'].groupby('Dish Name')['Type'].count().sort_values(ascending=False).tolist(),\
                             labels={'x':'Dish Name','y':'Number of times ordered'},title='Demographics of dishes ordered in main dish types',\
                             width=500,height=500)
                st.plotly_chart(figure_or_data=fig2)

            with col2:
                fig3 = px.bar(x=df_restro[df_restro['Type'] == 'Appetizer'].groupby('Dish Name')['Type'].count().sort_values(ascending=False).index,\
                            y=df_restro[df_restro['Type'] == 'Appetizer'].groupby('Dish Name')['Type'].count().sort_values(ascending=False).tolist(),\
                            labels={'x':'Dish Name','y':'Number of times ordered'},title='Demographics of dishes ordered in appetizer dish types',\
                            width=500,height=500)
                st.plotly_chart(figure_or_data=fig3)

            with col3:
                fig4 = px.bar(x=df_restro[df_restro['Type'] == 'Dessert'].groupby('Dish Name')['Type'].count().sort_values(ascending=False).index,\
                             y=df_restro[df_restro['Type'] == 'Dessert'].groupby('Dish Name')['Type'].count().sort_values(ascending=False).tolist(),\
                             labels={'x':'Dish Name','y':'Number of times ordered'},title='Demographics of dishes ordered in dessert dish types',\
                             width=500,height=500)
                st.plotly_chart(figure_or_data=fig4)

            with col4:   
                fig5 = px.bar(x=df_restro[df_restro['Type'] == 'Beverage'].groupby('Dish Name')['Type'].count().sort_values(ascending=False).index,\
                            y=df_restro[df_restro['Type'] == 'Beverage'].groupby('Dish Name')['Type'].count().sort_values(ascending=False).tolist(),\
                            labels={'x':'Dish Name','y':'Number of times ordered'},title='Demographics of dishes ordered in beverage dish types',
                            width=500,height=500)
                st.plotly_chart(figure_or_data=fig5)

            fig = px.bar(x=df_restro['Type'].value_counts().index,y=df_restro['Type'].value_counts().values,\
                          labels={'x':'Dish Type','y':'Number of times ordered'},title='Demographics of dish types ordered by customers',
                          width=900,height=700)
            st.plotly_chart(figure_or_data=fig)
    
            
            st.markdown('Two customers with same name:')
            st.table(df_two_customers)

        with tab2:
            col1, col2, col3 = st.columns(3)

            with col1:
                median_orders_monthly = int(df_orders_new['Numbers of orders'].median())
                st.metric(label='Median orders',value=median_orders_monthly)

            with col2:
                number_of_months_below_median = len(df_orders_new[df_orders_new['Numbers of orders'] < df_orders_new\
                                                    ['Numbers of orders'].median()])
                st.metric(label='Number of months having orders below median value',value=number_of_months_below_median)

            with col3:
                number_of_months_above_median = len(df_orders_new[df_orders_new['Numbers of orders'] >\
                                                                df_orders_new['Numbers of orders'].median()])
                st.metric(label='Number of months having orders above median value',\
                          value=number_of_months_above_median)
            
            df_orders_new['Percent change in orders'] = df_orders_new['Numbers of orders'].pct_change()
            fig6 = px.line(x=df_orders_new.index,y=df_orders_new['Numbers of orders'],\
                           labels={'x':'Month_year','y':'Number of orders'},title='Month vs Number of orders',width=900,height=700)
            st.plotly_chart(figure_or_data=fig6)

            fig7 = px.line(x=df_orders_new.index,y=df_orders_new['Percent change in orders'],\
                           labels={'x':'Month_Year','y':'Percent change in orders'},title='Month vs Percent change in orders',\
                           width=900,height=700)
            st.plotly_chart(figure_or_data=fig7)

        with tab3:
            col1, col2, col3 = st.columns(3)

            with col1:
                median_orders_quarterly = int(quarter_orders['Number of orders'].median())
                st.metric(label='Median orders',value=median_orders_quarterly)

            with col2:
                number_of_quarters_below_median = len(quarter_orders[quarter_orders['Number of orders'] < quarter_orders\
                                                    ['Number of orders'].median()])
                st.metric(label='Number of quarters having orders below median value',value=number_of_quarters_below_median)

            with col3:
                number_of_quarters_above_median = len(quarter_orders[quarter_orders['Number of orders'] >\
                                                                  quarter_orders['Number of orders'].median()])
                st.metric(label='Number of quarters having orders above median value',\
                          value=number_of_quarters_above_median)
                
            quarter_orders['Percent change in orders'] = quarter_orders['Number of orders'].pct_change()
             
            fig8 = px.line(x=quarter_orders['OrderDate quarter'],y=quarter_orders['Number of orders'],\
                           labels={'x':'Quarter','y':'Number of orders'},title='Quarter vs Number of orders',width=900,height=700)
            st.plotly_chart(figure_or_data=fig8)

            fig9 = px.line(x=quarter_orders['OrderDate quarter'],y=quarter_orders['Percent change in orders'],\
                           labels={'x':'Quarter','y':'Percent change in orders'},title='Quarter vs Percent change in orders',\
                           width=700,height=700)
            st.plotly_chart(figure_or_data=fig9)

        with tab4:
            col1, col2, col3 = st.columns(3)

            with col1:
                median_orders_yearly = int(year_orders['Number of orders'].median())
                st.metric(label='Median orders',value=median_orders_yearly)

            with col2:
                number_of_years_below_median = len(year_orders[year_orders['Number of orders'] < year_orders\
                                                    ['Number of orders'].median()])
                st.metric(label='Number of years having orders below median value',value=number_of_years_below_median)

            with col3:
                number_of_years_above_median = len(year_orders[year_orders['Number of orders'] >\
                                                                  year_orders['Number of orders'].median()])
                st.metric(label='Number of years having orders above median value',\
                          value=number_of_years_above_median)
            
            year_orders['Percent change in orders'] = year_orders['Number of orders'].pct_change()

            fig10 = px.line(x=year_orders['OrderDate year'],y=year_orders['Number of orders'],\
                           labels={'x':'Year','y':'Number of orders'},title='Year vs Number of orders',width=900,height=700)
            st.plotly_chart(figure_or_data=fig10)

            fig11 = px.line(x=year_orders['OrderDate year'],y=year_orders['Percent change in orders'],\
                           labels={'x':'Year','y':'Percent change in orders'},title='Year vs Percent change in orders',\
                           width=900,height=700)
            st.plotly_chart(figure_or_data=fig11)



    elif add_sidebar == 'Individual customer analysis':
        select_customer = st.number_input('Pick a customer:',1,100)

        df_customer_select = df_customer_fav[df_customer_fav['CustomerID'] == select_customer]
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            customer_name = df_customer_select['Customer Name'].unique()[0]
            st.metric(label='Customer name',value=customer_name) 

        with col2:
            customer_birthday = df_customer_select['Birthday'].unique()[0]
            st.metric(label='Birthday',value=customer_birthday)

        with col3:
            fav_dish = df_customer_select['Dish Name'].unique()[0]
            st.metric(label='Favorite Dish',value=fav_dish)

        with col4:
            fav_dish_type = df_customer_select['Type'].unique()[0]
            st.metric(label='Favorite dish type',value=fav_dish_type)       
        
        
        
        df_customer_select_new = df_customer[df_customer['CustomerID'] == select_customer]

        with col1:
            most_ordered = df_customer_select_new['Dish Name'].mode()[0]
            st.metric(label='Most ordered dish',value=most_ordered)

        with col2:
            most_ordered_type = df_customer_select_new['Type'].mode()[0]
            st.metric(label='Most ordered dish type',value=most_ordered_type)

        with col3:
            least_ordered = df_customer_select_new['Dish Name'].value_counts().index[-1]
            st.metric(label='Least ordered dish',value=least_ordered)

        with col4:
            least_ordered_type = df_customer_select_new['Type'].value_counts().index[-1]
            st.metric(label='Least ordered dish type',value=least_ordered_type)

        df_orders = pd.DataFrame({'OrderDate':df_customer_select_new['OrderDate'].value_counts().sort_index().index,'Number of orders':\
                                  df_customer_select_new['OrderDate'].value_counts().sort_index().values})
        df_orders['OrderDate'] = pd.to_datetime(df_orders['OrderDate'])
        s2 = df_customer_select_new['Gap between order dates'].value_counts().index
        df_orders.insert(2,'Gap between order dates',s2)
        df_orders.replace('0 days 00:00:00',np.nan,inplace=True)
        df_orders['Percent change in orders'] = df_orders['Number of orders'].pct_change()

        avg_dur_bet_orderdates = df_customer_1['Gap between order dates'].mean()
        avg_dur_bet_cust_orderdates = df_orders['Gap between order dates'].mean()

        if avg_dur_bet_cust_orderdates <= avg_dur_bet_orderdates:
            frequent = 'Yes'

        else:
            frequent = 'No'

        with col1:
            st.metric(label='Frequent customer or not',value=frequent)

        fig12 = px.line(x=df_orders['OrderDate'],y=df_orders['Number of orders'],labels={'x':'Order Date','y':'Number of orders'},\
                        title='Order Date vs Number of orders',width=900,height=700)
        st.plotly_chart(figure_or_data=fig12)

        fig13 = px.line(x=df_orders['OrderDate'],y=df_orders['Percent change in orders'],\
                           labels={'x':'Order Date','y':'Percent change in orders'},title='Order Date vs Percent change in orders',\
                           width=900,height=700)
        st.plotly_chart(figure_or_data=fig13)

except Exception as e:
    print(e)