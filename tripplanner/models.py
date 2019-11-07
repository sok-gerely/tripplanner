from django.db import models

class Station(models.Model):
    xpos = models.FloatField(default=0.0)
    ypos = models.FloatField(default=0.0)


class Line(models.Model):
    #is it sortable this way
    stations = models.ManyToManyField(
                            Station,
                            through='StationOrder')
                            
class StationOrder(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    line = models.ForeignKey(Line, on_delete=models.CASCADE)
    order_num = models.IntegerField()

class Service(models.Model):
    fee = models.IntegerField(default=1)
    line = models.ForeignKey(Line, on_delete=models.CASCADE)
    

class Timetable(models.Model):
    service = models.OneToOneField(Service, on_delete=models.CASCADE)

class TimetableData(models.Model):
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE)
    #is the order of stations handled this way?
    station_order = models.ForeignKey(StationOrder(), on_delete=models.CASCADE) #is cascade necessary here?
    date_time = models.DateTimeField()

class Delay(models.Model):
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE)
    delay = models.TimeField()