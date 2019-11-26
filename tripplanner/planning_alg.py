from enum import Enum
from typing import List

import pandas as pd

from tripplanner.bi.dijkstra import Dijkstra, WeightArgs, RouteInfo
from tripplanner.models import *


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


def plan(planning_mode: PlanningMode, start_time: datetime.datetime, start_station: Station,
         destination_station: Station) -> pd.DataFrame:
    if start_station == destination_station:
        raise StationsAreTheSame()

    dijkstra = Dijkstra(planning_mode.get_weight_fnc())
    dist, info = dijkstra(start_station.id, start_time)
    if info[destination_station.id].time_arrive is None:
        raise NoRouteExists()

    df = __routeinfos2df(start_station, destination_station, info)
    return df


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


def get_weight_distance(args: WeightArgs):
    return args.distance


def get_weight_cost(args: WeightArgs):
    return args.fee


def get_weight_time(args: WeightArgs):
    return (args.v_arrive_time - args.t).total_seconds()
