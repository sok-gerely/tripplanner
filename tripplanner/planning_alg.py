from math import inf
from collections import defaultdict

from tripplanner.models import *


def plan():
    start_name = 'A'
    destination_name = 'D'
    start = Station.objects.get(name=start_name)
    destination = Station.objects.get(name=destination_name)

    dijkstra = Dijkstra(get_neighbors_distance)
    dist, prev = dijkstra(start)
    route = [destination]
    while True:
        u = prev[route[-1]]
        route.append(u)
        if u == start:
            break
    route.reverse()

    return dist[destination], route


class Dijkstra:
    def __init__(self, get_neighbors) -> None:
        super().__init__()
        self.get_neighbors = get_neighbors

    def __call__(self, start):
        Q = list(Station.objects.all())
        dist = defaultdict(lambda: inf)
        prev = defaultdict(None)
        dist[start] = 0
        while len(Q) != 0:
            u = self.get_Q_min_dist(Q, dist)
            Q.remove(u)

            for v, w in self.get_neighbors(u):
                alt = dist[u] + w
                if alt < dist[v]:
                    dist[v] = alt
                    prev[v] = u
        return dist, prev

    def get_Q_min_dist(self, Q, dist):
        min_d = inf
        min_u = None
        for u, d in dist.items():
            if (u in Q) & (d < min_d):
                min_d = d
                min_u = u
        return min_u


def get_neighbors_distance(u):
    return [(station_order.station_to, station_order.distance) for station_order in
            StationOrder.objects.filter(station_from=u)]


def get_neighbors_dost(u):
    pass


def get_neighbors_time(u):
    pass
