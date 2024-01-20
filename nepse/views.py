from django.shortcuts import render
from django.http import HttpResponse

import json

from .forms import MyForm

from .trading import nepse_symbols, stock_dataFrame

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
            try:
                df = stock_dataFrame(upper_str)
                df = df.reset_index()
                df['Date'] = df['Date'].astype(str)
                processed_data = df.head(100)
                print(processed_data)
                
                processed_data_json = processed_data.to_json(orient='records')
                print(processed_data_json)
                # Extract column names
                column_names = processed_data.columns.tolist()

            except:
                pass


            return render(request,"nepse/form.html",{'form':form,
                                                     'processed_data_json':processed_data_json,
                                                     'column_names': column_names,
                                                     "stock_symbols":stock_symbols})
        
    else:
        form = MyForm()

    return render(request,'nepse/form.html',{'form':form,
                                             "stock_symbols":stock_symbols})
