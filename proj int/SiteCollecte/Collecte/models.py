# collecte/models.py

from django.db import models

class Sensor(models.Model):
    sensor_id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255, null=True)
    emplacement = models.CharField(max_length=255, null=True, blank=True)
    piece = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = 'sensor'

    def __str__(self):
        return self.sensor_id

class TemperatureData(models.Model):
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    value = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        db_table = 'temperaturedata'

    def __str__(self):
        return f"{self.sensor.sensor_id}, {self.timestamp}, {self.value}"
