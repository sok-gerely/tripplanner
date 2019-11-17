from django.http import HttpResponse

from tripplanner.planning_alg import plan


def index(request):
    gen = plan()
    return HttpResponse('<br>'.join(f'{r}, {l}, {t}' for (r, t), l in gen))
