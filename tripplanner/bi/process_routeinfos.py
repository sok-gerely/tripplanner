import datetime
from typing import List, Iterator, Tuple

import pandas as pd

from tripplanner.bi.dijkstra import RouteStationInfo, RouteInfo
from tripplanner.bi.utils import format_datetime
from tripplanner.models import Station, Line


def routeinfo2end_middlepoints(info, start_station, destination_station):
    df = __routeinfos2df(start_station, destination_station, info)
    endpoints_df = __split_df_to_middle_endpoints(df)
    middles_list = __get_list_zip_of_middle(df, endpoints_df)
    total_cost = endpoints_df['Fee'].sum()
    total_time = endpoints_df['End time'].iloc[-1] - endpoints_df.at[0, 'Start time']
    total_distance = endpoints_df['Distance'].sum()
    return _endpointsdf2list(endpoints_df), middles_list, total_cost, total_time, total_distance


def __routeinfos2df(start_station: Station, destination_station: Station, infos: RouteInfo) -> pd.DataFrame:
    route = [destination_station.id]
    while True:
        u = infos[route[-1]].prev
        route.append(u)
        if u == start_station.id:
            break
    route.reverse()
    df = pd.DataFrame(
        data=[(infos[r].time_arrive, infos[r].time_leave_prev, Station.objects.values_list('name', flat=True).get(id=r),
               infos[r].line_prev, infos[r].fee, infos[r].distance) for r in route],
        columns=['Arrive time', 'Leave time', 'Station', 'Line', 'Fee', 'Distance'])
    values2shift = ['Leave time', 'Line', 'Fee', 'Distance']
    df[values2shift] = df[values2shift].shift(-1)
    return df


def __split_df_to_middle_endpoints(df: pd.DataFrame) -> pd.DataFrame:
    df['prev line'] = df['Line'].shift(1)
    df['Middle Station'] = df['prev line'] == df['Line']
    ends_df = df[~df['Middle Station']]
    endpoints_df = __get_endpoints_df(ends_df)
    return endpoints_df


def __get_endpoints_df(ends_df: pd.DataFrame) -> pd.DataFrame:
    endpoints_df = pd.DataFrame({'Start station': ends_df['Station'][:-1],
                                 'End station': ends_df['Station'].shift(-1)[:-1],
                                 'Start time': ends_df['Leave time'][:-1],
                                 'End time': ends_df['Arrive time'].shift(-1)[:-1],
                                 'Start index': ends_df.index[:-1],
                                 'End index': ends_df.index[1:],
                                 'Fee': ends_df['Fee'][:-1],
                                 'Line': ends_df['Line'][:-1],
                                 'Distance': ends_df['Distance'][:-1]})
    endpoints_df['Travel time'] = (endpoints_df['End time'] - endpoints_df['Start time'])
    return endpoints_df


TransposeMiddle = Iterator[Tuple[datetime.datetime, Station]]


def __get_list_zip_of_middle(df: pd.DataFrame, endpoints_df: pd.DataFrame) -> List[TransposeMiddle]:
    middles_df = df[df['Middle Station']]
    middles_list = []
    for i, row in endpoints_df[['Start index', 'End index']].iterrows():
        df = middles_df[(row['Start index'] <= middles_df.index) & (middles_df.index <= row['End index'])]
        endpoints_df.at[i, 'Fee'] *= df.shape[0] + 1
        endpoints_df.at[i, 'Distance'] += df['Distance'].sum()
        middles_list.append(__middlesdf2zip(df))
    return middles_list


def __middlesdf2zip(df: pd.DataFrame) -> TransposeMiddle:
    return zip(df['Leave time'].apply(format_datetime).to_list(),
               df['Station'].to_list())


TransposeEndpoint = List[List]


def _endpointsdf2list(df: pd.DataFrame) -> TransposeEndpoint:
    types = [Line.objects.values_list('type', flat=True).get(name=l) for l in df['Line'].to_list()]
    return [df['Start time'].apply(format_datetime).to_list(),
            df['End time'].apply(format_datetime).to_list(),
            df['Start station'].to_list(),
            df['End station'].to_list(),
            df['Fee'].to_list(),
            df['Line'].to_list(),
            df['Travel time'].to_list(),
            types,
            df['Distance'].to_list()]
