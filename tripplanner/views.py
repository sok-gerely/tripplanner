from django.shortcuts import render
from django.http import HttpResponse

from tripplanner.planning_alg import plan

# Create your views here.
def index(request):
    # return HttpResponse('Hy there!')
    return HttpResponse(plan())
