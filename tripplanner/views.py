from django.http import HttpResponse

from tripplanner.planning_alg import plan


def index(request):
    gen = plan()
    return HttpResponse('<br>'.join(f'{l} {t} --> {a}, {s}' for a, s, t, l in gen))
