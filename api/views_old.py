from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.utils import timezone
from django.db.models import Q
from django.conf import settings

import re
import json
import datetime
import pytz

from .models import *
from .models import Machine


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
    shift = ''

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
        try:
            if ts.isdigit():
                tsdatetime = datetime.datetime.fromtimestamp(
                    int(ts), tz=pytz.timezone(settings.TIME_ZONE))
                site_time = timezone.localtime(timezone.now())
                try:
                    MachineStatus.objects.create(machine_id=Machine.objects.get(machine_id=mid), active_date_time=site_time)
                except:
                    MachineStatus.objects.filter(machine_id=Machine.objects.get(machine_id=mid)).update(active_date_time=site_time)
                if(ts != "999"):
                    site_time = tsdatetime

                machine_shift = Machine.objects.get(machine_id = mid)
                shift1_time = (machine_shift.shift1_start_time,machine_shift.shift1_end_time)
                shift2_time = (machine_shift.shift2_start_time,machine_shift.shift2_end_time)
                shift3_time = (machine_shift.shift3_start_time,machine_shift.shift3_end_time)

                shiftstart1 = site_time.replace(
                    hour=shift1_time(0).hour, minute=shift1_time(0).minute, second=shift1_time(0).second, microsecond=0)
                shiftend1 = site_time.replace(
                    hour=shift1_time(1).hour, minute=shift1_time(1).minute, second=shift1_time(1).second, microsecond=0)
                shiftstart2 = site_time.replace(
                    hour=shift2_time(0).hour, minute=shift2_time(0).minute, second=shift2_time(0).second, microsecond=0)
                shiftend2 = site_time.replace(
                    hour=shift2_time(1).hour, minute=shift2_time(1).minute, second=shift2_time(1).second, microsecond=0)

                if shiftstart1 <= site_time and site_time <= shiftend1:
                    shift = "1"
                elif shiftstart2 <= site_time and site_time <= shiftend2:
                    shift = "2"
                print("shift3_time",shift3_time)
                if shift3_time is not None:
                    shiftstart3 = site_time.replace(
                    hour=shift3_time(0).hour, minute=shift3_time(0).minute, second=shift3_time(0).second, microsecond=0)
                    shiftend3 = site_time.replace(
                    hour=shift3_time(1).hour, minute=shift3_time(1).minute, second=shift3_time(1).second, microsecond=0)
                    if shiftstart3 <= site_time and site_time <= shiftend3:
                        shift = "3"

                """if shiftstart1 <= site_time and site_time <= shiftend1:
                    shift = "1"
                elif shiftstart2 <= site_time and site_time <= shiftend2:
                    shift = "2"
                elif shiftstart3 <= site_time and site_time <= shiftend3:
                    shift = "3"""
                
                """shiftstart1 = site_time.replace(
                    hour=7, minute=0, second=0, microsecond=0)
                shiftend1 = site_time.replace(
                    hour=14, minute=59, second=59, microsecond=0)
                shiftstart2 = site_time.replace(
                    hour=15, minute=0, second=0, microsecond=0)
                shiftend2 = site_time.replace(
                    hour=22, minute=59, second=59, microsecond=0)
                if shiftstart1 <= site_time and site_time <= shiftend1:
                    shift = "1"
                elif shiftstart2 <= site_time and site_time <= shiftend2:
                    shift = "2"
                else:
                    shift = "3"""
        except :
            pass

    if ts != '999':
        try:
            if len(c) == 2:
                outer_diameter_code = c[0]
                pipe_length_code = c[1]
            elif len(c) == 4:
                outer_diameter_code = c[0] + c[1]
                pipe_length_code = c[2] + c[3]
            elif len(c) == 3:
                if int(c[0] + c[1]) > 19:
                    outer_diameter_code = c[0]
                    pipe_length_code = c[1] + c[2]
                else:
                    outer_diameter_code = c[0] + c[1]
                    pipe_length_code = c[2]
            else:
                outer_diameter_code = None
                pipe_length_code = None
        except:
            outer_diameter_code = None
            pipe_length_code = None
        try:
            bms = BasicMetarialStandard.objects.filter(code=b[0])[0]
            basic_metarial = bms.toDic().get("basic_metarial")
        except:
            bms = None
            basic_metarial = None
        try:
            stc = StandardTypeClassification.objects.filter(
                basic_metarial=bms, code=b[1])[0]
            standard_type_classification = stc.toDic().get("standard_type_classification")
        except:
            stc = None
            standard_type_classification = None
        try:
            if(len(b) == 4):
                pts_code = b[2] + b[3]
            else:
                pts_code = b[2]
            pts = PressureTypeSpecification.objects.filter(
                basic_metarial=bms, standard_type_classification=stc, code=pts_code)[0]
            pressure_type_specification = pts.toDic().get("pressure_type_specification")
        except:
            pts = None
            pressure_type_specification = None
        try:
            pod = PipeOuterDiameter.objects.filter(
                standard_type_classification=stc, code=outer_diameter_code)[0]
            pod_dic = pod.toDic()
            outer_diameter_unit=str(pod_dic.get("unit"))
            outer_diameter = float(pod_dic.get("outer_diameter"))
        except:
            pod = None
            outer_diameter = None
            outer_diameter_unit = None
        try:
            pl = PipeLength.objects.filter(
                standard_type_classification=stc, code=pipe_length_code)[0]
            pl_dic = pl.toDic()
            length = float(pl_dic.get("length"))
            length_unit = str(pl_dic.get("unit"))
        except:
            print(e)
            pl = None
            length = None
            length_unit = None
        try:
            if int(d) - int(weight) < 0:
                weightloss = int(d) - int(weight)
                weightgain = 0
            else:
                weightgain = int(d) - int(weight)
                weightloss = 0
            if ps == '0':
                pass_status = 'Underweight'
            elif ps == '1':
                pass_status = 'Overweight'
            elif ps == '2':
                pass_status = 'Passed'
            PipeDataProcessed.objects.create(machine_id=mid, basic_metarial=basic_metarial, standard_type_classification=standard_type_classification, pressure_type_specification=pressure_type_specification, outer_diameter=outer_diameter, outer_diameter_unit=outer_diameter_unit, length = length, length_unit = length_unit, timestamp = int(ts), count = int(count), weight = int(weight), maxweight = int(d), minweight = int(e), weightgain = weightgain, weightloss = weightloss, pass_status = pass_status, site_time = site_time, shift = shift)
        except Exception as excep:
            print(excep)
    try:
        site_time = site_time.isoformat()
    except:
        pass
    try:
        PipeData.objects.create(mid=mid, b=b, c=c, d=d, e=e, ts=ts, count=count,
                                weight=weight, ps=ps, site_time=site_time, shift=shift)
    except:
        print("PipeData.objects.create ERROR")
    return HttpResponse(status=200)






def get_synced_data(request):
    mid = request.GET.get('a', None)
    b = request.GET.get('b', None)
    c = request.GET.get('c', None)
    d = request.GET.get('d', None)
    e = request.GET.get('e', None)
    ts = request.GET.get('ts', None)
    count = request.GET.get('count', None)
    weight = request.GET.get('weight', None)
    ps = request.GET.get('ps', None)
    site_time = request.GET.get('site_time', None)
    shift = request.GET.get('shift', None)
    if mid != None and b != None and c != None and d != None and e != None and ts != None and count != None and weight != None and ps != None and site_time != None and shift != None:
        try:
            MachineStatus.objects.create(machine_id=Machine.objects.get(machine_id=mid), active_date_time=timezone.now())
        except:
            MachineStatus.objects.filter(machine_id=Machine.objects.get(machine_id=mid)).update(active_date_time=timezone.now())
        if len(c) == 2:
            outer_diameter_code = c[0]
            pipe_length_code = c[1]
        elif len(c) == 4:
            outer_diameter_code = c[0] + c[1]
            pipe_length_code = c[2] + c[3]
        elif len(c) == 3:
            if int(c[0] + c[1]) > 19:
                outer_diameter_code = c[0]
                pipe_length_code = c[1] + c[2]
            else:
                outer_diameter_code = c[0] + c[1]
                pipe_length_code = c[2]
        else:
            outer_diameter_code = None
            pipe_length_code = None
        try:
            bms = BasicMetarialStandard.objects.get(code=b[0])
            basic_metarial = bms.basic_metarial
        except:
            bms = None
            basic_metarial = None
        try:
            stc = StandardTypeClassification.objects.get(
                basic_metarial=bms, code=b[1])
            standard_type_classification = stc.standard_type_classification
        except:
            stc = None
            standard_type_classification = None
        try:
            if(len(b) == 4):
                pts_code = b[2] + b[3]
            else:
                pts_code = b[2]
            pts = PressureTypeSpecification.objects.get(
                basic_metarial=bms, standard_type_classification=stc, code=pts_code)
            pressure_type_specification = pts.pressure_type_specification
        except:
            pts = None
            pressure_type_specification = None
        try:
            pod = PipeOuterDiameter.objects.get(
                standard_type_classification=stc, code=outer_diameter_code)
            outer_diameter_unit=pod.unit.unit
            outer_diameter = float(pod.outer_diameter)
        except:
            pod = None
            outer_diameter = None
            outer_diameter_unit = None
        try:
            pl = PipeLength.objects.get(
                standard_type_classification=stc, code=pipe_length_code)
            length = float(pl.length)
            length_unit = str(pl.unit.unit)
        except:
            pl = None
            length = None
            length_unit = None
        if int(d) - int(weight) < 0:
            weightloss = int(d) - int(weight)
            weightgain = 0
        else:
            weightgain = int(d) - int(weight)
            weightloss = 0
        if ps == '0':
            pass_status = 'Underweight'
        elif ps == '1':
            pass_status = 'Overweight'
        elif ps == '2':
            pass_status = 'Passed'
        try:
            PipeDataProcessed.objects.create(
                machine_id=mid, 
                basic_metarial=basic_metarial, 
                standard_type_classification=standard_type_classification, 
                pressure_type_specification=pressure_type_specification, 
                outer_diameter=outer_diameter, 
                outer_diameter_unit=outer_diameter_unit, 
                length=length, 
                length_unit=length_unit, 
                timestamp=int(ts), 
                count=int(count), 
                weight=int(weight), 
                maxweight=int(d), 
                minweight=int(e), 
                weightgain=weightgain, 
                weightloss=weightloss, 
                pass_status=pass_status, 
                site_time=timezone.make_aware(datetime.datetime.strptime(site_time[:19], "%Y-%m-%dT%H:%M:%S")),
                shift=shift
            )
        except Exception as exception:
            print(str(exception))
        try:
            PipeData.objects.create(mid=mid, b=b, c=c, d=d, e=e, ts=ts, count=count,
                                    weight=weight, ps=ps, site_time=site_time, shift=shift)
        except Exception as exception:
            print(str(exception))
        return HttpResponse(status=200)
    else:
       return HttpResponse(status=400)
    

    






def index(request):
    data = {"data": []}
    for i in PipeData.objects.all()[: : -1][:100]:
        data["data"].append(i.toDic())
    return JsonResponse(data, json_dumps_params={'indent': 4})


@login_required(login_url='/')
def fetch(request):
    data = {"data": []}
    for i in PipeDataProcessed.objects.all()[: 100]:
        data["data"].append(i.toDic())
    return JsonResponse(data, json_dumps_params={'indent': 4})







