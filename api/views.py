from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core import serializers

import re
import json

from .models import PipeData

# Create your views here.
def GetStringGetMethod(request):
    mid = ''
    b = ''
    c = ''
    ts = ''
    count = ''
    weight = ''
    ps = ''

    mid = request.GET.get('a')
    b = request.GET.get('b')
    c = request.GET.get('c')
    m = request.GET.get('m')
    if re.search(r'^[0-9]+\$[0-9]+\$[0-9]+\.[0-9]+\$\w{6,7}$', m):
        flag = 'ts'
        for i in m:
            if i == '$':
                if flag == 'ts':
                    flag = 'count'
                elif flag == 'count':
                    flag = 'weight'
                elif flag == 'weight':
                    flag = 'ps'
            else:
                if flag == 'ts':
                    ts += i
                elif flag == 'count':
                    count += i
                elif flag == 'weight':
                    weight += i
                else:
                    ps += i
    try:
        PipeData.objects.create(mid = mid, b = b, c = c, ts = ts, count = count, weight = weight, ps = ps)
    except Exception as e:
        print(e)
    return HttpResponse(status=200)

def index(request):
    data = {"data": []}
    for i in PipeData.objects.all():
        data["data"].append(i.toDic())
    return JsonResponse(data)
