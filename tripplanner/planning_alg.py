from enum import Enum
from typing import List, Tuple

from tripplanner.bi.dijkstra import Dijkstra, WeightArgs
from tripplanner.bi.process_routeinfos import _endpointsdf2list, TransposeMiddle, TransposeEndpoint, \
    routeinfo2end_middlepoints
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


def get_weight_distance(args: WeightArgs):
    return args.distance


def get_weight_cost(args: WeightArgs):
    return args.fee


def get_weight_time(args: WeightArgs):
    return (args.v_arrive_time - args.t).total_seconds()


def plan(planning_mode: PlanningMode, start_time: datetime.datetime, start_station: Station,
         destination_station: Station) -> Tuple[TransposeEndpoint, List[TransposeMiddle], float, float, float]:
    if start_station == destination_station:
        raise StationsAreTheSame()

    dijkstra = Dijkstra(planning_mode.get_weight_fnc())
    info = dijkstra(start_station.id, start_time)
    if info[destination_station.id].time_arrive is None:
        raise NoRouteExists()

    return routeinfo2end_middlepoints(info, start_station, destination_station)


