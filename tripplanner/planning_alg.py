from math import inf
from collections import defaultdict
import datetime

from tripplanner.models import *


def plan():
    start_name = 'A'
    destination_name = 'D'
    start_time = datetime.time(10, 0, 0, 0)
    start_station = Station.objects.get(name=start_name)
    destination_station = Station.objects.get(name=destination_name)

    dijkstra = Dijkstra(get_neighbors_distance)
    dist, prev, time, line = dijkstra(start_station.id, start_time)
    route = [destination_station.id]
    while True:
        u = prev[route[-1]]
        route.append(u)
        if u == start_station.id:
            break
    route.reverse()

    return zip([(Station.objects.values_list('name', flat=True).get(id=r), time[r]) for r in route], [line[r] for r in route[1:]] + [None, ])


class Dijkstra:
    def __init__(self, get_neighbors) -> None:
        super().__init__()
        self.get_neighbors = get_neighbors

    def __call__(self, start_station, start_time):
        Q = list(Station.objects.values_list('id', flat=True))
        dist = defaultdict(lambda: inf)
        time = defaultdict(lambda: inf)
        prev = defaultdict(None)
        line = defaultdict(None)
        dist[start_station] = 0
        time[start_station] = start_time
        while len(Q) != 0:
            u = self.get_Q_min_dist(Q, dist)
            if u is None:
                break
            Q.remove(u)

            neighbors = self.get_neighbors(u, time[u])
            for v, d, l, t in neighbors:
                alt = dist[u] + d
                if alt < dist[v]:
                    dist[v] = alt
                    prev[v] = u
                    time[v] = t
                    line[v] = l
        return dist, prev, time, line

    def get_Q_min_dist(self, Q, dist):
        min_d = inf
        min_u = None
        for u, d in dist.items():
            if (u in Q) & (d < min_d):
                min_d = d
                min_u = u
        return min_u


def get_neighbors_distance(u, t):
    return StationOrder.objects.filter(station_from=u, line__service__timetabledata__date_time__gt=t).values_list(
        'station_to', 'distance', 'line__name', 'line__service__timetabledata__date_time')


def get_neighbors_dost(u):
    pass


def get_neighbors_time(u):
    pass
