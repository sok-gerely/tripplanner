from django.db import models
import datetime


class Station(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name


class Line(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name


class StationOrder(models.Model):
    station_from = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='from+')
    station_to = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='to+')
    line = models.ForeignKey(Line, on_delete=models.CASCADE)
    distance = models.IntegerField()

    def __str__(self):
        return f'{self.station_from} -> {self.station_to};'


class Service(models.Model):
    fee = models.IntegerField(default=1)
    line = models.ForeignKey(Line, on_delete=models.CASCADE)
    valid_from = models.DateField(default=datetime.date.today)
    valid_until = models.DateField(default=datetime.date.today)
    NORMAL = 'N'
    WEEKEND = 'W'
    HOLIDAY = 'H'
    TYPE_CHOICES = [(NORMAL, 'normal'),
                    (WEEKEND, 'weekend'),
                    (HOLIDAY, 'holiday')]

    type = models.CharField(max_length=1, choices=TYPE_CHOICES, default=NORMAL)

    def get_station_list(self):
        ret_stations = []
        service_stations = StationOrder.objects.filter(line=self.line).values_list('station_from','station_to')
        for ind,(from_station,to_station) in enumerate(service_stations):
            if(ind==0):ret_stations.append(from_station)
            ret_stations.append(to_station)
        return ret_stations

    def save(self,*args,**kwargs):
        created = not self.pk
        super().save(*args,**kwargs)
        if created:
            ret_stations = self.get_station_list()
            for temp_station in ret_stations:
                TimetableData.objects.create_timetable(service=self,station=Station.objects.get(pk=temp_station))

    

    def get_station_num(self):
        return StationOrder.objects.filter(line=self.line).count()

    def __str__(self):
        date_times = self.timetabledata_set.order_by("date_time")
        if len(date_times) > 0:
            return f'{self.line} ({date_times[0].date_time}): {self.fee}'
        else:
            return f'{self.line} (): {self.fee}'


class TimetableDataManager(models.Manager):
    def create_timetable(self, service, station):
        timetable = self.create(service=service,station=station)
        return timetable

class TimetableData(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    date_time = models.TimeField(default=datetime.datetime.now().time)
    objects = TimetableDataManager()

    def get_station_num(self):
        temp_service = Service.objects.get(pk=1) #how in the fck can i get the Service with self.service??
        return temp_service.get_station_num()

    def __str__(self):
        return f'{self.service.line} ({self.station}): {self.date_time}'

class Delay(models.Model):
    timetable = models.ForeignKey(TimetableData, on_delete=models.CASCADE)
    delay = models.DurationField(default=datetime.timedelta)
    date = models.DateField(default=datetime.date.today)

    def __str__(self):
        return f'{self.timetable} ({self.date}): {self.delay}'