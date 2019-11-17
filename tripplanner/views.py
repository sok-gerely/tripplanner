from django.http import HttpResponse

from tripplanner.planning_alg import plan


def index(request):
    gen = plan()
    return HttpResponse('<br>'.join(f'{a} --> {t}, {s}, {l}' for a, s, t, l in gen))
