
import pandas as pd
from datetime import datetime, timedelta
from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
import re
import math

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
def stock_dataFrame(stock_symbol,start_date='2020-12-01',weekly=False):
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
      signal = 0
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
    if((company_df3['Buy_Sell'][i] == 2)&(flag == 0)):
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

    elif((company_df3['Buy_Sell'][i] == -2) & (company_df3['Close'][i] > last_buy_price) & (flag == 1)):
      #print('Selling share at: ')
      #print(company_df3['Close'][i])
      new_money = shares*company_df3['Close'][i]
      shares = 0
      #print(new_money)
      money = money + new_money
      #print(money)
      #print('\n\n')
      flag = 0

  final_money = shares*company_df3['Close'][-1] + money
  return [final_money,shares,money]



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
