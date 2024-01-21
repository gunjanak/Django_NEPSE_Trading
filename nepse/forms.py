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
    