from enum import Enum
from math import inf
from collections import defaultdict
from dataclasses import dataclass
import datetime
from typing import Callable, List

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
            return get_neighbors_distance
        elif self == PlanningMode.COST:
            return get_neighbors_cost
        elif self == PlanningMode.TIME:
            return get_neighbors_time
        else:
            raise NotImplementedError()

    def __str__(self):
        return self.value


def plan(planning_mode: PlanningMode, start_time: datetime.time, start_station: Station, destination_station: Station):
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
    distance: float
    line_name: str
    u_leave_time: datetime.time
    v_arrive_time: datetime.time
    fee: int


@dataclass
class RouteInfo:
    prev: int
    line_prev: str
    time_leave_prev: datetime.time
    time_arrive: datetime.time
    fee: int


class Dijkstra:
    def __init__(self, get_neighbors) -> None:
        super().__init__()
        self.get_neighbors: Callable[[int, datetime.time], List[NeighbourResult]] = get_neighbors

    def __call__(self, start_station, start_time):
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

            neighbors = self.get_neighbors(u, info[u].time_arrive)
            for res in neighbors:
                alt = dist[u] + res.distance
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


def get_neighbors_distance(u, t):
    station_service = StationOrder.objects.filter(station_from=u).values_list(
        'station_to', 'distance', 'line__name', 'line__service', 'line__service__fee')

    res = []
    for v, distance, line__name, service, fee in station_service:
        v_arrive_time = TimetableData.objects.get(service=service, station=v).date_time
        u_leave_time = TimetableData.objects.get(service=service, station=u).date_time
        if u_leave_time >= t:
            res.append(NeighbourResult(v=v, distance=distance, line_name=line__name,
                                       u_leave_time=u_leave_time, v_arrive_time=v_arrive_time, fee=fee))
    return res


def get_neighbors_cost(u, t):
    station_service = StationOrder.objects.filter(station_from=u).values_list(
        'station_to', 'line__service__fee', 'line__name', 'line__service')

    res = []
    for v, fee, line__name, service in station_service:
        v_arrive_time = TimetableData.objects.get(service=service, station=v).date_time
        u_leave_time = TimetableData.objects.get(service=service, station=u).date_time
        if u_leave_time >= t:
            res.append(NeighbourResult(v=v, distance=fee, line_name=line__name,
                                       u_leave_time=u_leave_time, v_arrive_time=v_arrive_time, fee=fee))
    return res


def get_neighbors_time(u, t):
    station_service = StationOrder.objects.filter(station_from=u).values_list(
        'station_to', 'line__name', 'line__service', 'line__service__fee')

    res = []
    for v, line__name, service, fee in station_service:
        v_arrive_time = TimetableData.objects.get(service=service, station=v).date_time
        u_leave_time = TimetableData.objects.get(service=service, station=u).date_time
        if u_leave_time >= t:
            seconds = int((time2datetime(v_arrive_time) - time2datetime(t)).total_seconds())
            res.append(NeighbourResult(v=v, distance=seconds,
                                       line_name=line__name,
                                       u_leave_time=u_leave_time, v_arrive_time=v_arrive_time, fee=fee))
    return res


def time2datetime(t: datetime.time):
    return datetime.datetime(1, 1, 1, t.hour, t.minute, t.second, t.microsecond)
