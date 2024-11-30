from django import forms

class BMICalculatorForm(forms.Form):
    weight = forms.FloatField(label='Weight (kg)', min_value=1)
    height = forms.FloatField(label='Height (m)', min_value=0.1, widget=forms.NumberInput(attrs={'step': '0.01'}))
