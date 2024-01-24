
import pandas as pd
from datetime import datetime, timedelta
from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
import re
import math
import talib as ta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


import warnings
warnings.filterwarnings('ignore')

#All the stock symbols
def nepse_symbols():
    path = 'https://merolagani.com/LatestMarket.aspx'
    r = requests.get(path,headers={'User-Agent': 'Chrome/108.0.0.0'})
    print(r.status_code)
    #Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36

    #creating a beautiful soup object
    bs = BeautifulSoup(r.content,'html.parser')
    tables = bs.find_all('table',attrs={'class': 'table table-hover live-trading sortable'})
    clean_string = re.sub('[0-9.]', '', tables[0].text)
    lines =clean_string.split('\n')


    # Remove empty lines
    lines = [line for line in lines if line.strip()]

    # Extract the alphabets between '\n' and '\n' and store them in a list
    results = [line.strip() for line in lines[1:]]
    modified_list = [element.replace('-', '') for element in results]
    stock_symbols = [element.replace(',','') for element in modified_list]

    return stock_symbols


















#Get the dataframe

def custom_business_week_mean(values):
    # Filter out Saturdays
    working_days = values[values.index.dayofweek != 5]
    return working_days.mean()

#function to read stock data from Nepalipaisa.com api
def stock_dataFrame(stock_symbol,start_date='2023-01-01',weekly=False):
  """
  input : stock_symbol
            start_data set default at '2020-01-01'
            weekly set default at False 
  output : dataframe of daily or weekly transactions
  """
  #print(end_date)
  today = datetime.today()
  # Calculate yesterday's date
  yesterday = today - timedelta(days=1)

  # Format yesterday's date
  formatted_yesterday = yesterday.strftime('%Y-%-m-%-d')
  print(formatted_yesterday)


  path = f'https://www.nepalipaisa.com/api/GetStockHistory?stockSymbol={stock_symbol}&fromDate={start_date}&toDate={formatted_yesterday}&pageNo=1&itemsPerPage=10000&pagePerDisplay=5&_=1686723457806'
  df = pd.read_json(path)
  theList = df['result'][0]
  df = pd.DataFrame(theList)
  #reversing the dataframe
  df = df[::-1]

  #removing 00:00:00 time
  #print(type(df['tradeDate'][0]))
  df['Date'] = pd.to_datetime(df['tradeDateString'])

  #put date as index and remove redundant date columns
  df.set_index('Date', inplace=True)
  columns_to_remove = ['tradeDate', 'tradeDateString','sn']
  df = df.drop(columns=columns_to_remove)

  new_column_names = {'maxPrice': 'High', 'minPrice': 'Low', 'closingPrice': 'Close','volume':'Volume','previousClosing':"Open"}
  df = df.rename(columns=new_column_names)

  if(weekly == True):
     weekly_df = df.resample('W').apply(custom_business_week_mean)
     weekly_df = weekly_df.round(1)
     df = weekly_df


  return df


#On Balance Volume
def obv_column(company_df):
  length = len(company_df)
  #print(length)
  OBV = 0
  obv_daily = []
  for i in range(length-1):
    if(company_df['Close'][i+1] > company_df['Close'][i]):
      OBV = OBV + company_df['Volume'][i+1]
      obv_daily.append(OBV)
    elif (company_df['Close'][i+1] < company_df['Close'][i]):
      OBV = OBV - company_df['Volume'][i+1]
      obv_daily.append(OBV)
    else:
      OBV = OBV
      obv_daily.append(OBV)
  company_df2 = company_df
  # Drop first row
  company_df2.drop(index=company_df2.index[0],
        axis=0,
        inplace=True)

  company_df2['OBV'] = obv_daily
  #print(len(company_df2))
  return company_df2

def buy_sell_obv(company_df):
  company_df2 = company_df
  length = len(company_df2)
  #print(length)
  buy_sell = []
  signal = 0
  for i in range(length-1):
    if (company_df2['OBV'][i+1]>company_df2['OBV'][i]):
      signal = "Buy"
      buy_sell.append(signal)
    elif (company_df2['OBV'][i+1] < company_df2['OBV'][i]):
      signal = "Sell"
      buy_sell.append(signal)
    else:
      signal = "Hold"
      buy_sell.append(signal)

  company_df3 = company_df2
  # Drop first row
  company_df3.drop(index=company_df3.index[0], axis=0, inplace=True)
  #print(len(buy_sell))
  company_df3['Buy_Sell'] = buy_sell
  #print(len(company_df3))
  return company_df3

def profit_obv(company_df,seed_money=10000):
  company_df3 = company_df
  length = len(company_df3)
  money = seed_money
  shares = 0
  last_buy_price = 0
  flag = 0
  for i in range(length):
    if((company_df3['Buy_Sell'][i] == "Buy")&(flag == 0)):
      #print('Buying share at: ')
      #print(company_df3['Close'][i])
      #print('Date: ')
      #print(company_df3.index[i])
      shares = math.floor(money/company_df3['Close'][i])
      #print(shares)
      money = money - shares*company_df3['Close'][i]
      last_buy_price = company_df3['Close'][i]
      #print(money)
      #print('\n')
      flag = 1

    elif((company_df3['Buy_Sell'][i] == "Sell")  & (flag == 1)):
      #print('Selling share at: ')
      #print(company_df3['Close'][i])
      new_money = shares*company_df3['Close'][i]
      shares = 0
      #print(new_money)
      money = money + new_money
      #print(money)
      #print('\n\n')
      flag = 0

  final_money = round(shares*company_df3['Close'][-1] + money,1)
  return [final_money,shares,money]

def plot_obv_graph(df):
  print("generating plot for obv")
  obv_df = df
  df_to_plot = obv_df.iloc[:,-2:]
  df_to_plot = df_to_plot.reset_index()
  print(df_to_plot)
  fig = px.line(df_to_plot,x='Date',y='OBV',title="OBV Chart with Buy/Sell Markers")

  #Add Markers for Buy and Sell events
  buy_events = df_to_plot[df_to_plot["Buy_Sell"]=="Buy"]
  sell_events = df_to_plot[df_to_plot["Buy_Sell"] == "Sell"]

  #Add traces directly from the Dataframe
  fig.add_trace(go.Scatter(x=buy_events['Date'],y=buy_events['OBV'],
                            mode='markers',marker=dict(color='blue',symbol='circle-dot'),
                            name='Buy'))
  fig.add_trace(go.Scatter(x=sell_events['Date'],y=sell_events['OBV'],
                            mode='markers',marker=dict(color='red',symbol='x'),
                            name='Sell'))
  fig.update_layout(showlegend=False)
  # Increase the height of the figure
  fig.update_layout(height=600)

  plot_obv = fig.to_html(full_html=False)

  return plot_obv



#Japanese candle stick
def jcs_signals(df):
 
  for i in range(2,df.shape[0]):
 
    current = df.iloc[i,:]

    prev = df.iloc[i-1,:]
    prev_2 = df.iloc[i-2,:]

    realbody = abs(current['Open'] - current['Close'])
    candle_range = current['High'] - current['Low']

    idx = df.index[i]

    # Bullish swing
    df.loc[idx,'Bullish swing'] = current['Low'] > prev['Low'] and prev['Low'] < prev_2['Low']
    
    # Bearish swing
    df.loc[idx,'Bearish swing'] = current['High'] < prev['High'] and prev['High'] > prev_2['High']

    # # Bullish engulfing
    # df.loc[idx,'Bullish engulfing'] = current['High'] > prev['High'] and current['Low'] < prev['Low'] and realbody >= 0.8 * candle_range and current['Close'] > current['Open']

    # # Bearish engulfing
    # df.loc[idx,'Bearish engulfing'] = current['High'] > prev['High'] and current['Low'] < prev['Low'] and realbody >= 0.8 * candle_range and current['Close'] < current['Open']


  return df

def buy_sell_jcs(df):
  
  company_df = df.dropna()
  # print(company_df)
  length = len(company_df)
  print(length)
  buy_sell = []
  signal = 0
  for i in range(length):
    if (company_df["Bullish swing"][i] == True):
      signal = "Buy"
      buy_sell.append(signal)
    elif (company_df["Bearish swing"][i] == True):
      signal = "Sell"
      buy_sell.append(signal)
    else:
      signal = "Hold"
      buy_sell.append(signal)

  print(len(buy_sell))
  company_df3 = company_df
  # Drop first row
  # company_df3.drop(index=company_df3.index[0], axis=0, inplace=True)
  #print(len(buy_sell))
  company_df3['Buy_Sell'] = buy_sell
  

  return company_df3


def profit_jcs(company_df,seed_money=10000):
  company_df3 = company_df
  length = len(company_df3)
  money = seed_money
  shares = 0
  last_buy_price = 0
  flag = 0
  for i in range(length):
    if((company_df3['Buy_Sell'][i] == "Buy")&(flag == 0)):
      shares = math.floor(money/company_df3['Close'][i])
      #print(shares)
      money = money - shares*company_df3['Close'][i]
      last_buy_price = company_df3['Close'][i]
      flag = 1

    elif((company_df3['Buy_Sell'][i] == "Sell") & (flag == 1)):
      new_money = shares*company_df3['Close'][i]
      shares = 0
      money = money + new_money
      flag = 0

  final_money = round(shares*company_df3['Close'][-1] + money,1)
  return [final_money,shares,money]

def plot_jcs_graph(df):
  print("Create a candle stick chart")
  df = df.reset_index()
  selected_columns = ['Date', 'High', 'Low','Open','Close','Buy_Sell']
  df = df[selected_columns]
  print(df.tail(10))
  fig = go.Figure(data=[go.Candlestick(x=df['Date'],
                                       open=df['Open'],
                                       high=df['High'],
                                       low=df['Low'],
                                       close=df['Close'])])
  
  # Add a line plot for 'Close'
  fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], mode='lines', name='Close',line=dict(color='black')))

  #Add markers for 'Buy' and 'Sell'
  buy_events = df[df["Buy_Sell"] == 'Buy']
  sell_events = df[df['Buy_Sell'] == "Sell"]

  fig.add_trace(go.Scatter(x=buy_events['Date'],y=buy_events['Close'],
                           mode='markers',marker=dict(color='blue',symbol='circle-dot'),
                           name='Buy'))
  
  fig.add_trace(go.Scatter(x=sell_events['Date'],y=sell_events['Close'],
                           mode='markers',marker=dict(color='red',symbol='x'),
                           name='Sell'))
  
  #customize the layout
  fig.update_layout(title="Japanese Candlestick Chart",
                    xaxis_title="Date",
                    yaxis_title="Price",
                    xaxis_rangeslider_visible=False)
  
  # Increase the height of the figure
  fig.update_layout(height=700)
  #Convert the Plotly figure to HTML
  plot_div = fig.to_html(full_html=False)

  

  return plot_div



#MACD


def macd(company_df):
  company_df2 = company_df
  company_df['EMA_12'] = company_df['Close'].ewm(span=12, adjust=False).mean()
  company_df['EMA_9'] = company_df['Close'].ewm(span=9, adjust=False).mean()
  company_df['MACD'] = company_df['EMA_12'] - company_df['EMA_9']
  company_df['MACD_signal'] = company_df['MACD'].ewm(span=9, adjust=False).mean()
  company_df['Difference'] = company_df['MACD'] - company_df['MACD_signal']

  company_df2['MACD_Diff'] = company_df['Difference']
  return company_df2



def buy_sell_macd(company_df):
  company_df4 = company_df
  length = len(company_df4)
  buy_sell = []
  for i in range(1,(length),1):
    if (company_df4['MACD_Diff'][i]<0) & (company_df4['MACD_Diff'][i-1]>0):
      buy_sell.append("Sell")
    elif (company_df4['MACD_Diff'][i]>0) & (company_df4['MACD_Diff'][i-1]<0):
      buy_sell.append("Buy")
    else:
      buy_sell.append("Hold")

  # Drop first row
  company_df4.drop(index=company_df4.index[0],
        axis=0,
        inplace=True)
  company_df4['Buy_Sell'] = buy_sell

  return company_df4

def profit_macd(company_df,seed_money=10000):
  money = seed_money
  company_df3 = company_df
  length = len(company_df3)
  shares = 0
  last_buy_price = 0
  flag = 0
  for i in range(length):
    if ((company_df3['Buy_Sell'][i] == "Buy")&(flag == 0)):
      shares = math.floor(money/company_df3['Close'][i])
     
      money = money - shares*company_df3['Close'][i]
      last_buy_price = company_df3['Close'][i]
      flag = 1

    elif ((company_df3['Buy_Sell'][i] == "Sell") & (flag == 1)):
     
      new_money = shares*company_df3['Close'][i]
      shares = 0
  
      money = money + new_money
 
      flag = 0

  return [round(shares*company_df3['Close'][-1] + money,1),shares,money]

def plot_macd_graph(df):
  print("Create a macd chart")
  df = df.reset_index()
  selected_columns = ['Date','EMA_9','MACD', 'MACD_signal','MACD_Diff','Buy_Sell']
  df = df[selected_columns]
  df['Date'] = pd.to_datetime(df['Date'])
  print(type(df['MACD'][0]))
  print(type(df['MACD_signal'][0]))
  fig = go.Figure()
  fig.add_trace(go.Scatter(x=df['Date'],y=df['MACD'],mode='lines',name='MACD'))
  fig.add_trace(go.Scatter(x=df["Date"],y=df["MACD_signal"],mode="lines",name="MACD Signal"))

  # #Mark Buy events with blue dots
  buy_events = df[df['Buy_Sell'] == 'Buy']
  fig.add_trace(go.Scatter(x=buy_events['Date'],y=buy_events['MACD'],
                            mode='markers',marker=dict(color='blue',symbol='circle-dot'),
                            name='Buy'))
  
  sell_events = df[df['Buy_Sell'] == 'Sell']
  fig.add_trace(go.Scatter(x=sell_events['Date'],y=sell_events['MACD'],
                            mode='markers',marker=dict(color='red',symbol='cross'),
                            name='Sell'))
  
  # Add MACD_diff as a bar plot with different colors for positive and negative values
  fig.add_trace(go.Bar(x=df['Date'], y=df['MACD_Diff'],
                     marker_color=['pink' if val > 0 else 'orange' for val in df['MACD_Diff']],
                     opacity=0.7, name='MACD Difference'))

  #Customize the layout
  fig.update_layout(title="MACD",
                    xaxis_title="Date",
                    yaxis_title="Values")
  
  # Increase the height of the figure
  fig.update_layout(height=700)


  #convert the Plotly figure to HTML
  plt_div = fig.to_html(full_html=False)

  return plt_div


#Stochastic oscillator
def stochastic_os(df):
  company_df = df.dropna()
  #Stochastic
  slowk, slowd = ta.STOCH(company_df['High'], company_df['Low'], company_df['Close'], fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
  company_df['Slowk'] = slowk
  company_df['Slowd'] = slowd
  company_df2 = company_df.dropna()
  company_df2['Difference'] = company_df2['Slowk'] - company_df2['Slowd']
  company_df2['Lowest_Slowk'] = company_df2['Slowk'].rolling(window=5).min()
  company_df2['Highest_Slowk'] = company_df2['Slowk'].rolling(window=5).max()
  company_df5 = company_df2.dropna()

  length = len(company_df5)
  return company_df5

def buy_sell_stochastic_os(df):
  length = len(df)

  buy_sell = []
  for i in range(0,(length),1):
    if((df['Difference'][i]>0) & (df['Lowest_Slowk'][i]<20)):
      buy_sell.append("Buy")
    elif (df['Difference'][i]<0) & (df['Highest_Slowk'][i]>80):
      buy_sell.append("Sell")
    else:
      buy_sell.append("Hold")
  
  df['Buy_Sell'] = buy_sell
  return df

def profit_stochastic_os(df,seed_money=10000):
  company_df6 = df
  length = len(company_df6)
  money = seed_money
  shares = 0
  last_buy_price = 0
  flag = 0
  for i in range(length):
    if((company_df6['Buy_Sell'][i] == "Buy")&(flag == 0)):
      # print('Buying share at: ')
      # print(company_df6['Close'][i])
      # print('Date: ')
      # print(company_df6.index[i])
      shares = math.floor(money/company_df6['Close'][i])
      # print(shares)
      money = money - shares*company_df6['Close'][i]
      last_buy_price = company_df6['Close'][i]
      # print(money)
      # print('\n')
      flag = 1

    elif((company_df6['Buy_Sell'][i] == "Sell")  & (flag == 1)):
      # print('Selling share at: ')
      # print(company_df6['Close'][i])
      new_money = shares*company_df6['Close'][i]
      shares = 0
      # print(new_money)
      money = money + new_money
      # print(money)
      # print('\n\n')
      flag = 0
  return [round(shares*company_df6['Close'][-1] + money,1),shares,money]

def plot_stochastic_os_graph(df):
  print("Create a Stochastic OS chart")
  df = df.reset_index()
  selected_columns = ['Date','Slowk','Slowd','Buy_Sell']
  df = df[selected_columns]
  df['Date'] = pd.to_datetime(df['Date'])
  
  fig = go.Figure()
  fig.add_trace(go.Scatter(x=df['Date'],y=df['Slowk'],mode='lines',name='Slow k'))
  fig.add_trace(go.Scatter(x=df["Date"],y=df["Slowd"],mode="lines",name="Slow d"))

  #Add markers for 'Buy' and 'Sell'
  buy_events = df[df["Buy_Sell"] == 'Buy']
  sell_events = df[df['Buy_Sell'] == "Sell"]

  fig.add_trace(go.Scatter(x=buy_events['Date'],y=buy_events['Slowk'],
                           mode='markers',marker=dict(color='blue',symbol='circle-dot'),
                           name='Buy'))
  
  fig.add_trace(go.Scatter(x=sell_events['Date'],y=sell_events['Slowd'],
                           mode='markers',marker=dict(color='red',symbol='x'),
                           name='Sell'))
  

  # Add horizontal lines at 80 and 20
  fig.add_shape(
        dict(type="line", x0=df['Date'].min(), x1=df['Date'].max(), y0=80, y1=80,
             line=dict(color="goldenrod", width=2), name="Overbought (80)"))

  fig.add_shape(
        dict(type="line", x0=df['Date'].min(), x1=df['Date'].max(), y0=20, y1=20,
             line=dict(color="goldenrod", width=2), name="Oversold (20)"))
  

  #Customize the layout
  fig.update_layout(title="Stochastic Oscillator",
                    xaxis_title="Date",
                    yaxis_title="Values")
  
  # Increase the height of the figure
  fig.update_layout(height=700)

  
  #convert the Plotly figure to HTML
  plt_div = fig.to_html(full_html=False)

  return plt_div



#ADX
def adx(df):
  company_df = df.dropna()
  # Average Directional Movement Index(Momentum Indicator)
  company_df['avg'] = ta.ADX(company_df['High'],company_df['Low'], company_df['Close'], timeperiod=20)
  company_df['Plus_DI'] = ta.PLUS_DI(company_df['High'],company_df['Low'], company_df['Close'], timeperiod=20)
  company_df['Minus_DI'] = ta.MINUS_DI(company_df['High'],company_df['Low'], company_df['Close'], timeperiod=20)

  company_df2 = company_df

  company_df5 = company_df2[['Close','avg','Plus_DI','Minus_DI']]

  company_df5['Diff'] = company_df5['Plus_DI']-company_df5['Minus_DI']
  company_df5 = company_df5.dropna()

  return company_df5


def buy_sell_adx(df):
  length = len(df)
  buy_sell = []
  for i in range(1,(length),1):
    if (df['avg'][i]>25):
      if (df['Diff'][i]<0) & (df['Diff'][i-1]>0):
        buy_sell.append("Sell")
      elif (df['Diff'][i]>0) & (df['Diff'][i-1]<0):
        buy_sell.append("Buy")
      else:
        buy_sell.append("Hold")
    else:
      buy_sell.append("Hold")

    # Drop first row
  df.drop(index=df.index[0], 
          axis=0, 
          inplace=True)
  df['Buy_Sell'] = buy_sell

  return df


def profit_adx(df,seed_money=10000):
  company_df3 = df
  length = len(company_df3)
  money = seed_money
  shares = 0
  last_buy_price = 0
  flag = 0
  for i in range(length):
    if ((company_df3['Buy_Sell'][i] == "Buy")&(flag == 0)):
      print('Buying share at: ')
      print(company_df3['Close'][i])
      print('Date: ')
      print(company_df3.index[i])
      shares = math.floor(money/company_df3['Close'][i])
      print(shares)
      money = money - shares*company_df3['Close'][i]
      last_buy_price = company_df3['Close'][i]
      print(money)
      print('\n')
      flag = 1

    elif ((company_df3['Buy_Sell'][i] == "Sell") & (flag == 1)):
      print('Selling share at: ')
      print(company_df3['Close'][i])
      new_money = shares*company_df3['Close'][i]
      shares = 0
      print(new_money)
      money = money + new_money
      print(money)
      print('\n\n')
      flag = 0

  return [round(shares*company_df3['Close'][-1] + money,1),shares,money]




def plot_adx_graph(df):
  print("Create a adx chart")
  df = df.reset_index()
  # selected_columns = ['Date','Slowk','Slowd','Buy_Sell']
  # df = df[selected_columns]
  df['Date'] = pd.to_datetime(df['Date'])
  
  fig = go.Figure()
  fig.add_trace(go.Scatter(x=df['Date'],y=df['avg'],mode='lines',name='AVG'))
  fig.add_trace(go.Scatter(x=df["Date"],y=df["Plus_DI"],mode="lines",name="Plus DI"))
  fig.add_trace(go.Scatter(x=df["Date"],y=df["Minus_DI"],mode="lines",name="Minus DI"))


  #Add markers for 'Buy' and 'Sell'
  buy_events = df[df["Buy_Sell"] == 'Buy']
  sell_events = df[df['Buy_Sell'] == "Sell"]

  fig.add_trace(go.Scatter(x=buy_events['Date'],y=buy_events['avg'],
                           mode='markers',marker=dict(color='blue',symbol='circle-dot'),
                           name='Buy'))
  
  fig.add_trace(go.Scatter(x=sell_events['Date'],y=sell_events['avg'],
                           mode='markers',marker=dict(color='red',symbol='x'),
                           name='Sell'))
  

  # Add horizontal lines at 25
  fig.add_shape(
        dict(type="line", x0=df['Date'].min(), x1=df['Date'].max(), y0=25, y1=25,
             line=dict(color="goldenrod", width=2), name="25"))

  

  #Customize the layout
  fig.update_layout(title="ADX",
                    xaxis_title="Date",
                    yaxis_title="Values")
  
  # Increase the height of the figure
  fig.update_layout(height=700)

  
  #convert the Plotly figure to HTML
  plt_div = fig.to_html(full_html=False)

  return plt_div