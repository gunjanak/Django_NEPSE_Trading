import asyncio

from nepse.trading import (stock_dataFrame,obv_column,buy_sell_obv,profit_obv,
                           jcs_signals,profit_jcs,macd,buy_sell_macd,profit_macd,
                           stochastic_os,buy_sell_stochastic_os,
                           adx,buy_sell_adx)

async def run_indicator_function(indicator_function,df):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None,indicator_function,df)

async def simulation(form_data):
    print(form_data)
    try:
        df = stock_dataFrame(form_data["Stock"],start_date=form_data["Start Date"])
    except:
        print("Code fucked up")

    indicator_functions = {
        "OBV":obv_function,
        "JCS":jcs_function,
        "MACD":macd_function
    }

    selected_indicators = form_data["indicators"]

    tasks = [run_indicator_function(indicator_functions[indicator],df.copy()) for indicator in selected_indicators]

    await asyncio.gather(*tasks)




    






# def simulation(form_data):
#     print(form_data)
#     try:
#         df = stock_dataFrame(form_data["Stock"],start_date=form_data["Start Date"])
#     except:
#         print("Code fucked up")
#     print(form_data["indicators"])
#     selected_indicators = form_data["indicators"]

#     indicator_functions = {
#         "OBV":obv_function,
#         "JCS":jcs_function,
#         "MACD":macd_function
#     }

#     for indicator in selected_indicators:
#         if indicator in indicator_functions:
#             indicator_functions[indicator](df.copy())
#     # obv_df = df.copy()    
#     # obv_function(obv_df)

#     # jcs_df = df.copy()
#     # jcs_function(jcs_df)

#     # macd_df = df.copy()
#     # macd_function(macd_df)

#     return None

def obv_function(df):
    print("Calling OBV function")
    #Dealing with obv
    obv_df = obv_column(df)
    obv_df = buy_sell_obv(df)
    obv_profit = profit_obv(obv_df) 
    # print(obv_df)
    print(obv_profit)


    return None

def jcs_function(df):
    print("Calling JCS function")
    jcs_df = jcs_signals(df)
    # print(jcs_df)
    jcs_profit = profit_jcs(jcs_df)
    print(jcs_profit)
    return None

def macd_function(df):
    print("Calling MACD function")
    return None