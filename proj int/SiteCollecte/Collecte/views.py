from django.shortcuts import render, HttpResponse
from .models import Sensor, TemperatureData
import matplotlib.pyplot as plt
import pymysql
from io import BytesIO
import base64

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
    
    return render(request, 'collecte/home.html', context)

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
    return HttpResponse(request, 'collecte/home.html')

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

    # Génération du graphique
    plt.figure(figsize=(10, 6))
    for sensor in sensor_data:
        plt.plot(sensor['temperatures'], label=sensor['sensor'].piece)
    plt.xlabel('Temps')
    plt.ylabel('Température (°C)')
    plt.title('Graphique des Températures par Capteur')
    plt.legend()
    
    # Conversion du graphique en image pour l'afficher dans le template
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    graphique = base64.b64encode(image_png).decode('utf-8')
    plt.close()

    context = {
        'graphique': graphique
    }

    return render(request, 'collecte/graphiques.html', context)
