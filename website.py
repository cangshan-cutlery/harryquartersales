from flask import Flask, render_template, Markup,send_file
import pyodbc
import pandas as pd
import matplotlib.pyplot as plt
import io
app = Flask(__name__)


def get_data():
    conn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER=EVERWARE4\CBO;DATABASE=SBOCangshan;UID=rog;PWD=d4zNbvcw;Encrypt=optional')
    Query = pd.read_sql_query('SELECT GrosProfit,DocDate,CardName,CardCode FROM OINV', conn)
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
    extra = pivot_result
    extra = extra.drop('CardName', axis=1)
    extra = extra.drop('CardCode', axis=1)
    buffer = []
    for co1l in extra.columns:
        buffer.append(str(co1l))
    col = pivot_result.columns
    length = len(col)-2
    extra['Average'] = extra.sum(axis=1)/length
    extra['Newest_Element'] = extra.iloc[:, -2]
    extra['Project_Growth'] = extra['Newest_Element'] + extra['Average']
    extra = extra[["Average","Newest_Element","Project_Growth"]]
    result_df = pd.concat([pivot_result, extra], axis=1)
    
    
    return result_df,buffer


@app.route('/generate_excel')
def generate_excel():
    data,other = get_data()
    excel_buffer = io.BytesIO()
    excel_writer = pd.ExcelWriter(excel_buffer, engine='xlsxwriter')
    data.to_excel(excel_writer, sheet_name='Sheet1', index=False)
    excel_writer.close()
    excel_buffer.seek(0)
    return send_file(excel_buffer, download_name='data.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
@app.route('/')
def home():
    pivot_result,buffer = get_data()
    table_html = pivot_result.to_html(index=False, classes='table table-striped')
    return render_template('index.html', table=Markup(table_html), buffer = buffer)






if __name__ == '__main__':
    app.run(debug=True)


