from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from .models import Sensor, TemperatureData
import matplotlib.pyplot as plt
import pymysql
from io import BytesIO
import base64
from django.views.decorators.csrf import csrf_protect
from .forms import SensorForm
from django.http import JsonResponse

def home(request):
    sensors = Sensor.objects.all()
    sensor_data = []

    for sensor in sensors:
        temperature_data = TemperatureData.objects.filter(sensor=sensor)
        sensor_data.append({
            'sensor': sensor,
            'temperature_data': temperature_data
        })

    context = {
        'sensor_data': sensor_data,
    }
    
    return render(request, 'Collecte/home.html', context)

def empty_sql(request):
    db = pymysql.connect(
        host="localhost",
        user="siteusr",
        password="2503",
        database="SiteCollecte"
    )
    cursor = db.cursor()
    cursor.execute("TRUNCATE TABLE temperaturedata")
    db.commit()
    return HttpResponse(request, 'Collecte/home.html')

def graphiques(request):
    sensors = Sensor.objects.all()
    sensor_data = []

    for sensor in sensors:
        temperature_data = TemperatureData.objects.filter(sensor=sensor)
        sensor_temperatures = [temp.value for temp in temperature_data]
        sensor_data.append({
            'sensor': sensor,
            'temperatures': sensor_temperatures
        })

def get_all_sensor_data(request):
    try:
        data = TemperatureData.objects.all().order_by('timestamp')
        response_data = {}
        for entry in data:
            sensor_id = str(entry.sensor.sensor_id)  # Utiliser l'ID du capteur comme clé
            sensor_name = entry.sensor.piece  # Nom du capteur
            if sensor_id not in response_data:
                response_data[sensor_id] = {
                    'name': sensor_name,
                    'values': []
                }
            response_data[sensor_id]['values'].append({
                'timestamp': entry.timestamp.isoformat(),  # Convertir en format ISO pour JSON
                'value': float(entry.value)
            })
        print("Données renvoyées:", response_data)  # Ajout du message de console
        return JsonResponse(response_data, safe=False)
    except Exception as e:
        print("Erreur lors de la récupération des données des capteurs:", e)
        return JsonResponse({"error": str(e)}, status=500)

def indexgraph(request):
    return render(request, 'Collecte/graphiques.html')
    
@csrf_protect
def update_sensor(request, sensor_id):
    sensor = get_object_or_404(Sensor, sensor_id=sensor_id)
    if request.method == 'POST':
        form = SensorForm(request.POST, instance=sensor)
        if form.is_valid():
            form.save()
            return redirect('collecte:home')  # Rediriger vers la page d'accueil ou une autre vue après modification
    else:
        form = SensorForm(instance=sensor)
    
    return render(request, 'Collecte/update_sensor.html', {'form': form})

def view_sensor(request, sensor_id):
    sensor = get_object_or_404(Sensor, sensor_id=sensor_id)
    temperaturedata = TemperatureData.objects.filter(sensor=sensor)
    
    return render(request, 'Collecte/view_sensor.html', {
        'sensor': sensor,
        'temperaturedata': temperaturedata
    })
