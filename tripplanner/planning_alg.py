from math import inf
from collections import defaultdict

from tripplanner.models import *


def plan():
    start_name = 'A'
    destination_name = 'D'
    start = Station.objects.get(name=start_name)
    Q = list(Station.objects.all())
    dist = defaultdict(lambda: inf)
    prev = defaultdict(None)
    dist[start] = 0

    # return get_Q_min_dist(Q, dist)
    while len(Q) != 0:
        u = get_Q_min_dist(Q, dist)
        Q.remove(u)

        for v, w in get_neighbors(u):
            alt = dist[u] + w
            if alt < dist[v]:
                dist[v] = alt
                prev[v] = u

    destination = Station.objects.get(name=destination_name)
    route = [destination]
    while True:
        u = prev[route[-1]]
        route.append(u)
        if u == start:
            break
    route.reverse()

    return dist[destination], route


def get_Q_min_dist(Q, dist):
    min_d = inf
    min_u = None
    for u, d in dist.items():
        if (u in Q) & (d < min_d):
            min_d = d
            min_u = u
    return min_u


def get_neighbors(u):
    return [(station_order.station_to, station_order.distance) for station_order in
            StationOrder.objects.filter(station_from=u)]
