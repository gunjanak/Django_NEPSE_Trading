from django.shortcuts import render
from django.http import HttpResponse

import json


from .forms import MyForm

from .trading import (nepse_symbols, stock_dataFrame,obv_column,buy_sell_obv,
                      jcs_signals,macd,buy_sell_macd)

# Create your views here.
def homePageView(request):
    all_stock_symbols = nepse_symbols()
    print(all_stock_symbols)
    print(len(all_stock_symbols))
    return HttpResponse("Hello ")

def nepseData(request):
    stock_symbols = nepse_symbols()
    if request.method == "POST":
        form = MyForm(request.POST)
        if form.is_valid():
            input_string = form.cleaned_data['input_string']

            upper_str= input_string.upper()
            current_symbol = upper_str
            try:
                df = stock_dataFrame(upper_str)
                
                

            except Exception as e:
                error_message = f"An error occurred: {str(e)}"
                return render(request,"nepse/form.html",{'form':form,
                                                        "error_message":error_message,
                                                     "stock_symbols":stock_symbols})
            
            
            verdict = {}
            #send data to calculate obv
            obv_df = df.copy()
            obv_df = obv_column(obv_df)
            obv_df = obv_df[['OBV']]
            # print(obv_df)
            obv_b_s = buy_sell_obv(obv_df)
            obv_verdict = obv_b_s.iloc[-1,-1]
            verdict["OBV"] = obv_verdict
            # print(verdict)

            #Send data to calculate jcs signals
            # print(df)
            jcs_df = df.copy()
            jcs_df = jcs_signals(jcs_df)
            jcs_df = jcs_df[["Bullish swing","Bearish swing"]]
            # print(jcs_df.tail(2))
            if jcs_df.iloc[-1]['Bullish swing']:
                jcs_verdict = "Buy"
            elif jcs_df.iloc[-1]['Bearish swing']:
                jcs_verdict = "Sell"
            else:
                jcs_verdict = "Hold"
            
            # print(jcs_verdict)
            verdict["JCS"] = jcs_verdict

            #Send data to MACD
            macd_df = df.copy()
            macd_df = macd(macd_df)
            macd_df = buy_sell_macd(macd_df)
            print(macd_df)
            true_count = (macd_df['Buy_Sell'] == "Buy").sum()
            print(true_count)
            macd_verdict = macd_df.iloc[-1,-1]
            verdict["MACD"] = macd_verdict


            print(verdict)
           
            


            df = df.reset_index()
            df['Date'] = df['Date'].astype(str)
            processed_data = df[::-1]
            
            
            processed_data_json = processed_data.to_json(orient='records')
            
            # Extract column names
            column_names = processed_data.columns.tolist()


            return render(request,"nepse/form.html",{'form':form,
                                                     "current_symbol":current_symbol,
                                                     'processed_data_json':processed_data_json,
                                                     'column_names': column_names,
                                                     "stock_symbols":stock_symbols,
                                                     "verdict":verdict})
        
    else:
        form = MyForm()

    return render(request,'nepse/form.html',{'form':form,
                                             "stock_symbols":stock_symbols})
