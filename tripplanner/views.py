from django.http import HttpResponse

from tripplanner.planning_alg import plan


# Create your views here.
def index(request):
    # return HttpResponse('Hy there!')
    d, route = plan()
    return HttpResponse(', '.join(str(r) for r in route))
