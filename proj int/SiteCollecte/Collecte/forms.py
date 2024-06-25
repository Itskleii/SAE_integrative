from django import forms
from .models import Sensor

class SensorForm(forms.ModelForm):
    class Meta:
        model = Sensor
        fields = ['sensor_id', 'piece', 'name', 'emplacement']
        widgets = {
            'sensor_id': forms.TextInput(attrs={'readonly': 'readonly'}),
            'piece': forms.TextInput(attrs={'readonly': 'readonly'}),
        }
