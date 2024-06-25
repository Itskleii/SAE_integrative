from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from .models import Sensor, TemperatureData
import matplotlib.pyplot as plt
import pymysql
from io import BytesIO
import base64
from django.views.decorators.csrf import csrf_protect
from .forms import SensorForm

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
    
    return render(request, 'collecte/update_sensor.html', {'form': form})

def view_sensor(request, sensor_id):
    sensor = get_object_or_404(Sensor, sensor_id=sensor_id)
    temperaturedata = TemperatureData.objects.filter(sensor=sensor)
    
    return render(request, 'collecte/view_sensor.html', {
        'sensor': sensor,
        'temperaturedata': temperaturedata
    })
