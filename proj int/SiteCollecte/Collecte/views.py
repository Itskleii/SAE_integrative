# collecte/views.py

from django.shortcuts import render
from .models import Sensor, TemperatureData
from . import models
def home(request):
    sensors = Sensor.objects.all()
    sensor_data = []
    temp = models.TemperatureData.objects.all()

    for sensor in sensors:
        sensors = Sensor.objects.all()
        temperature_data = TemperatureData.objects.filter(sensor_id=sensor).order_by('-timestamp')[:10]
        sensor_data.append({
            'sensor': sensor,
            'temperature_data': temperature_data
        })
    
    context = {
        'sensor_data': sensor_data,
        'temp': temp
    }
    
    return render(request, 'collecte/home.html', context)

