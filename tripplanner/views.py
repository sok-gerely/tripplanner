import json

from django.http import HttpResponse, Http404
import datetime

from django.shortcuts import render, redirect, get_object_or_404

from tripplanner.planning_alg import plan, NoRouteExists, StationsAreTheSame, PlanningMode
from tripplanner import models
from tripplanner import constants


def result(request, planning_mode_str: str, date_str: str, time_str: str, station_from_name: str, station_to_name: str):
    try:
        planning_mode = PlanningMode(planning_mode_str)
    except ValueError:
        raise Http404('Planning mode in not valid!')
    start_station = get_object_or_404(models.Station, name=station_from_name)
    destination_station = get_object_or_404(models.Station, name=station_to_name)
    start_datetime = datetime.datetime.strptime(f'{date_str} {time_str}',
                                                f'{constants.date_fromat} {constants.time_format}')
    try:
        df = plan(planning_mode, start_datetime, start_station, destination_station)
    except NoRouteExists:
        return HttpResponse("Route doesn't exist")
    except StationsAreTheSame:
        return HttpResponse("The start and destination can't be the same!")
    return render(request, 'tripplanner/result.html', {'table': df.to_html()})


def index(request):
    stations = models.Station.objects.all()
    modes = list(PlanningMode)
    now = datetime.datetime.now()
    return render(request, 'tripplanner/index.html',
                  {'stations_json': json.dumps({station.name: None for station in stations}),
                   'modes': modes,
                   'today': now.date().strftime(constants.date_fromat),
                   'time': now.time().strftime(constants.time_format)})


def redirect2result(request):
    return redirect(result, planning_mode_str=request.GET['planning_mode'],
                    date_str=request.GET['date'],
                    time_str=request.GET['time'],
                    station_from_name=request.GET['start_station'],
                    station_to_name=request.GET['destination_station'])
