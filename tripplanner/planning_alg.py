from enum import Enum
from math import inf
from collections import defaultdict
from dataclasses import dataclass
import datetime
from typing import Callable, List

from tripplanner.models import *
from tripplannersite.settings import CALENDAR


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
            return get_cost_distance
        elif self == PlanningMode.COST:
            return get_cost_cost
        elif self == PlanningMode.TIME:
            return get_cost_time
        else:
            raise NotImplementedError()

    def __str__(self):
        return self.value


def plan(planning_mode: PlanningMode, start_time: datetime.datetime, start_station: Station,
         destination_station: Station):
    if start_station == destination_station:
        raise StationsAreTheSame()

    dijkstra = Dijkstra(planning_mode.get_weight_fnc())
    dist, info = dijkstra(start_station.id, start_time)
    if info[destination_station.id].time_arrive is None:
        raise NoRouteExists()

    route = [destination_station.id]
    while True:
        u = info[route[-1]].prev
        route.append(u)
        if u == start_station.id:
            break
    route.reverse()

    return [(info[r].time_arrive, Station.objects.values_list('name', flat=True).get(id=r), info[r].time_leave_prev,
             info[r].line_prev, info[r].fee) for r in route]


@dataclass
class NeighbourResult:
    v: int
    cost: float
    line_name: str
    u_leave_time: datetime.datetime
    v_arrive_time: datetime.datetime
    fee: int


@dataclass
class RouteInfo:
    prev: int
    line_prev: str
    time_leave_prev: datetime.datetime
    time_arrive: datetime.datetime
    fee: int


class Dijkstra:
    def __init__(self, get_cost) -> None:
        super().__init__()
        self.get_cost: Callable[[int, datetime.time], List[NeighbourResult]] = get_cost

    def __call__(self, start_station: int, start_time: datetime.datetime):
        Q = list(Station.objects.values_list('id', flat=True))
        dist = defaultdict(lambda: inf)
        info = defaultdict(lambda: RouteInfo(None, None, None, None, None))

        dist[start_station] = 0
        info[start_station].time_arrive = start_time

        while len(Q) != 0:
            u = self.get_Q_min_dist(Q, dist)
            if u is None:
                break
            Q.remove(u)

            neighbors = get_neighbors(u, info[u].time_arrive, self.get_cost)
            for res in neighbors:
                alt = dist[u] + res.cost
                if alt < dist[res.v]:
                    dist[res.v] = alt
                    info[res.v].prev = u
                    info[res.v].time_arrive = res.v_arrive_time
                    info[res.v].time_leave_prev = res.u_leave_time
                    info[res.v].line_prev = res.line_name
                    info[res.v].fee = res.fee
        return dist, info

    def get_Q_min_dist(self, Q, dist):
        min_d = inf
        min_u = None
        for u, d in dist.items():
            if (u in Q) & (d < min_d):
                min_d = d
                min_u = u
        return min_u


def is_weekend(t: datetime.datetime):
    return t.weekday() >= 5


def is_holiday(t: datetime.datetime):
    return t in CALENDAR


def datetime2TimetableData_TYPE(t: datetime.datetime):
    if is_weekend(t):
        return TimetableData.WEEKEND
    elif is_holiday(t):
        return TimetableData.HOLIDAY
    else:
        return TimetableData.NORMAL


@dataclass
class WeightArgs:
    distance: int
    fee: int
    v_arrive_time: datetime.datetime
    t: datetime.datetime


def get_cost_distance(args: WeightArgs):
    return args.distance


def get_cost_cost(args: WeightArgs):
    return args.fee


def get_cost_time(args: WeightArgs):
    return (args.v_arrive_time - args.t).total_seconds()


def get_neighbors(u, t: datetime.datetime, get_cost):
    station_service = StationOrder.objects.filter(station_from=u).values_list(
        'station_to', 'distance', 'line__name', 'line__service', 'line__service__fee')

    res = []
    for v, distance, line__name, service, fee in station_service:
        query_t = t
        while True:
            timetabledata_type = datetime2TimetableData_TYPE(query_t)
            get_station_datetime = lambda s: \
                datetime.datetime.combine(query_t.date(),
                                          TimetableData.objects.get(service=service, station=s,
                                                                    type=timetabledata_type).date_time)
            try:
                v_arrive_time = get_station_datetime(v)
                u_leave_time = get_station_datetime(u)
                if u_leave_time >= t:
                    res.append(NeighbourResult(v=v, cost=get_cost(
                        WeightArgs(distance=distance, fee=fee, v_arrive_time=v_arrive_time, t=t)), line_name=line__name,
                                               u_leave_time=u_leave_time, v_arrive_time=v_arrive_time, fee=fee))
                    break
                else:
                    raise TimetableData.DoesNotExist
            except TimetableData.DoesNotExist:
                query_t = (query_t + datetime.timedelta(days=1)).replace(hour=0, minute=0, microsecond=0)
    return res


def time2datetime(t: datetime.time):
    return datetime.datetime(1, 1, 1, t.hour, t.minute, t.second, t.microsecond)
