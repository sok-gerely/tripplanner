from enum import Enum
from typing import List, Tuple, Iterator

import pandas as pd

from tripplanner.bi.dijkstra import Dijkstra, WeightArgs, RouteInfo
from tripplanner.models import *
from tripplanner import constants

TransposeMiddle = Iterator[Tuple[datetime.datetime, Station]]
TransposeEndpoint = List[List]


class NoRouteExists(Exception):
    pass


class StationsAreTheSame(Exception):
    pass


class PlanningMode(Enum):
    DISTANCE = 'distance'
    COST = 'cost'
    TIME = 'time'

    # ATTENTION: If a new value is added, change get_weight_fnc

    def get_weight_fnc(self):
        if self == PlanningMode.DISTANCE:
            return get_weight_distance
        elif self == PlanningMode.COST:
            return get_weight_cost
        elif self == PlanningMode.TIME:
            return get_weight_time
        else:
            raise NotImplementedError()

    def __str__(self):
        return self.value


def get_weight_distance(args: WeightArgs):
    return args.distance


def get_weight_cost(args: WeightArgs):
    return args.fee


def get_weight_time(args: WeightArgs):
    return (args.v_arrive_time - args.t).total_seconds()


def plan(planning_mode: PlanningMode, start_time: datetime.datetime, start_station: Station,
         destination_station: Station) -> Tuple[TransposeEndpoint, List[TransposeMiddle], float, float]:
    if start_station == destination_station:
        raise StationsAreTheSame()

    dijkstra = Dijkstra(planning_mode.get_weight_fnc())
    dist, info = dijkstra(start_station.id, start_time)
    if info[destination_station.id].time_arrive is None:
        raise NoRouteExists()

    df = __routeinfos2df(start_station, destination_station, info)
    endpoints_df = __split_df_to_middle_endpoints(df)
    middles_list = __get_list_zip_of_middle(df, endpoints_df)
    total_cost = endpoints_df['Fee'].sum(),
    total_time = endpoints_df['End time'].iloc[-1] - endpoints_df.at[0, 'Start time']
    return _endpointsdf2list(endpoints_df), middles_list, total_cost[0], total_time


def __routeinfos2df(start_station: Station, destination_station: Station, infos: List[RouteInfo]) -> pd.DataFrame:
    route = [destination_station.id]
    while True:
        u = infos[route[-1]].prev
        route.append(u)
        if u == start_station.id:
            break
    route.reverse()
    df = pd.DataFrame(
        data=[(infos[r].time_arrive, infos[r].time_leave_prev, Station.objects.values_list('name', flat=True).get(id=r),
               infos[r].line_prev, infos[r].fee) for r in route],
        columns=['Arrive time', 'Leave time', 'Station', 'Line', 'Fee'])
    values2shift = ['Leave time', 'Line', 'Fee']
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
                                 'Line': ends_df['Line'][:-1]})
    endpoints_df['Travel time'] = (endpoints_df['End time'] - endpoints_df['Start time'])  # .apply(
    # lambda x: f'{x.hour}')##.time().strptime(f'{time_str}'))
    return endpoints_df


def __get_list_zip_of_middle(df: pd.DataFrame, endpoints_df: pd.DataFrame) -> List[TransposeMiddle]:
    middles_df = df[df['Middle Station']]
    middles_list = []
    for i, row in endpoints_df[['Start index', 'End index']].iterrows():
        df = middles_df[(row['Start index'] <= middles_df.index) & (middles_df.index <= row['End index'])]
        endpoints_df.at[i, 'Fee'] *= df.shape[0] + 1
        middles_list.append(__middlesdf2zip(df))
    return middles_list


def __middlesdf2zip(df: pd.DataFrame) -> TransposeMiddle:
    return zip(df['Leave time'].apply(format_datetime).to_list(),
               df['Station'].to_list())


def _endpointsdf2list(df: pd.DataFrame) -> TransposeEndpoint:
    types = [Line.objects.values_list('type', flat=True).get(name=l) for l in df['Line'].to_list()]
    return [df['Start time'].apply(format_datetime).to_list(),
            df['End time'].apply(format_datetime).to_list(),
            df['Start station'].to_list(),
            df['End station'].to_list(),
            df['Fee'].to_list(),
            df['Line'].to_list(),
            df['Travel time'].to_list(),
            types]


def format_datetime(t):
    return t.strftime(f'{constants.time_format} {constants.date_fromat}')
