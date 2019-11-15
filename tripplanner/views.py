from django.http import HttpResponse

from tripplanner.planning_alg import plan


def index(request):
    d, route = plan()
    return HttpResponse(', '.join(str(r) for r in route))
