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
import sys

def summary_1_view(request):
    machine = Machine.objects.filter(user=request.user)
    machine_list = [] 
    for i in machine:
        machine_list.append(i.toDic()["machine_id"])
    shiftdate = request.GET.get('shiftdate') 
    if shiftdate == None:
        shiftdate = str(timezone.localdate())
    print(shiftdate)
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
    starttimestamp = timezone.make_aware(shiftdatestart)
    endtimestamp = timezone.make_aware(shiftdateend)    
    print(starttimestamp, endtimestamp)

    
    try:
        total_pipe = PipeDataProcessed.objects.filter(site_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list).count()
    except:
        total_pipe = None
    if machine_total_shift == 3:
        pipeshiftdic["total"] = pipeshiftdic["shift_1"] + pipeshiftdic["shift_2"] + pipeshiftdic["shift_3"]
        pipeshiftdic["totaldowntime"] = pipeshiftdic["shift_1_downtime"] + pipeshiftdic["shift_2_downtime"] + pipeshiftdic["shift_3_downtime"]
    elif machine_total_shift == 2:
        pipeshiftdic["total"] = pipeshiftdic["shift_1"] + pipeshiftdic["shift_2"]
        pipeshiftdic["totaldowntime"] = pipeshiftdic["shift_1_downtime"] + pipeshiftdic["shift_2_downtime"]
    totalpipecount = {}
    try:
        if machine_total_shift == 3:
            totalpipecount["shift1"] = PipeDataProcessed.objects.filter(site_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='1').count()
            totalpipecount["shift2"] = PipeDataProcessed.objects.filter(site_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='2').count()
            totalpipecount["shift3"] = PipeDataProcessed.objects.filter(site_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='3').count()
            totalpipecount["total"] = totalpipecount["shift1"]+totalpipecount["shift2"]+totalpipecount["shift3"]
        elif machine_total_shift == 2:
            totalpipecount["shift1"] = PipeDataProcessed.objects.filter(site_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='1').count()
            totalpipecount["shift2"] = PipeDataProcessed.objects.filter(site_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='2').count()
            totalpipecount["total"] = totalpipecount["shift1"]+totalpipecount["shift2"]

        #totalpipecount["total"] = total_pipe
    except:
        totalpipecount = None
    passed = {}
    try:
        if machine_total_shift == 3:
            passed["shift1"] = PipeDataProcessed.objects.filter(site_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='1', pass_status='Passed').count()
            passed["shift2"] = PipeDataProcessed.objects.filter(site_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='2', pass_status='Passed').count()
            passed["shift3"] = PipeDataProcessed.objects.filter(site_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='3', pass_status='Passed').count()
            passed["total"] = passed["shift1"] + passed["shift2"] + passed["shift3"]
        elif machine_total_shift == 2:
            passed["shift1"] = PipeDataProcessed.objects.filter(site_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='1', pass_status='Passed').count()
            passed["shift2"] = PipeDataProcessed.objects.filter(site_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='2', pass_status='Passed').count()
            passed["total"] = passed["shift1"] + passed["shift2"]
        passed["unit"] = (passed["total"] / total_pipe) * 100
    except:
        passed = None
    overweight = {}
    try:
        if machine_total_shift == 3:
            overweight["shift1"] = PipeDataProcessed.objects.filter(site_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='1', pass_status='Overweight').count()
            overweight["shift2"] = PipeDataProcessed.objects.filter(site_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='2', pass_status='Overweight').count()
            overweight["shift3"] = PipeDataProcessed.objects.filter(site_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='3', pass_status='Overweight').count()
            overweight["total"] = overweight["shift1"] + overweight["shift2"] + overweight["shift3"]
        elif machine_total_shift == 2:
            overweight["shift1"] = PipeDataProcessed.objects.filter(site_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='1', pass_status='Overweight').count()
            overweight["shift2"] = PipeDataProcessed.objects.filter(site_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='2', pass_status='Overweight').count()
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
            totalweight["shift1"] = PipeDataProcessed.objects.filter(site_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='1').aggregate(Sum('weight'))['weight__sum']
            totalweight["shift1"] = 0 if totalweight["shift1"] == None else totalweight["shift1"] / 1000
            totalweight["shift2"] = PipeDataProcessed.objects.filter(site_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='2').aggregate(Sum('weight'))['weight__sum'] 
            totalweight["shift2"] = 0 if totalweight["shift2"] == None else totalweight["shift2"] / 1000
            totalweight["shift3"] = PipeDataProcessed.objects.filter(site_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='3').aggregate(Sum('weight'))['weight__sum'] 
            totalweight["shift3"] = 0 if totalweight["shift3"] == None else totalweight["shift3"] / 1000
            totalweight["total"] = totalweight["shift1"] + totalweight["shift2"] + totalweight["shift3"]
        elif machine_total_shift == 2:
            totalweight["shift1"] = PipeDataProcessed.objects.filter(site_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='1').aggregate(Sum('weight'))['weight__sum']
            totalweight["shift1"] = 0 if totalweight["shift1"] == None else totalweight["shift1"] / 1000
            totalweight["shift2"] = PipeDataProcessed.objects.filter(site_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='2').aggregate(Sum('weight'))['weight__sum'] 
            totalweight["shift2"] = 0 if totalweight["shift2"] == None else totalweight["shift2"] / 1000
            totalweight["total"] = totalweight["shift1"] + totalweight["shift2"]
    except Exception as exec:
        print(exec)
        totalweight = None
    weightperhour = {}
    try:
        if machine_total_shift == 3:
            weightperhour["shift1"] = totalweight["shift1"] / 8#(pipeshiftdic["shift_1"].total_seconds() / 3600)
            weightperhour["shift2"] = totalweight["shift2"] / 8#(pipeshiftdic["shift_2"].total_seconds() / 3600)
            weightperhour["shift3"] = totalweight["shift3"] / 8#(pipeshiftdic["shift_3"].total_seconds() / 3600)
            weightperhour["total"] = totalweight["total"]/ 24#(pipeshiftdic["total"].total_seconds() / 3600)
        elif machine_total_shift == 2:
            weightperhour["shift1"] = totalweight["shift1"] / 12#(pipeshiftdic["shift_1"].total_seconds() / 3600)
            weightperhour["shift2"] = totalweight["shift2"] / 12#(pipeshiftdic["shift_2"].total_seconds() / 3600)
            weightperhour["total"] = totalweight["total"]/ 24#(pipeshiftdic["total"].total_seconds() / 3600)

    except:
        weightperhour = None
    length = {}
    try:
        if machine_total_shift == 3:
            length["shift1"] = PipeDataProcessed.objects.filter(site_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='1').aggregate(Sum('length'))['length__sum']
            length["shift1"] = 0 if length["shift1"] == None else length["shift1"]
            length["shift2"] = PipeDataProcessed.objects.filter(site_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='2').aggregate(Sum('length'))['length__sum']
            length["shift2"] = 0 if length["shift2"] == None else length["shift2"]
            length["shift3"] = PipeDataProcessed.objects.filter(site_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='3').aggregate(Sum('length'))['length__sum']
            length["shift3"] = 0 if length["shift3"] == None else length["shift3"]
            length["total"] = length["shift1"] + length["shift2"] + length["shift3"]
        elif machine_total_shift ==2:
            length["shift1"] = PipeDataProcessed.objects.filter(site_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='1').aggregate(Sum('length'))['length__sum']
            length["shift1"] = 0 if length["shift1"] == None else length["shift1"]
            length["shift2"] = PipeDataProcessed.objects.filter(site_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='2').aggregate(Sum('length'))['length__sum']
            length["shift2"] = 0 if length["shift2"] == None else length["shift2"]
            length["total"] = length["shift1"] + length["shift2"]

    except:
        length = None
    weightgain = {}
    try:
        if machine_total_shift == 3:
            weightgain["shift1"] = PipeDataProcessed.objects.filter(site_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='1').aggregate(Sum('weightgain'))['weightgain__sum'] 
            weightgain["shift1"] = 0 if weightgain["shift1"] == None else weightgain["shift1"] / 1000
            weightgain["shift2"] = PipeDataProcessed.objects.filter(site_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='2').aggregate(Sum('weightgain'))['weightgain__sum']
            weightgain["shift2"] = 0 if weightgain["shift2"] == None else weightgain["shift2"] / 1000
            weightgain["shift3"] = PipeDataProcessed.objects.filter(site_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='3').aggregate(Sum('weightgain'))['weightgain__sum']
            weightgain["shift3"] = 0 if weightgain["shift3"] == None else weightgain["shift3"] / 1000
            weightgain["total"] = weightgain["shift1"] + weightgain["shift2"] + weightgain["shift3"]
        elif machine_total_shift == 2:
            weightgain["shift1"] = PipeDataProcessed.objects.filter(site_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='1').aggregate(Sum('weightgain'))['weightgain__sum'] 
            weightgain["shift1"] = 0 if weightgain["shift1"] == None else weightgain["shift1"] / 1000
            weightgain["shift2"] = PipeDataProcessed.objects.filter(site_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='2').aggregate(Sum('weightgain'))['weightgain__sum']
            weightgain["shift2"] = 0 if weightgain["shift2"] == None else weightgain["shift2"] / 1000
            weightgain["total"] = weightgain["shift1"] + weightgain["shift2"]

    except:
        weightgain = None
    weightloss = {}
    try:
        if machine_total_shift == 3:
            weightloss["shift1"] = PipeDataProcessed.objects.filter(site_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='1').aggregate(Sum('weightloss'))['weightloss__sum']
            weightloss["shift1"] = 0 if weightloss["shift1"] == None else weightloss["shift1"] / 1000
            weightloss["shift2"] = PipeDataProcessed.objects.filter(site_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='2').aggregate(Sum('weightloss'))['weightloss__sum']
            weightloss["shift2"] = 0 if weightloss["shift2"] == None else weightloss["shift2"] / 1000
            weightloss["shift3"] = PipeDataProcessed.objects.filter(site_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='3').aggregate(Sum('weightloss'))['weightloss__sum']
            weightloss["shift3"] = 0 if weightloss["shift3"] == None else weightloss["shift3"] / 1000
            weightloss["total"] = weightloss["shift1"] + weightloss["shift2"] + weightloss["shift3"]
        elif machine_total_shift == 2:
            weightloss["shift1"] = PipeDataProcessed.objects.filter(site_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='1').aggregate(Sum('weightloss'))['weightloss__sum']
            weightloss["shift1"] = 0 if weightloss["shift1"] == None else weightloss["shift1"] / 1000
            weightloss["shift2"] = PipeDataProcessed.objects.filter(site_time__range=(starttimestamp, endtimestamp), machine_id__in = machine_list, shift='2').aggregate(Sum('weightloss'))['weightloss__sum']
            weightloss["shift2"] = 0 if weightloss["shift2"] == None else weightloss["shift2"] / 1000
            weightloss["total"] = weightloss["shift1"] + weightloss["shift2"]

    except:
        weightloss = None
    try:
        if machine_total_shift == 3:
            netgain = {
            "shift1": weightgain["shift1"] + weightloss["shift1"],
            "shift2": weightgain["shift2"] + weightloss["shift2"],
            "shift3": weightgain["shift3"] + weightloss["shift3"],
            "total": weightgain["total"] + weightloss["total"]
            }
        elif machine_total_shift == 2:
            netgain = {
            "shift1": weightgain["shift1"] + weightloss["shift1"],
            "shift2": weightgain["shift2"] + weightloss["shift2"],
            "total": weightgain["total"] + weightloss["total"]
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
    summary_1_dic = {"machine": machine, "summary_name": "MIS 1 : DAILY PRODUCTION REPORT", "shiftdate": shiftdate,"shiftinputvalue":shiftinputvalue, "shiftdatestart": shiftdatestart, "shiftdateend": shiftdateend, "pipeshiftdic": pipeshiftdic, "totalpipecount": totalpipecount, "passed": passed, "overweight": overweight, "underweight": underweight, "totalweight": totalweight, "weightperhour": weightperhour, "length": length, "weightgain": weightgain, "weightloss": weightloss, "netgain": netgain, "weightlength": weightlength,'mshift':machine_total_shift}
    # print(summary_1_dic)
    return 'summary_1.html', summary_1_dic
