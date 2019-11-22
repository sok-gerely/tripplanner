from django.http import HttpResponse, Http404
import datetime

from django.shortcuts import render, redirect, get_object_or_404

from tripplanner.planning_alg import plan, NoRouteExists, StationsAreTheSame, PlanningMode
from tripplanner import models


def result(request, planning_mode_str: str, datetime_str: str, station_from_name: str, station_to_name: str):
    try:
        planning_mode = PlanningMode(planning_mode_str)
    except ValueError:
        raise Http404('Planning mode in not valid!')
    start_station = get_object_or_404(models.Station, name=station_from_name)
    destination_station = get_object_or_404(models.Station, name=station_to_name)
    start_datetime = datetime.datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M')
    print(start_datetime)
    try:
        gen = plan(planning_mode, start_datetime, start_station, destination_station)
    except NoRouteExists:
        return HttpResponse("Route doesn't exist")
    except StationsAreTheSame:
        return HttpResponse("The start and destination can't be the same!")
    return HttpResponse('<br>'.join(f'{l} {t} --> {a}, {s} - {f}' for a, s, t, l, f in gen))


def index(request):
    stations = models.Station.objects.all()
    modes = list(PlanningMode)
    return render(request, 'tripplanner/index.html', {'stations': stations, 'modes': modes})


def redirect2result(request):
    return redirect(result, planning_mode_str=request.GET['planning_mode'], datetime_str=request.GET['datetime'],
                    station_from_name=request.GET['start_station'],
                    station_to_name=request.GET['destination_station'])
