# collecte/models.py

from django.db import models

class Sensor(models.Model):
    id = models.AutoField(primary_key=True)
    sensor_id = models.CharField(max_length=255, unique=True)
    piece = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = 'sensor'

    def __str__(self):
        return self.sensor_id

class TemperatureData(models.Model):
    sensor_id = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    value = models.FloatField()

    class Meta:
        db_table = 'temperaturedata'

    def __str__(self):
        return self.sensor_id, self.timestamp, self.value
