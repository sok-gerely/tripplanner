from django.db import models
import datetime



class Station(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name


class Line(models.Model):
    name = models.CharField(max_length=30, unique=True)
    station_list = []
    """TRAIN = 'T'
    BUS = 'B'
    TYPE_CHOICES = [(TRAIN, 'train'),
                    (BUS, 'bus')]

    type = models.CharField(max_length=1, choices=TYPE_CHOICES, default=TRAIN)"""
    
    def get_station_list(self):
        self.order_stations()
        return self.station_list

    def update_station_list(self):
        ret_stations = []
        service_stations = StationOrder.objects.filter(line=self).values_list('station_from','station_to')
        for ind,(from_station,to_station) in enumerate(service_stations):
            if(ind==0):ret_stations.append(from_station)
            ret_stations.append(to_station)
        self.station_list = ret_stations

    def get_starting_station(self):
        starting_station = None
        self.update_station_list()
        for station in self.station_list:
            if StationOrder.objects.filter(line=self,station_from=station):
                if not StationOrder.objects.filter(line=self,station_to=station):
                    if starting_station is None: starting_station = station
                    #else multiple starting stations-throw error
        return starting_station

    def get_next_station(self,station):
        next_station = StationOrder.objects.filter(line=self,station_from=station).values_list('station_to')
        #If there is a next station and is not ambiguous
        if next_station.count() == 1:
            return next_station[0]
        #If there isn't a next station
        elif next_station.count() == 0:
            #else ambiguous
            return None

    def order_stations(self):
        starting_station = self.get_starting_station()
        if starting_station is not None:
            #else throw error
            ret_stations = [starting_station]
            next_station = self.get_next_station(starting_station)
            while(next_station):
                ret_stations.append(next_station)
                next_station = self.get_next_station(next_station)
            self.station_list = ret_stations

    def get_last_station(self):
        self.order_stations()
        return self.station_list[-1]

    def update_services(self):
        services = Service.objects.filter(line=self).all()
        for service in services:
            service.update_timetables(self.station_list)

    def del_update_services(self):
        services = Service.objects.filter(line=self).all()
        for service in services:
            service.check_to_delete(self.station_list)

    def update(self):
        self.order_stations()
        self.update_services()

    def deletion_update(self):
        self.order_stations()
        self.del_update_services()

    def __str__(self):
        return self.name


class StationOrder(models.Model):
    station_from = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='from+')
    station_to = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='to+')
    line = models.ForeignKey(Line, on_delete=models.CASCADE)
    distance = models.IntegerField()

    def save(self, *args, **kwargs):
        created = not self.pk
        super().save(*args,**kwargs)
        if created:
            self.line.update()

    def delete(self, *args, **kwargs):
        super().delete(*args,**kwargs)
        self.line.deletion_update()

    def __str__(self):
        return f'{self.station_from} -> {self.station_to};'

"""class LineStation(Station):
    class Meta:
        proxy = True

    line = models.ForeignKey(Line,on_delete=models.CASCADE)

    def get_distance_to_next(self,line):
        next_station = line.get_next_station(self)
        distance = StationOrder.objects.filter(station_from=self,station_to=next_station).values_list('distance')[0]
        return distance"""

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

    def save(self, *args, **kwargs):
        is_adding = self._state.adding
        super().save(*args,**kwargs)
        if is_adding:
            self.update_timetables(self.line.get_station_list())

    def check_to_delete(self,comp_stations):
        timetable_stations = TimetableData.objects.filter(service=self).values_list('station','id')
        for tt_station, tt_id in timetable_stations:
            if tt_station not in comp_stations:
                TimetableData.objects.get(id=tt_id).delete()
            else:
                tt = TimetableData.objects.get(id=tt_id)
                tt.station_num = len(comp_stations)

    def update_timetables(self,compare_stations):
        for temp_station in compare_stations:
            tts = TimetableData.objects.filter(service=self,station=Station.objects.get(pk=temp_station)).all()
            if not tts:
                TimetableData.objects.create_timetable(service=self,station=Station.objects.get(pk=temp_station),station_num=len(compare_stations))
            else:
                for tt in tts:
                    tt.station_num = len(compare_stations)


    def __str__(self):
        date_times = self.timetabledata_set.order_by("date_time")
        if len(date_times) > 0:
            return f'{self.line} ({date_times[0].date_time}): {self.fee}'
        else:
            return f'{self.line} (): {self.fee}'


class TimetableDataManager(models.Manager):
    def create_timetable(self, service, station, station_num):
        timetable = self.create(service=service,station=station)
        timetable.station_num = station_num
        return timetable

class TimetableData(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    date_time = models.TimeField(default=datetime.datetime.now)
    objects = TimetableDataManager()
    station_num = 0

    def __str__(self):
        return f'{self.service.line} ({self.station}): {self.date_time}'

class Delay(models.Model):
    timetable = models.ForeignKey(TimetableData, on_delete=models.CASCADE)
    delay = models.DurationField(default=datetime.timedelta)
    date = models.DateField(default=datetime.date.today)

    def __str__(self):
        return f'{self.timetable} ({self.date}): {self.delay}'