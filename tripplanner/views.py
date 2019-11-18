from django.http import HttpResponse

from tripplanner.planning_alg import plan


def index(request, planning_mode: str, station_from_name: str, station_to_name: str):
    gen = plan(planning_mode, station_from_name, station_to_name)
    return HttpResponse('<br>'.join(f'{l} {t} --> {a}, {s} - {f}' for a, s, t, l, f in gen))
