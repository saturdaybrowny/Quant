import psycopg2
import pandas as pd
import plotly.offline as offline
import plotly.graph_objs as go

# Connect to an existing database
host = 'localhost'
dbname = 'sbt'
user = 'sbt'
pwd = 'sbt'
conn = psycopg2.connect('host={0} dbname={1} user={2} password={3}'.format(host, dbname, user, pwd))

df = pd.read_sql("SELECT name, date, open, high, low, close FROM daily_stock_price WHERE name='우리은행'", conn)

offline.init_notebook_mode(connected=True)

trace = go.Candlestick(x=df.date_time, open=df.open_price, high=df.high_price, low=df.low_price, close=df.close_price)

data = [trace]
layout = go.Layout(title='셀트리온 캔들차트')
fig = go.Figure(data=data, layout=layout)
offline.iplot(fig, filename="candlestick")
