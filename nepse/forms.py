from django import forms

class MyForm(forms.Form):
    input_string = forms.CharField(label="Input String",max_length=100)
     # Add the radio button field
    frequency_choices = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
    ]
    frequency = forms.ChoiceField(
        label="Frequency",
        choices=frequency_choices,
        widget=forms.RadioSelect,
        required=False
    )
    
class SimulationForm(forms.Form):
    input_string = forms.CharField(
        label="Input String",
        max_length=100,
        widget=forms.TextInput(attrs={'autocomplete':"off",
                                      'list': 'stockSymbolsList'}))
    

    date_input = forms.DateField(
        label="Date Input",
        widget=forms.DateInput(attrs={"type":"date"}))
    
    positive_number = forms.IntegerField(
        label="Initial Capital",
        min_value=10000,max_value=1000000)
    

    checkbox_choices = [
        ('OBV','OBV'),
        ("JCS","JCS"),
        ("MACD","MACD"),
        ("Stochastic OS","Stochastic OS"),
        ("ADX","ADX"),
        
    ]

    checkboxes = forms.MultipleChoiceField(
        label="Select Indicators",
        choices=checkbox_choices,
        widget=forms.CheckboxSelectMultiple,
    )

    def clean_checkboxes(self):
        selected_indicators = self.cleaned_data.get('checkboxes')
        if not selected_indicators:
            raise forms.ValidationError("Select at least one indicator.")
        return selected_indicators