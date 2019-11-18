from django.http import HttpResponse
import datetime

from tripplanner.planning_alg import plan, NoRouteExists


def index(request, planning_mode: str, time_int: int, station_from_name: str, station_to_name: str):
    start_time = datetime.time(time_int // 100, time_int % 100)
    print(start_time)
    try:
        gen = plan(planning_mode, start_time, station_from_name, station_to_name)
    except NoRouteExists:
        return HttpResponse("Route doesn't exist")
    return HttpResponse('<br>'.join(f'{l} {t} --> {a}, {s} - {f}' for a, s, t, l, f in gen))
