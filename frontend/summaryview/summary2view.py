from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_protect

import datetime, pytz
from datetime import timedelta
from django.utils import timezone

from django.db.models import Sum, Avg, Count
from django.db.models.functions import TruncDay 

import xlwt

from api.models import *

def summary_2_view(request):
    startdate = request.GET.get('startdate')
    enddate = request.GET.get('enddate')
    starttime = request.GET.get('starttime')
    endtime = request.GET.get('endtime')
    machine = Machine.objects.filter(user=request.user)
    machine_list = [] 
    for i in machine:
        machine_list.append(i.toDic()["machine_id"]) 
    if(startdate == None and enddate == None and starttime == None and endtime == None):
        timezone_localtime = timezone.localtime(timezone.now())
        enddate = startdate = timezone_localtime.strftime('%Y-%m-%d')  
        starttime = "00:00"
        endtime = "23:59"
    try:
        starttimestamp = int(datetime.datetime.strptime(str(startdate) + ' ' + starttime + ':00', "%Y-%m-%d %H:%M:%S").timestamp())
        endtimestamp = int(datetime.datetime.strptime(str(enddate) + ' ' + endtime + ':59', "%Y-%m-%d %H:%M:%S").timestamp())
        sizewiseoutput = PipeDataProcessed.objects.annotate(group_day=TruncDay('site_time')).values('group_day', 'basic_metarial', 'standard_type_classification', 'pressure_type_specification', 'outer_diameter', 'outer_diameter_unit', 'length', 'length_unit').annotate(Sum('weight'), Avg('weight'), Count('weight')).filter(timestamp__gte = starttimestamp, timestamp__lte = endtimestamp, machine_id__in = machine_list)
        sizewiseoutput.query.clear_ordering(force_empty = True)
        for i in sizewiseoutput:
            i['weight__sum'] /= 1000 
            i['weight__avg'] /= 1000 
    except:
        timezone_localtime = timezone.localtime(timezone.now())
        enddate = startdate = timezone_localtime.strftime('%Y-%m-%d')  
        starttime = (timezone_localtime - timedelta(hours=2)).strftime('%H:%M')
        endtime = timezone_localtime.strftime('%H:%M')
        starttimestamp = int(datetime.datetime.strptime(str(startdate) + ' ' + starttime + ':00', "%Y-%m-%d %H:%M:%S").timestamp())
        endtimestamp = int(datetime.datetime.strptime(str(enddate) + ' ' + endtime + ':59', "%Y-%m-%d %H:%M:%S").timestamp())
        sizewiseoutput = PipeDataProcessed.objects.annotate(group_day=TruncDay('site_time')).values('group_day', 'basic_metarial', 'standard_type_classification', 'pressure_type_specification', 'outer_diameter', 'outer_diameter_unit', 'length', 'length_unit').annotate(Sum('weight'), Avg('weight'), Count('weight')).filter(timestamp__gte = starttimestamp, timestamp__lte = endtimestamp, machine_id__in = machine_list)                                        
        sizewiseoutput.query.clear_ordering(force_empty = True)
        for i in sizewiseoutput:
            i['weight__sum'] /= 1000 
            i['weight__avg'] /= 1000 
    print(starttimestamp, endtimestamp)
    return 'summary_2.html', {"machine": machine, "summary_name": "MIS 2 : SIZE WISE OUTPUT", "startdate": startdate, "enddate": enddate, "starttime": starttime, "endtime": endtime, "sizewiseoutput": sizewiseoutput}
