from flask import Flask, render_template, Markup
import pyodbc
import pandas as pd

app = Flask(__name__)

def get_data():
    conn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER=EVERWARE4\CBO;DATABASE=SBOCangshan;UID=rog;PWD=d4zNbvcw;Encrypt=optional')
    Query = pd.read_sql_query('SELECT * FROM OINV', conn)
    money = Query['GrosProfit']
    date = pd.to_datetime(Query['DocDate'])
    customer = Query['CardName']
    card = Query['CardCode']

    result = pd.concat([customer, card, date, money], axis=1)
    result['Quarter'] = result['DocDate'].dt.to_period('Q')

    quarterly_earnings = result.groupby(['CardName', 'CardCode', 'Quarter'])['GrosProfit'].sum().reset_index()
    quarterly_earnings = quarterly_earnings.round({'GrosProfit': 2})
    pivot_result = quarterly_earnings.pivot(index=['CardName', 'CardCode'], columns='Quarter', values='GrosProfit').reset_index()

    pivot_result = pivot_result.rename_axis(None, axis=1)
    pivot_result = pivot_result.fillna(0)

    return pivot_result

@app.route('/')
def home():
    pivot_result = get_data()
    table_html = pivot_result.to_html(index=False, classes='table table-striped')
    return render_template('index.html', table=Markup(table_html))

if __name__ == '__main__':
    app.run(debug=True)