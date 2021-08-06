from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_protect

import datetime, pytz
from datetime import timedelta
from django.utils import timezone as util_timezone

from django.db.models import Sum, Avg, Count
from django.db.models.functions import TruncDay 

import xlwt

from api.models import *
from pytz import timezone

def summary_7_view(request):
    startdate = request.GET.get('startdate')
    enddate = request.GET.get('enddate')
    machine = Machine.objects.filter(user=request.user)
    machine_list = [] 
    for i in machine:
        machine_list.append(i.toDic()["machine_id"])
    #---Souren Ghosh---24/04/2021----------
    machine_details = Machine.objects.get(machine_id=machine_list[0])
    starttime = machine_details.shift1_start_time
    machine_total_shift = machine_details.machine_total_shift
    if machine_total_shift==2:
        endtime = machine_details.shift2_end_time
    else:
        endtime = machine_details.shift3_end_time

    shift1_time_duration = machine_details.shift1_time_duration
    shift2_time_duration = machine_details.shift2_time_duration
    if machine_total_shift==3:
        shift3_time_duration = machine_details.shift3_time_duration
    else:
        shift3_time_duration=0

    if(startdate == None and enddate == None):
        timezone_localtime = util_timezone.localtime(util_timezone.now())
        enddate = startdate = timezone_localtime.strftime('%Y-%m-%d')  
        starttime = starttime
        endtime = endtime
    if (shift1_time_duration+shift2_time_duration+shift3_time_duration)==24.00:
        l=enddate.split('-')
        day_of_date = int(l[2])+1
        enddate = l[0] + "-" + l[1] + "-" + str(day_of_date)
    local_zone = MachineTimeZone.objects.get(machine_id=machine_list[0]).machine_timezone
    try:
        starttimestamp = int(timezone(local_zone).localize(datetime.datetime.strptime(str(startdate) + ' ' + str(starttime), "%Y-%m-%d %H:%M:%S")).timestamp())
        endtimestamp = int(timezone(local_zone).localize(datetime.datetime.strptime(str(enddate) + ' ' + str(endtime), "%Y-%m-%d %H:%M:%S")).timestamp())
        sizewiselength = PipeDataProcessed.objects.annotate(group_day=TruncDay('site_time')).values('group_day', 'basic_metarial', 'standard_type_classification', 'pressure_type_specification', 'outer_diameter', 'outer_diameter_unit', 'length', 'length_unit', 'shift').annotate(Sum('length'), Count('weight')).filter(timestamp__gte = starttimestamp, timestamp__lte = endtimestamp, machine_id__in = machine_list) 
        sizewiselength.query.clear_ordering(force_empty = True)
        sizewiselength = sizewiselength.order_by('group_day', 'shift')
    except:
        timezone_localtime = util_timezone.localtime(util_timezone.now())
        enddate = startdate = timezone_localtime.strftime('%Y-%m-%d')  
        starttime = (timezone_localtime - timedelta(hours=2)).strftime('%H:%M')
        endtime = timezone_localtime.strftime('%H:%M')
        starttimestamp = int(timezone(local_zone).localize(datetime.datetime.strptime(str(startdate) + ' ' + starttime + ':00', "%Y-%m-%d %H:%M:%S")).timestamp())
        endtimestamp = int(timezone(local_zone).localize(datetime.datetime.strptime(str(enddate) + ' ' + endtime + ':59', "%Y-%m-%d %H:%M:%S")).timestamp())
        sizewiselength = PipeDataProcessed.objects.annotate(group_day=TruncDay('site_time')).values('group_day', 'basic_metarial', 'standard_type_classification', 'pressure_type_specification', 'outer_diameter', 'outer_diameter_unit', 'length', 'length_unit').annotate(Sum('length'), Count('weight')).filter(timestamp__gte = starttimestamp, timestamp__lte = endtimestamp, machine_id__in = machine_list) 
        sizewiselength.query.clear_ordering(force_empty = True)
        
    # print(starttimestamp, endtimestamp, sizewiselength)
    return 'summary_7.html', {"machine": machine, "summary_name": "MIS 7 : SIZE WISE LENGTH",  "startdate": startdate, "enddate": enddate, "starttime": starttime, "endtime": endtime, "sizewiselength": sizewiselength}
