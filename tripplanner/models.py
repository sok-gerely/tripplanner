from django.db import models
import datetime

class Station(models.Model):
    xpos = models.FloatField(default=0.0)
    ypos = models.FloatField(default=0.0)


class Line(models.Model):
    stations = models.ManyToManyField(
                            Station,
                            through='StationOrder')
                            
class StationOrder(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    line = models.ForeignKey(Line, on_delete=models.CASCADE)
    order_num = models.IntegerField(unique=True)

class Service(models.Model):
    fee = models.IntegerField(default=1)
    line = models.ForeignKey(Line, on_delete=models.CASCADE)

class TimetableData(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    station_order = models.ForeignKey(StationOrder, on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    delay = models.DurationField(default=datetime.timedelta)