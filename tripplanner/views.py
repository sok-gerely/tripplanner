from django.http import HttpResponse
import datetime

from django.shortcuts import render, redirect

from tripplanner.planning_alg import plan, NoRouteExists
from tripplanner import models


def result(request, planning_mode: str, time_int: int, station_from_name: str, station_to_name: str):
    start_time = datetime.time(time_int // 100, time_int % 100)
    print(start_time)
    try:
        gen = plan(planning_mode, start_time, station_from_name, station_to_name)
    except NoRouteExists:
        return HttpResponse("Route doesn't exist")
    return HttpResponse('<br>'.join(f'{l} {t} --> {a}, {s} - {f}' for a, s, t, l, f in gen))


def index(request):
    stations = models.Station.objects.all()
    return render(request, 'tripplanner/index.html', {'stations': stations})


def redirect2result(request):
    return redirect(result, planning_mode='time', time_int='1100', station_from_name=request.GET['start_station'],
                    station_to_name=request.GET['destination_station'])
