from django.shortcuts import render
from django.http import HttpResponse

import json
import asyncio


from .forms import MyForm,SimulationForm


from .trading import (nepse_symbols, stock_dataFrame,obv_column,buy_sell_obv,
                      jcs_signals,macd,buy_sell_macd,stochastic_os,buy_sell_stochastic_os,
                      adx,buy_sell_adx)
from .simulation import simulation


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
            frequency = form.cleaned_data['frequency']
            print("************************************************")
            print(frequency)

            upper_str= input_string.upper()
            current_symbol = upper_str
            try:
                if frequency == "weekly":
                    df = stock_dataFrame(upper_str,weekly=True)
                else:
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

            #Send data to Stochastic Oscillator
            stochastic_df = df.copy()
            stochastic_df = stochastic_os(stochastic_df)
            stochastic_df = buy_sell_stochastic_os(stochastic_df)
            stochastic_os_verdict = stochastic_df.iloc[-1,-1]
            # print(stochastic_df)
            verdict["Stochastic Oscillator"] = stochastic_os_verdict

            #Send data to adx
            adx_df = df.copy()
            adx_df = adx(df)
            adx_df = buy_sell_adx(adx_df)
            # print(adx_df)
            adx_verdict = adx_df.iloc[-1,-1]
            verdict["ADX"] = adx_verdict


            print(verdict)
           
            


            df = df.reset_index()
            # print(df)
            df['Date'] = df['Date'].astype(str)
            processed_data = df[::-1]
            print(processed_data)
            
            
            processed_data_json = processed_data.to_json(orient='records')
            print(processed_data_json)
            
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



def trading_simulation(request):
    stock_symbols = nepse_symbols()
    if request.method == "POST":
        form = SimulationForm(request.POST)
        if form.is_valid():
            input_string = form.cleaned_data['input_string']
            date_input = form.cleaned_data['date_input']
            initial_capital = form.cleaned_data['positive_number']
            indicators = form.cleaned_data['checkboxes']


            form_data = {"Stock":input_string,
                         "Start Date":date_input,
                         "initial_capital":initial_capital,
                         "indicators":indicators}
            
            # simulation(form_data)
            asyncio.run(simulation(form_data))

        return render(request,"nepse/simulation.html",{'form':form,
                                                       "stock_symbols":stock_symbols,
                                                       "form_data":form_data})

    else:
        form = SimulationForm()

    return render(request,"nepse/simulation.html",{'form':form,
                                                   "stock_symbols":stock_symbols})
