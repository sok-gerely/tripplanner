import datetime
from collections import defaultdict
from dataclasses import dataclass
from math import inf
from typing import Callable, List, Dict

from tripplanner.bi.utils import datetime2ServiceTYPE
from tripplanner.models import Station, StationOrder, TimetableData


@dataclass
class WeightArgs:
    distance: int
    fee: int
    v_arrive_time: datetime.datetime
    t: datetime.datetime


@dataclass
class RouteInfo:
    prev: int
    line_prev: str
    time_leave_prev: datetime.datetime
    time_arrive: datetime.datetime
    fee: int


class Dijkstra:
    def __init__(self, get_weight: Callable[[WeightArgs], float]):
        super().__init__()
        self.get_weight = get_weight

    def __call__(self, start_station: int, start_time: datetime.datetime) -> Dict[int, RouteInfo]:
        stations = list(Station.objects.values_list('id', flat=True))
        dist = defaultdict(lambda: inf)
        info = defaultdict(lambda: RouteInfo(None, None, None, None, None))

        dist[start_station] = 0
        info[start_station].time_arrive = start_time

        while len(stations) != 0:
            u = self.__get_stations_with_min_dist(stations, dist)
            if u is None:
                break
            stations.remove(u)

            neighbors = self.__get_neighbors(u, info[u].time_arrive)
            for res in neighbors:
                alt = dist[u] + res.cost
                if alt < dist[res.v]:
                    dist[res.v] = alt
                    self.__update_info(info, res, u)
        return dist, info

    @staticmethod
    def __update_info(info: Dict[int, RouteInfo], res: Dijkstra.NeighbourResult, u: int):
        info[res.v].prev = u
        info[res.v].time_arrive = res.v_arrive_time
        info[res.v].time_leave_prev = res.u_leave_time
        info[res.v].line_prev = res.line_name
        info[res.v].fee = res.fee

    @staticmethod
    def __get_stations_with_min_dist(stations: List[int], dist: Dict[int, float]):
        min_d = inf
        min_u = None
        for u, d in dist.items():
            if (u in stations) & (d < min_d):
                min_d = d
                min_u = u
        return min_u

    def __get_neighbors(self, u: int, t: datetime.datetime) -> Dijkstra.NeighbourResult:
        station_service = StationOrder.objects.filter(station_from=u).values_list(
            'station_to', 'distance', 'line__name', 'line__service', 'line__service__fee')

        res = []
        for v, distance, line__name, service, fee in station_service:
            query_t = t
            while True:
                timetabledata_type = datetime2ServiceTYPE(query_t)
                get_station_datetime = lambda s: \
                    TimetableData.objects.get(service=service, station=s,
                                              service__type=timetabledata_type).get_actual_datetime(query_t.date())
                try:
                    v_arrive_time = get_station_datetime(v)
                    u_leave_time = get_station_datetime(u)
                    if u_leave_time > v_arrive_time:
                        v_arrive_time += datetime.timedelta(days=1)
                    if u_leave_time >= t:
                        weight = self.get_weight(
                            WeightArgs(distance=distance, fee=fee, v_arrive_time=v_arrive_time, t=t))
                        res.append(Dijkstra.NeighbourResult(v=v, cost=weight, line_name=line__name,
                                                            u_leave_time=u_leave_time, v_arrive_time=v_arrive_time,
                                                            fee=fee))
                        break
                    else:
                        raise TimetableData.DoesNotExist
                except TimetableData.DoesNotExist:
                    query_t = (query_t + datetime.timedelta(days=1)).replace(hour=0, minute=0, microsecond=0)
        return res

    @dataclass
    class NeighbourResult:
        v: int
        cost: float
        line_name: str
        u_leave_time: datetime.datetime
        v_arrive_time: datetime.datetime
        fee: int
