import pandas as pd
import json

from django.http import HttpResponse, Http404
import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import NoReverseMatch

from tripplanner.planning_alg import plan, NoRouteExists, StationsAreTheSame, PlanningMode
from tripplanner import models
from tripplanner import constants


def result(request, planning_mode_str: str, date_str: str, time_str: str, station_from_name: str, station_to_name: str):
    try:
        planning_mode = PlanningMode(planning_mode_str)
    except ValueError:
        return render(request, 'tripplanner/error.html', {'message': "Planning mode in not valid!"})
    start_station = get_object_or_404(models.Station, name=station_from_name)
    destination_station = get_object_or_404(models.Station, name=station_to_name)
    start_datetime = datetime.datetime.strptime(f'{date_str} {time_str}',
                                                f'{constants.date_fromat} {constants.time_format}')
    try:
        df = plan(planning_mode, start_datetime, start_station, destination_station)
        # ['Arrive time', 'Leave time', 'Station', 'Line', 'Fee']
        df['prev line'] = df['Line'].shift(1)
        df['Middle Station'] = df['prev line'] == df['Line']
        ends_df = df[~df['Middle Station']]
        middles_df = df[df['Middle Station']]
        endpoints_df = pd.DataFrame({'Start station': ends_df['Station'][:-1],
                                     'End station': ends_df['Station'].shift(-1)[:-1],
                                     'Start time': ends_df['Leave time'][:-1],
                                     'End time': ends_df['Arrive time'].shift(-1)[:-1],
                                     'Start index': ends_df.index[:-1],
                                     'End index': ends_df.index[1:],
                                     'Fee': ends_df['Fee'][:-1],
                                     'Line': ends_df['Line'][:-1]})
        endpoints_df['Travel time'] = (endpoints_df['End time'] - endpoints_df['Start time'])  # .apply(
        # lambda x: f'{x.hour}')##.time().strptime(f'{time_str}'))
        middles_zips = []
        for i, row in endpoints_df[['Start index', 'End index']].iterrows():
            df = middles_df[(row['Start index'] <= middles_df.index) & (middles_df.index <= row['End index'])]
            endpoints_df.at[i, 'Fee'] *= df.shape[0] + 1
            middles_zips.append(middlesdf2list(df))
    except NoRouteExists:
        return render(request, 'tripplanner/error.html', {'message': "Route doesn't exist!"})
    except StationsAreTheSame:
        return render(request, 'tripplanner/error.html', {'message': "The start and destination can't be the same!"})

    data = endpointsdf2list(endpoints_df)
    data.append(middles_zips)
    return render(request, 'tripplanner/result.html',
                  {'data': zip(*data), 'total_cost': endpoints_df['Fee'].sum(),
                   'total_time': endpoints_df['End time'].iloc[-1] - endpoints_df.at[0, 'Start time']})


def format_datetime(t):
    return t.strftime(f'{constants.time_format} {constants.date_fromat}')


def middlesdf2list(df):
    return zip(df['Leave time'].apply(format_datetime).to_list(),
               df['Station'].to_list())


def endpointsdf2list(df):
    return [df['Start time'].apply(format_datetime).to_list(),
            df['End time'].apply(format_datetime).to_list(),
            df['Start station'].to_list(),
            df['End station'].to_list(),
            df['Fee'].to_list(),
            df['Line'].to_list(),
            df['Travel time'].to_list()]


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
    try:
        return redirect(result, planning_mode_str=request.GET['planning_mode'],
                        date_str=request.GET['date'],
                        time_str=request.GET['time'],
                        station_from_name=request.GET['start_station'],
                        station_to_name=request.GET['destination_station'])
    except NoReverseMatch:
        return render(request, 'tripplanner/error.html', {'message': 'You have to fill all fields!'})
