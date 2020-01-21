from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core import serializers

import re
import json
import datetime

from .models import PipeData

# Create your views here.
def GetStringGetMethod(request):
    mid = ''
    b = ''
    c = ''
    d = ''
    e = ''
    ts = ''
    count = ''
    weight = ''
    ps = ''
    site_time = ''

    mid = request.GET.get('a')
    b = request.GET.get('b')
    c = request.GET.get('c')
    d = request.GET.get('d')
    e = request.GET.get('e')
    m = request.GET.get('m')
    if re.search(r'\w+\$\w+\$\w+\$\w+$', m):
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
        if ts.isdigit():
            site_time = datetime.datetime.fromtimestamp(int(ts)).replace(tzinfo=datetime.timezone.utc).isoformat()
    try:
        PipeData.objects.create(mid = mid, b = b, c = c, d = d, e = e, ts = ts, count = count, weight = weight, ps = ps, site_time = site_time)
    except Exception as e:
        print(e)
    return HttpResponse(status=200)

def index(request):
    data = {"data": []}
    for i in PipeData.objects.all():
        data["data"].append(i.toDic())
    return JsonResponse(data)
