from django import forms

class MyForm(forms.Form):
    input_string = forms.CharField(label="Input String",max_length=100)
    