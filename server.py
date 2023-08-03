import pyodbc
import pandas as pd
import datetime

conn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER=EVERWARE4\CBO;DATABASE=SBOCangshan;UID=rog;PWD=d4zNbvcw;Encrypt=optional')
Query = pd.read_sql_query('SELECT * FROM OINV',conn)
money = Query['GrosProfit']
date = pd.to_datetime(Query['DocDate'])
customer = Query['CardName']
card = Query['CardCode']

result = pd.concat([customer, card, date, money], axis=1)
result['Quarter'] = result['DocDate'].dt.to_period('Q')

print(result.columns.tolist())

quarterly_earnings = result.groupby(['CardName', 'CardCode', 'Quarter'])['GrosProfit'].sum().reset_index()
quarterly_earnings = quarterly_earnings.round({'GrosProfit': 2})
pivot_result = quarterly_earnings.pivot(index=['CardName', 'CardCode'], columns='Quarter', values='GrosProfit').reset_index()

pivot_result = pivot_result.rename_axis(None, axis=1)
pivot_result = pivot_result.fillna(0)

pivot_result.to_excel('random.xlsx', index=False)
'''
total_dict = dict(zip(dat,mon))

print(total_dict)

projection = []
for i in range(4):
    total = (mon[i+5]/(mon[i]+1)) *mon[i+5]
    projection.append(total)

date = 1
projection_dict = {}
for i in range(0,4):
    projection_dict['2024Q'+str(date)] = projection[i]
    date+=1
print(projection_dict)
'''