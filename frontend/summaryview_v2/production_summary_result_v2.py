from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_protect

import time
import datetime, pytz
from datetime import timedelta
from django.utils import timezone

from django.db.models import Sum, Avg, Count, Max, Min
from django.db.models.functions import TruncDay 

import xlwt

from api.models import *
import sys
import pandas as pd
from . import downtime

def summary_1_view(request):
    machine = Machine.objects.filter(user=request.user)
    machine_list = [] 
    for i in machine:
        machine_list.append(i.toDic()["machine_id"])
    shiftdate = request.GET.get('shiftdate')
    if shiftdate == None:
        shiftdate = str(timezone.localdate())
    #>----Souren/25/03/2021--------->
    machine_id = Machine.objects.get(user=request.user).machine_id
    try:
        rejectedPipeDic = rejectedPipeByQc.objects.get(machine_id=machine_id, shift_date=shiftdate).toDic()
        rejectedPipeDic["rejected_pipe_shift1"]= a = int(rejectedPipeDic["rejected_pipe_shift1"])
        rejectedPipeDic["rejected_pipe_shift2"] = b = int(rejectedPipeDic["rejected_pipe_shift2"])
        rejectedPipeDic["rejected_pipe_shift3"]= c = int(rejectedPipeDic["rejected_pipe_shift3"])
        rejectedPipeDic["total"] = a+b+c
    except:
        rejectedPipeDic = {}
        rejectedPipeDic["rejected_pipe_shift1"]= 0
        rejectedPipeDic["rejected_pipe_shift2"] = 0
        rejectedPipeDic["rejected_pipe_shift3"]= 0
        rejectedPipeDic["total"] = 0

    #>------------------------------------>
    try:
        PipeShiftDuration.objects.create(user = request.user, shift_date = shiftdate)  
    except:
        pass
    try:
        pipeshiftdic = PipeShiftDuration.objects.get(user = request.user, shift_date = shiftdate).toDic()
    except:
        pass
    machine_total_shift = Machine.objects.get(machine_id = machine_list[0]).machine_total_shift
    machine_shift1_start_time = Machine.objects.get(machine_id = machine_list[0]).shift1_start_time
    if machine_total_shift == 3:
        machine_shift1_time_duration = Machine.objects.get(machine_id = machine_list[0]).shift1_time_duration
        machine_shift2_time_duration = Machine.objects.get(machine_id = machine_list[0]).shift2_time_duration
        machine_shift3_time_duration = Machine.objects.get(machine_id = machine_list[0]).shift3_time_duration
        machine_total_shift_duration = int(machine_shift1_time_duration + machine_shift2_time_duration + machine_shift3_time_duration)
    elif machine_total_shift == 2:
        machine_shift1_time_duration = Machine.objects.get(machine_id = machine_list[0]).shift1_time_duration
        machine_shift2_time_duration = Machine.objects.get(machine_id = machine_list[0]).shift2_time_duration
        machine_total_shift_duration = int(machine_shift1_time_duration + machine_shift2_time_duration)

    shiftdatestart = datetime.datetime.strptime(shiftdate + " "+machine_shift1_start_time.strftime("%H:%M")+":00", "%Y-%m-%d %H:%M:%S")
    shiftdateend = shiftdatestart+timedelta(hours = machine_total_shift_duration)#datetime.datetime.strptime(shiftdate + ' 06:59:59', "%Y-%m-%d %H:%M:%S") + timedelta(days=1)
    # starttimestamp = int(shiftdatestart.timestamp())
    # endtimestamp = int(shiftdateend.timestamp())    
    starttimestamp = shiftdatestart#timezone.make_aware(shiftdatestart)
    endtimestamp = shiftdateend#timezone.make_aware(shiftdateend)    
    print(starttimestamp, endtimestamp)

    
    try:
        total_pipe = PipeDataProcessed.objects.filter(site_local_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list).count()
    except:
        total_pipe = None
    pipeshiftdic["total"] = pipeshiftdic["shift_1"] + pipeshiftdic["shift_2"] + pipeshiftdic["shift_3"]
    if machine_total_shift == 3:
        try:
            shift1_data = PipeDataProcessed.objects.filter(site_local_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='1')
            shift1_df = pd.DataFrame.from_records(shift1_data.values())
            shift1_downtime = downtime.calculate_downtime(shift1_df)
            s1_downtime=shift1_downtime
        except:
            shift1_downtime = 0
            s1_downtime=0
        try:
            shift2_data = PipeDataProcessed.objects.filter(site_local_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='2')
            shift2_df = pd.DataFrame.from_records(shift2_data.values())
            shift2_downtime = downtime.calculate_downtime(shift2_df)
            s2_downtime = shift2_downtime
        except:
            shift2_downtime = 0
            s2_downtime=0
        try:
            shift3_data = PipeDataProcessed.objects.filter(site_local_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='3')
            shift3_df = pd.DataFrame.from_records(shift3_data.values())
            shift3_downtime = downtime.calculate_downtime(shift3_df)
            s3_downtime=shift3_downtime
        except:
            shift3_downtime = 0
            s3_downtime = 0
        totaldowntime = shift1_downtime+shift2_downtime+shift3_downtime
        t_downtime = totaldowntime
    elif machine_total_shift == 2:
        try:
            shift1_data = PipeDataProcessed.objects.filter(site_local_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='1')
            shift1_df = pd.DataFrame.from_records(shift1_data.values())
            shift1_downtime = downtime.calculate_downtime(shift1_df)
            s1_downtime = shift1_downtime
        except:
            shift1_downtime = 0
            s1_downtime = 0
        try:
            shift2_data = PipeDataProcessed.objects.filter(site_local_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='2')
            shift2_df = pd.DataFrame.from_records(shift2_data.values())
            shift2_downtime = downtime.calculate_downtime(shift2_df)
            s2_downtime = shift2_downtime
        except:
            shift2_downtime = 0
            s2_downtime = 0
        shift3_downtime = 0
        s3_downtime = 0

        totaldowntime = shift1_downtime+shift2_downtime+shift3_downtime
        t_downtime = totaldowntime

    #pipeshiftdic["totaldowntime"] = pipeshiftdic["shift_1_downtime"] + pipeshiftdic["shift_2_downtime"] + pipeshiftdic["shift_3_downtime"]
    totalpipecount = {}
    try:
        if machine_total_shift == 3:
            totalpipecount["shift1"] = PipeDataProcessed.objects.filter(site_local_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='1').count()
            totalpipecount["shift2"] = PipeDataProcessed.objects.filter(site_local_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='2').count()
            totalpipecount["shift3"] = PipeDataProcessed.objects.filter(site_local_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='3').count()
            totalpipecount["total"] = totalpipecount["shift1"]+totalpipecount["shift2"]+totalpipecount["shift3"]
        elif machine_total_shift == 2:
            totalpipecount["shift1"] = PipeDataProcessed.objects.filter(site_local_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='1').count()
            totalpipecount["shift2"] = PipeDataProcessed.objects.filter(site_local_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='2').count()
            totalpipecount["total"] = totalpipecount["shift1"]+totalpipecount["shift2"]

        #totalpipecount["total"] = total_pipe
    except:
        totalpipecount = None
    passed = {}
    try:
        if machine_total_shift == 3:
            passed["shift1"] = PipeDataProcessed.objects.filter(site_local_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='1', pass_status='Passed').count() - rejectedPipeDic["rejected_pipe_shift1"]
            passed["shift2"] = PipeDataProcessed.objects.filter(site_local_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='2', pass_status='Passed').count() - rejectedPipeDic["rejected_pipe_shift2"]
            passed["shift3"] = PipeDataProcessed.objects.filter(site_local_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='3', pass_status='Passed').count() - rejectedPipeDic["rejected_pipe_shift3"]
            passed["total"] = passed["shift1"] + passed["shift2"] + passed["shift3"]
        elif machine_total_shift == 2:
            passed["shift1"] = PipeDataProcessed.objects.filter(site_local_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='1', pass_status='Passed').count() - rejectedPipeDic["rejected_pipe_shift1"]
            passed["shift2"] = PipeDataProcessed.objects.filter(site_local_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='2', pass_status='Passed').count() - rejectedPipeDic["rejected_pipe_shift2"]
            passed["total"] = passed["shift1"] + passed["shift2"]
        passed["unit"] = (passed["total"] / total_pipe) * 100
    except:
        passed = None
    overweight = {}
    try:
        if machine_total_shift == 3:
            overweight["shift1"] = PipeDataProcessed.objects.filter(site_local_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='1', pass_status='Overweight').count()
            overweight["shift2"] = PipeDataProcessed.objects.filter(site_local_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='2', pass_status='Overweight').count()
            overweight["shift3"] = PipeDataProcessed.objects.filter(site_local_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='3', pass_status='Overweight').count()
            overweight["total"] = overweight["shift1"] + overweight["shift2"] + overweight["shift3"]
        elif machine_total_shift == 2:
            overweight["shift1"] = PipeDataProcessed.objects.filter(site_local_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='1', pass_status='Overweight').count()
            overweight["shift2"] = PipeDataProcessed.objects.filter(site_local_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='2', pass_status='Overweight').count()
            overweight["total"] = overweight["shift1"] + overweight["shift2"]
        overweight["unit"] = (overweight["total"] / total_pipe) * 100
    except:
        overweight = None
    underweight = {}
    try:
        if machine_total_shift == 3:
            underweight["shift1"] = totalpipecount["shift1"] - passed["shift1"] - overweight["shift1"]
            underweight["shift2"] = totalpipecount["shift2"] - passed["shift2"] - overweight["shift2"]
            underweight["shift3"] = totalpipecount["shift3"] - passed["shift3"] - overweight["shift3"]
            underweight["total"] = underweight["shift1"] + underweight["shift2"] + underweight["shift3"]
        elif machine_total_shift == 2:
            underweight["shift1"] = totalpipecount["shift1"] - passed["shift1"] - overweight["shift1"]
            underweight["shift2"] = totalpipecount["shift2"] - passed["shift2"] - overweight["shift2"]
            underweight["total"] = underweight["shift1"] + underweight["shift2"]
        underweight["unit"] = (underweight["total"] / total_pipe) * 100
    except:
        underweight = None
    totalweight = {}
    try:
        if machine_total_shift == 3:
            totalweight["shift1"] = PipeDataProcessed.objects.filter(site_local_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='1').aggregate(Sum('weight'))['weight__sum']
            totalweight["shift1"] = 0 if totalweight["shift1"] == None else totalweight["shift1"] / 1000
            totalweight["shift2"] = PipeDataProcessed.objects.filter(site_local_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='2').aggregate(Sum('weight'))['weight__sum'] 
            totalweight["shift2"] = 0 if totalweight["shift2"] == None else totalweight["shift2"] / 1000
            totalweight["shift3"] = PipeDataProcessed.objects.filter(site_local_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='3').aggregate(Sum('weight'))['weight__sum'] 
            totalweight["shift3"] = 0 if totalweight["shift3"] == None else totalweight["shift3"] / 1000
            totalweight["total"] = totalweight["shift1"] + totalweight["shift2"] + totalweight["shift3"]
        elif machine_total_shift == 2:
            totalweight["shift1"] = PipeDataProcessed.objects.filter(site_local_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='1').aggregate(Sum('weight'))['weight__sum']
            totalweight["shift1"] = 0 if totalweight["shift1"] == None else totalweight["shift1"] / 1000
            totalweight["shift2"] = PipeDataProcessed.objects.filter(site_local_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='2').aggregate(Sum('weight'))['weight__sum'] 
            totalweight["shift2"] = 0 if totalweight["shift2"] == None else totalweight["shift2"] / 1000
            totalweight["total"] = totalweight["shift1"] + totalweight["shift2"]
    except Exception as exec:
        print(exec)
        totalweight = None
    weightperhour = {}
    try:
        if machine_total_shift == 3:
            weightperhour["shift1"] = totalweight["shift1"] / (machine_shift1_time_duration-s1_downtime)
            weightperhour["shift2"] = totalweight["shift2"] / (machine_shift2_time_duration-s2_downtime)
            weightperhour["shift3"] = totalweight["shift3"] / (machine_shift3_time_duration-s3_downtime)
            weightperhour["total"] = totalweight["total"]/ (machine_total_shift_duration-t_downtime)
        elif machine_total_shift == 2:
            weightperhour["shift1"] = totalweight["shift1"] / (machine_shift1_time_duration-s1_downtime)
            weightperhour["shift2"] = totalweight["shift2"] / (machine_shift2_time_duration-s2_downtime)
            weightperhour["total"] = totalweight["total"]/ (machine_total_shift_duration-t_downtime)

    except:
        weightperhour = None
    length = {}
    try:
        if machine_total_shift == 3:
            length["shift1"] = PipeDataProcessed.objects.filter(site_local_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='1').aggregate(Sum('length'))['length__sum']
            length["shift1"] = 0 if length["shift1"] == None else length["shift1"]
            length["shift2"] = PipeDataProcessed.objects.filter(site_local_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='2').aggregate(Sum('length'))['length__sum']
            length["shift2"] = 0 if length["shift2"] == None else length["shift2"]
            length["shift3"] = PipeDataProcessed.objects.filter(site_local_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='3').aggregate(Sum('length'))['length__sum']
            length["shift3"] = 0 if length["shift3"] == None else length["shift3"]
            length["total"] = length["shift1"] + length["shift2"] + length["shift3"]
        elif machine_total_shift ==2:
            length["shift1"] = PipeDataProcessed.objects.filter(site_local_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='1').aggregate(Sum('length'))['length__sum']
            length["shift1"] = 0 if length["shift1"] == None else length["shift1"]
            length["shift2"] = PipeDataProcessed.objects.filter(site_local_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='2').aggregate(Sum('length'))['length__sum']
            length["shift2"] = 0 if length["shift2"] == None else length["shift2"]
            length["total"] = length["shift1"] + length["shift2"]

    except:
        length = None
    weightgain = {}
    max_pipe=[]
    min_pipe=[]
    shift1_query = PipeDataProcessed.objects.filter(site_local_time__range=(starttimestamp, endtimestamp), machine_id__in=machine_list, shift='1')
    shift2_query = PipeDataProcessed.objects.filter(site_local_time__range=(starttimestamp, endtimestamp), machine_id__in=machine_list, shift='2')
    shift3_query = PipeDataProcessed.objects.filter(site_local_time__range=(starttimestamp, endtimestamp), machine_id__in=machine_list, shift='3')
    if machine_total_shift == 3:
        
        weightgain["shift1"] = shift1_query.aggregate(Sum('weightgain'))['weightgain__sum'] 
        weightgain["shift1"] = 0 if weightgain["shift1"] == None else weightgain["shift1"] / 1000
        weightgain["shift2"] = shift2_query.aggregate(Sum('weightgain'))['weightgain__sum']
        weightgain["shift2"] = 0 if weightgain["shift2"] == None else weightgain["shift2"] / 1000
        weightgain["shift3"] = shift3_query.aggregate(Sum('weightgain'))['weightgain__sum']
        weightgain["shift3"] = 0 if weightgain["shift3"] == None else weightgain["shift3"] / 1000
        weightgain["total"] = weightgain["shift1"] + weightgain["shift2"] + weightgain["shift3"]
        shift1_max=shift1_query.aggregate(Max('weight'))
        shift2_max=shift2_query.aggregate(Max('weight'))
        shift3_max=shift3_query.aggregate(Max('weight'))
        shift1_min=shift1_query.aggregate(Min('weight'))
        shift2_min=shift2_query.aggregate(Min('weight'))
        shift3_min=shift3_query.aggregate(Min('weight'))
        max_pipe.extend([shift1_max, shift2_max, shift3_max])
        min_pipe.extend([shift1_min, shift2_min, shift3_min])
    elif machine_total_shift == 2:
        shift1_query = PipeDataProcessed.objects.filter(site_local_time__range=(starttimestamp, endtimestamp), machine_id__in=machine_list, shift='1')
        shift2_query = PipeDataProcessed.objects.filter(site_local_time__range=(starttimestamp, endtimestamp), machine_id__in=machine_list, shift='2')
        weightgain["shift1"] = shift1_query.aggregate(Sum('weightgain'))['weightgain__sum'] 
        weightgain["shift1"] = 0 if weightgain["shift1"] == None else weightgain["shift1"] / 1000
        weightgain["shift2"] = shift2_query.aggregate(Sum('weightgain'))['weightgain__sum']
        weightgain["shift2"] = 0 if weightgain["shift2"] == None else weightgain["shift2"] / 1000
        weightgain["total"] = weightgain["shift1"] + weightgain["shift2"]
        shift1_max=shift1_query.aggregate(Max('weight'))
        shift2_max=shift2_query.aggregate(Max('weight'))
        shift1_min=shift1_query.aggregate(Min('weight'))
        shift2_min=shift2_query.aggregate(Min('weight'))
        max_pipe.extend([shift1_max, shift2_max])
        min_pipe.extend([shift1_min, shift2_min])
    weightloss = {}
    weightloss_underWeight={}
    weightloss_pass = {}
    try:
        if machine_total_shift == 3:
            weightloss["shift1"] = shift1_query.aggregate(Sum('weightloss'))['weightloss__sum']
            weightloss["shift1"] = 0 if weightloss["shift1"] == None else weightloss["shift1"] / 1000
            weightloss["shift2"] = shift2_query.aggregate(Sum('weightloss'))['weightloss__sum']
            weightloss["shift2"] = 0 if weightloss["shift2"] == None else weightloss["shift2"] / 1000
            weightloss["shift3"] = shift3_query.aggregate(Sum('weightloss'))['weightloss__sum']
            weightloss["shift3"] = 0 if weightloss["shift3"] == None else weightloss["shift3"] / 1000
            weightloss["total"] = weightloss["shift1"] + weightloss["shift2"] + weightloss["shift3"]
            weightloss_underWeight["shift1"] = shift1_query.filter(pass_status="Underweight").aggregate(Sum('weightloss'))['weightloss__sum']
            weightloss_underWeight["shift1"] = 0 if weightloss_underWeight["shift1"] == None else weightloss_underWeight["shift1"] / 1000
            weightloss_underWeight["shift2"] = shift2_query.filter(pass_status="Underweight").aggregate(Sum('weightloss'))['weightloss__sum']
            weightloss_underWeight["shift2"] = 0 if weightloss_underWeight["shift2"] == None else weightloss_underWeight["shift2"] / 1000
            weightloss_underWeight["shift3"] = shift3_query.filter(pass_status="Underweight").aggregate(Sum('weightloss'))['weightloss__sum']
            weightloss_underWeight["shift3"] = 0 if weightloss_underWeight["shift3"] == None else weightloss_underWeight["shift3"] / 1000
            weightloss_underWeight["total"] = weightloss_underWeight["shift1"]+weightloss_underWeight["shift2"]+weightloss_underWeight["shift3"]
            weightloss_pass["shift1"] = shift1_query.filter(pass_status="Passed").aggregate(Sum('weightloss'))['weightloss__sum']
            weightloss_pass["shift1"] = 0 if weightloss_pass["shift1"] == None else weightloss_pass["shift1"] / 1000
            weightloss_pass["shift2"] = shift2_query.filter(pass_status="Passed").aggregate(Sum('weightloss'))['weightloss__sum']
            weightloss_pass["shift2"] = 0 if weightloss_pass["shift2"] == None else weightloss_pass["shift2"] / 1000
            weightloss_pass["shift3"] = shift3_query.filter(pass_status="Passed").aggregate(Sum('weightloss'))['weightloss__sum']
            weightloss_pass["shift3"] = 0 if weightloss_pass["shift3"] == None else weightloss_pass["shift3"] / 1000
            weightloss_pass["total"] = weightloss_pass["shift1"]+weightloss_pass["shift2"]+weightloss_pass["shift3"] 
        elif machine_total_shift == 2:
            weightloss["shift1"] = shift1_query.aggregate(Sum('weightloss'))['weightloss__sum']
            weightloss["shift1"] = 0 if weightloss["shift1"] == None else weightloss["shift1"] / 1000
            weightloss["shift2"] = shift2_query.aggregate(Sum('weightloss'))['weightloss__sum']
            weightloss["shift2"] = 0 if weightloss["shift2"] == None else weightloss["shift2"] / 1000
            weightloss["total"] = weightloss["shift1"] + weightloss["shift2"]
            weightloss_underWeight["shift1"] = shift1_query.filter(pass_status="Underweight").aggregate(Sum('weightloss'))['weightloss__sum']
            weightloss_underWeight["shift1"] = 0 if weightloss_underWeight["shift1"] == None else weightloss_underWeight["shift1"] / 1000
            weightloss_underWeight["shift2"] = shift2_query.filter(pass_status="Underweight").aggregate(Sum('weightloss'))['weightloss__sum']
            weightloss_underWeight["shift2"] = 0 if weightloss_underWeight["shift2"] == None else weightloss_underWeight["shift2"] / 1000
            weightloss_underWeight["total"] = weightloss_underWeight["shift1"]+weightloss_underWeight["shift2"]
            weightloss_pass["shift1"] = shift1_query.filter(pass_status="Passed").aggregate(Sum('weightloss'))['weightloss__sum']
            weightloss_pass["shift1"] = 0 if weightloss_pass["shift1"] == None else weightloss_pass["shift1"] / 1000
            weightloss_pass["shift2"] = shift2_query.filter(pass_status="Passed").aggregate(Sum('weightloss'))['weightloss__sum']
            weightloss_pass["shift2"] = 0 if weightloss_pass["shift2"] == None else weightloss_pass["shift2"] / 1000
            weightloss_pass["total"] = weightloss_pass["shift1"]+weightloss_pass["shift2"] 

    except:
        if machine_total_shift == 3:
            weightloss['shift1'] = 0
            weightloss['shift2'] = 0
            weightloss['shift3'] = 0
            weightloss['total'] = 0
        elif machine_total_shift == 2:
            weightloss['shift1'] = 0
            weightloss['shift2'] = 0
            weightloss['total'] = 0
    try:
        if machine_total_shift == 3:
            netgain = {
            "shift1": weightgain["shift1"] + weightloss["shift1"],
            "shift2": weightgain["shift2"] + weightloss["shift2"],
            "shift3": weightgain["shift3"] + weightloss["shift3"],
            "total": weightgain["total"] + weightloss["total"],
            "percent_shift1": ((weightgain["shift1"]+weightloss["shift1"])/(totalweight["shift1"]+0.000000001))*100,
            "percent_shift2": ((weightgain["shift2"]+weightloss["shift2"])/(totalweight["shift2"]+0.000000001))*100,
            "percent_shift3": ((weightgain["shift3"]+weightloss["shift3"])/(totalweight["shift3"]+0.000000001))*100,
            "percent_total": ((weightgain["total"]+weightloss["total"])/(totalweight["total"]+0.000000001))*100,
            }
        elif machine_total_shift == 2:
            netgain = {
            "shift1": weightgain["shift1"] + weightloss["shift1"],
            "shift2": weightgain["shift2"] + weightloss["shift2"],
            "total": weightgain["total"] + weightloss["total"],
            "percent_shift1": (((weightgain["shift1"])+(weightloss["shift1"]))/(totalweight["shift1"]+0.000000001))*100,
            "percent_shift2": (((weightgain["shift2"])+(weightloss["shift2"]))/(totalweight["shift2"]+0.000000001))*100,
            "percent_total": (((weightgain["total"])+(weightloss["total"]))/(totalweight["total"]+0.000000001))*100
            }
    except:
        netgain = None
    try:
        if machine_total_shift == 3:
            weightlength = {
                "shift1": 0 if totalweight["shift1"] == None or length["shift1"] == 0 or length["shift1"] == None else totalweight["shift1"] / totalpipecount["shift1"],#length["shift1"],
                "shift2": 0 if totalweight["shift2"] == None or length["shift2"] == 0 or length["shift2"] == None else totalweight["shift2"] / totalpipecount["shift2"],#length["shift2"],
                "shift3": 0 if totalweight["shift3"] == None or length["shift3"] == 0 or length["shift3"] == None else totalweight["shift3"] / totalpipecount["shift3"],#length["shift3"],
                "total": 0 if totalweight["total"] == None or length["total"] == 0 or length["total"] == None else totalweight["total"] / totalpipecount['total']
            }
        elif machine_total_shift == 2:
            weightlength = {
                "shift1": 0 if totalweight["shift1"] == None or length["shift1"] == 0 or length["shift1"] == None else totalweight["shift1"] / totalpipecount["shift1"],#length["shift1"],
                "shift2": 0 if totalweight["shift2"] == None or length["shift2"] == 0 or length["shift2"] == None else totalweight["shift2"] / totalpipecount["shift2"],#length["shift2"],
                "total": 0 if totalweight["total"] == None or length["total"] == 0 or length["total"] == None else totalweight["total"] / totalpipecount['total']
            }
    except:
        weightlength = None
    try:
        if machine_total_shift == 3:
            shiftinputvalue = {
                "shift1": '0' + str(pipeshiftdic["shift_1"]),
                "shift2": '0' + str(pipeshiftdic["shift_2"]),
                "shift3": '0' + str(pipeshiftdic["shift_3"]) 
                }
        elif machine_total_shift ==2:
            shiftinputvalue = {
                "shift1": '0' + str(pipeshiftdic["shift_1"]),
                "shift2": '0' + str(pipeshiftdic["shift_2"]) 
                }
    except:
        shiftinputvalue = None
    try:
        for key, val in pipeshiftdic.items():
            try:
                pipeshiftdic[key] = val.total_seconds() / 3600
            except:
                pass
    except:
        pipeshiftdic = None
    #souren----
    allpipe = PipeDataProcessed.objects.filter(site_local_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list)
    all_max_pipe = allpipe.aggregate(Max('weight'))
    all_min_pipe = allpipe.aggregate(Min('weight'))
    max_pipe.append(all_max_pipe)
    min_pipe.append(all_min_pipe)
    totaldowntime = time.strftime('%H:%M', time.gmtime(totaldowntime*3600))
    shift1_downtime = time.strftime('%H:%M', time.gmtime(shift1_downtime*3600))
    shift2_downtime = time.strftime('%H:%M', time.gmtime(shift2_downtime*3600))
    shift3_downtime = time.strftime('%H:%M', time.gmtime(shift3_downtime*3600))
    rejectedPipeDic["unit"] = (rejectedPipeDic['total']/(total_pipe+0.000000001))*100
    summary_1_dic = {"machine": machine, "summary_name": "MIS 2 : DAILY PRODUCTION REPORT", "shiftdate": shiftdate,"shiftinputvalue":shiftinputvalue, "shiftdatestart": shiftdatestart, "shiftdateend": shiftdateend, "pipeshiftdic": pipeshiftdic, "totalpipecount": totalpipecount, "passed": passed, "overweight": overweight, "underweight": underweight, "totalweight": totalweight, "weightperhour": weightperhour, "length": length, "weightgain": weightgain, "weightloss": weightloss, "netgain": netgain, "weightlength": weightlength,'mshift':machine_total_shift,'shift1_downtime':shift1_downtime, 'shift2_downtime':shift2_downtime, 'shift3_downtime':shift3_downtime, 'totaldowntime':totaldowntime, 'rejectedPipeDic': rejectedPipeDic, 'weightloss_underWeight': weightloss_underWeight, 'weightloss_pass': weightloss_pass, 'max_pipe': max_pipe, 'min_pipe': min_pipe}
    # print(summary_1_dic)
    return 'summary_1.html', summary_1_dic
