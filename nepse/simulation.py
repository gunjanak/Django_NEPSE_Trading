import asyncio
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import warnings
warnings.filterwarnings('ignore')
from nepse.trading import (stock_dataFrame,obv_column,buy_sell_obv,profit_obv,plot_obv_graph,
                           jcs_signals,profit_jcs,buy_sell_jcs,plot_jcs_graph,
                           macd,buy_sell_macd,profit_macd,
                           stochastic_os,buy_sell_stochastic_os,profit_stochastic_os,
                           adx,buy_sell_adx,profit_adx)

async def run_indicator_function(indicator_function,df,seed_money=10000):
    net_worths = {}
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None,indicator_function,df,seed_money)
    # print(f"{indicator_function.__name__} result:{result}")
    net_worths[indicator_function.__name__] = result
    return net_worths


async def simulation(form_data):
    print(form_data)
    try:
        df = stock_dataFrame(form_data["Stock"],start_date=form_data["Start Date"])
    except:
        print("Code fucked up")

    indicator_functions = {
        "OBV":obv_function,
        "JCS":jcs_function,
        "MACD":macd_function,
        "Stochastic OS":stochastic_os_function,
        "ADX":adx_function,
    }

    selected_indicators = form_data["indicators"]
    seed_money = form_data["initial_capital"]

    tasks = [run_indicator_function(indicator_functions[indicator],df.copy(),seed_money) for indicator in selected_indicators]
    

    results = await asyncio.gather(*tasks)
    return results



def obv_function(df,seed_money):
    print("Calling OBV function")
    #Dealing with obv
    obv_df = obv_column(df)
    obv_df = buy_sell_obv(df)
    obv_profit = profit_obv(obv_df,seed_money) 
    plot_obv = plot_obv_graph(obv_df)
    # print(obv_profit)


    return [obv_profit,plot_obv]

def jcs_function(df,seed_money):
    print("Calling JCS function")
    jcs_df = jcs_signals(df)
    jcs_df = buy_sell_jcs(jcs_df)
    plot_jcs = plot_jcs_graph(jcs_df)
    
    jcs_profit = profit_jcs(jcs_df,seed_money)
    # print(jcs_profit)
    return [jcs_profit,plot_jcs]

def macd_function(df,seed_money):
    print("Calling MACD function")
    macd_df = macd(df)
    macd_df = buy_sell_macd(macd_df)
    macd_profit = profit_macd(macd_df,seed_money)
    # print(macd_profit)
    return macd_profit

def stochastic_os_function(df,seed_money):
    print("Calling Stochastic Oscillator")
    stochastic_os_df = stochastic_os(df)
    stochastic_os_df = buy_sell_stochastic_os(stochastic_os_df)
    stochastic_os_profit = profit_stochastic_os(stochastic_os_df,seed_money)
    # print(stochastic_os_profit)
    return stochastic_os_profit

def adx_function(df,seed_money):
    print("Calling ADX function")
    adx_df = adx(df)
    adx_df = buy_sell_adx(adx_df)
    adx_profit = profit_adx(adx_df,seed_money)
    print(adx_profit)
    return adx_profit