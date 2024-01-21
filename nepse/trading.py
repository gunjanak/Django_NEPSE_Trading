
import pandas as pd
from datetime import datetime, timedelta
from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
import re
import math
import talib as ta
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
    if ((company_df3['Buy_Sell'][i] == 2)&(flag == 0)):
      shares = math.floor(money/company_df3['Close'][i])
     
      money = money - shares*company_df3['Close'][i]
      last_buy_price = company_df3['Close'][i]
      flag = 1

    elif ((company_df3['Buy_Sell'][i] == -2) & (company_df3['Close'][i] > last_buy_price) & (flag == 1)):
     
      new_money = shares*company_df3['Close'][i]
      shares = 0
  
      money = money + new_money
 
      flag = 0

  return [shares*company_df3['Close'][-1] + money,shares,money]


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
    if (df['avg'][i]>20):
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


