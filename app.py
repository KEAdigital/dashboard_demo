#
# Imports
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output

import pandas as pd
import numpy as np
import openpyxl
import calendar

import plotly.express as px
import plotly.graph_objects as go

# Import af datamodel
# ***************************************
# Data import
# ***************************************
# 4 dataframes
githubpath = 'https://raw.githubusercontent.com/TueHellsternKea/dashdemo/main/data/'

# Import from Excel file, 4 different sheets
df_customers = pd.read_excel(githubpath + "fake_data.xlsx", sheet_name="customers")
df_order = pd.read_excel(githubpath + "fake_data.xlsx", sheet_name="order")
df_employee = pd.read_excel(githubpath + "fake_data.xlsx", sheet_name="employee")
df_products = pd.read_excel(githubpath + "fake_data.xlsx", sheet_name="products")

# Year - Create a dataframe with years usede in the order dataframe
df_year = df_order['orderdate'].dt.strftime("%Y").unique()

# Month - Create a dataframe with month names
months = []
for x in range(1, 13):
    months.append(calendar.month_name[x])

df_month = pd.DataFrame(months, columns=["monthnames"])

# Employee name
df_employee['emp_name'] = df_employee['firstname'] + ' ' + df_employee['lastname']

# Customers name
df_customers['cust_name'] = df_customers['first_name'] + ' ' + df_customers['last_name']

# Data - Add: total, order, year, month
df_order['total'] = df_order['unitprice'] * df_order['quantity']
df_order['deliverytime'] = df_order['deliverydate'] - df_order['orderdate']
df_order['orderyear'] = df_order['orderdate'].dt.strftime("%Y")
df_order['ordermonth'] = pd.to_datetime(df_order['orderdate'])
df_order['ordermonth'] = df_order['ordermonth'].dt.month_name()

# ***************************************
# Data - Relationer
# ***************************************
order = pd.merge(df_order, df_products, on='product_id')
order = pd.merge(order, df_employee, on='employee_id')
order = pd.merge(order, df_customers, on='customer_id')

# Order - Select colomns
order = order[['order_id', 
               'product_id', 'productname', 'type',
               'customer_id', 'cust_name', 'city', 'country',
               'employee_id', 'emp_name', 
               'orderdate', 'deliverydate', 'deliverytime', 'orderyear', 'ordermonth',
              'total']]


# ***************************************
# Diagram - Employee Sales
# ***************************************
fig_employee = px.bar(order, 
    x='emp_name', y='total', 
    color='type', text='total', title='Sales by Employee',
    hover_data=[],
    labels={'total':'Total sales', 'emp_name':'Employee', 'type':'Product Type'})
fig_employee.update_traces(texttemplate='%{text:.2s}', textposition='outside')
fig_employee.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', xaxis_tickangle=45)


# ***************************************
# Activate the app
# ***************************************
app = dash.Dash(__name__)

# ***************************************
# Layout
# ***************************************
app.layout = html.Div(
    children=[
        html.Div(className='row',
                children=[
                    html.Div(className='four columns div-user-controls',
                            children=[
                                html.H2('Sales dashboard'),
                                html.P('Select filters from dropdown'),

                    html.Div(children="Month", className="menu-title"),
                            dcc.Dropdown(
                                id='drop_month',
                                options=[{'label':selectmonth, 'value':selectmonth} for selectmonth in df_month['monthnames']],
                            ),
                    html.Div(children="Year", className="menu-title"),
                            dcc.Dropdown(
                                id='drop_year',
                                options=[{'label':selectyear, 'value':selectyear} for selectyear in df_year]
                            ),
                            ]
                    ),
                    html.Div(className='eight columns div-for-charts bg-grey',
                            children=[
                                #dcc.Graph(id="sales_employee", figure=fig_employee, config={"displayModeBar": False})
                                dcc.Graph(id="sales_employee", figure=fig_employee)
                            ]
                    ),
                ]
            )
        ]
)

# ***************************************
# Callbacks
# ***************************************
# Output er diagrammet
# Input er DropDown
@app.callback(Output('sales_employee', 'figure'),
              [Input('drop_month', 'value')],
              [Input('drop_year', 'value')])

def update_graph(drop_month, drop_year):
    if drop_month:
        order_month = order.loc[order['ordermonth'] == drop_month]
    else:
        order_month = order

    if drop_year:
        order_month = order.loc[order['orderyear'] == drop_year]
    else:
        order_month = order_month
        

    return {'data':[go.Bar(
        x = order_month['productname'],
        y = order_month['total']
            )
        ]
    }

# ***************************************
# Run the app
# ***************************************
if __name__ == '__main__':
    app.run_server(debug=True)