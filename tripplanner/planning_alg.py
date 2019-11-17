from math import inf
from collections import defaultdict, namedtuple
import datetime
from typing import Callable, List

from django.db.models import Q

from tripplanner.models import *


def plan():
    start_name = 'A'
    destination_name = 'D'
    start_time = datetime.time(10, 0, 0, 0)
    start_station = Station.objects.get(name=start_name)
    destination_station = Station.objects.get(name=destination_name)

    dijkstra = Dijkstra(get_neighbors_distance)
    dist, prev, time_leave, time_arrive, line = dijkstra(start_station.id, start_time)
    route = [destination_station.id]
    while True:
        u = prev[route[-1]]
        route.append(u)
        if u == start_station.id:
            break
    route.reverse()

    time_arrive[start_station.id] = None
    time_leave[destination_station.id] = None
    line[destination_station.id] = None

    return [(time_arrive[r], Station.objects.values_list('name', flat=True).get(id=r), time_leave[r], line[r]) for r in
            route]


NeighbourResult = namedtuple('NeighbourResult',
                             ['v', 'distance', 'line_name', 'u_leave_time', 'v_arrive_time'])


class Dijkstra:
    def __init__(self, get_neighbors) -> None:
        super().__init__()
        self.get_neighbors: Callable[[int, datetime.time], List[NeighbourResult]] = get_neighbors

    def __call__(self, start_station, start_time):
        Q = list(Station.objects.values_list('id', flat=True))
        dist = defaultdict(lambda: inf)
        time_arrive = defaultdict(lambda: inf)
        time_leave = defaultdict(lambda: inf)
        prev = defaultdict(None)
        line = defaultdict(None)
        dist[start_station] = 0
        time_arrive[start_station] = start_time
        while len(Q) != 0:
            u = self.get_Q_min_dist(Q, dist)
            if u is None:
                break
            Q.remove(u)

            neighbors = self.get_neighbors(u, time_arrive[u])
            for res in neighbors:
                alt = dist[u] + res.distance
                if alt < dist[res.v]:
                    dist[res.v] = alt
                    prev[res.v] = u
                    time_arrive[res.v] = res.v_arrive_time
                    time_leave[u] = res.u_leave_time
                    line[u] = res.line_name
        return dist, prev, time_leave, time_arrive, line

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
        'station_to', 'distance', 'line__name', 'line__service')

    res = []
    for v, distance, line__name, service in station_service:
        v_arrive_time = TimetableData.objects.get(service=service, station=v).date_time
        u_leave_time = TimetableData.objects.get(service=service, station=u).date_time
        if u_leave_time >= t:
            res.append(NeighbourResult(v=v, distance=distance, line_name=line__name,
                                       u_leave_time=u_leave_time, v_arrive_time=v_arrive_time))
    return res


def get_neighbors_cost(u, t):
    station_service = StationOrder.objects.filter(station_from=u).values_list(
        'station_to', 'fee', 'line__name', 'line__service')

    res = []
    for v, distance, line__name, service in station_service:
        v_arrive_time = TimetableData.objects.get(service=service, station=v).date_time
        u_leave_time = TimetableData.objects.get(service=service, station=u).date_time
        if u_leave_time > t:
            res.append(NeighbourResult(v=v, distance=distance, line_name=line__name,
                                       u_leave_time=u_leave_time, v_arrive_time=v_arrive_time))
    return res


def get_neighbors_time(u, t):
    return StationOrder.objects.filter(station_from=u, line__service__timetabledata__date_time__gt=t).values_list(
        'station_to', 'line__service__fee', 'line__name', 'line__service__timetabledata__date_time')
