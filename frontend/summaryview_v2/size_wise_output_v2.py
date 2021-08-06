from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_protect

import datetime, pytz
from datetime import timedelta
from django.utils import timezone as tuto

from django.db.models import Sum, Avg, Count
from django.db.models.functions import TruncDay 

import xlwt

from api.models import *
from pytz import timezone

def summary_2_view(request):
    startdate = request.GET.get('startdate')
    enddate = request.GET.get('enddate')
    enddate_searched = enddate
    machine = Machine.objects.filter(user=request.user)
    machine_list = [] 
    startdate_re=startdate
    for i in machine:
        machine_list.append(i.toDic()["machine_id"])
    #----Souren<24/04/2021>---------------------------->
    machine_details=Machine.objects.get(machine_id=machine_list[0])
    start_time = machine_details.shift1_start_time
    machine_total_shift = machine_details.machine_total_shift
    if machine_total_shift==2:
        end_time = machine_details.shift2_end_time
    else:
        end_time = machine_details.shift3_end_time
    shift1_time_duration = machine_details.shift1_time_duration
    shift2_time_duration = machine_details.shift2_time_duration
    if machine_total_shift==3:
        shift3_time_duration = machine_details.shift3_time_duration
    else:
        shift3_time_duration = 0

    if(startdate == None and enddate == None):
        timezone_localtime = tuto.localtime(tuto.now())
        enddate = startdate = timezone_localtime.strftime('%Y-%m-%d')  
        start_time = start_time
        end_time = end_time
    if (shift1_time_duration+shift2_time_duration+shift3_time_duration==24.00):
        shift_flag = True
        enddate = (datetime.datetime.strptime(enddate, '%Y-%m-%d')+timedelta(days=1)).strftime('%Y-%m-%d')
    local_zone = MachineTimeZone.objects.get(machine_id=machine_list[0]).machine_timezone

    endtimestamp = int(timezone(local_zone).localize(datetime.datetime.strptime(str(enddate) + ' ' + str(end_time), "%Y-%m-%d %H:%M:%S")).timestamp())
    starttimestamp = int(timezone(local_zone).localize(datetime.datetime.strptime(str(startdate) + ' ' + str(start_time), "%Y-%m-%d %H:%M:%S")).timestamp())
    sizewiseoutput = PipeDataProcessed.objects.annotate(group_day=TruncDay('site_time')).filter(timestamp__gte = starttimestamp, timestamp__lte = endtimestamp, machine_id__in = machine_list).values('group_day', 'basic_metarial', 'standard_type_classification', 'pressure_type_specification', 'outer_diameter', 'outer_diameter_unit', 'length', 'length_unit', 'shift').annotate(Sum('weight'), Avg('weight'), Count('weight'))
    sizewiseoutput.query.clear_ordering(force_empty = True)
    sizewiseoutput=sizewiseoutput.order_by('group_day')
    previous_day=datetime.datetime.strptime(startdate, '%Y-%m-%d')
    for i in sizewiseoutput:
        i['weight__sum'] /= 1000 
        i['weight__avg'] /= 1000
        i['next_day']=i['group_day']
        

   
    machine_total_shift=str(machine_total_shift)
    return 'summary_2.html', {"machine": machine, "summary_name": "MIS2", "startdate": startdate_re, "enddate": enddate, "sizewiseoutput": sizewiseoutput, 'starttimestamp': starttimestamp, "enddate_searched":enddate_searched, 'machine_total_shift': machine_total_shift, 'sizewiseoutput':sizewiseoutput}
