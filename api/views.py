from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.utils import timezone
from django.db.models import Q
from django.conf import settings
from datetime import timedelta
import re
import json
import datetime
import pytz
import sys

from .models import *


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
                site_time1 = site_time+timedelta(hours=5,minutes=30)
                try:
                    MachineStatus.objects.create(machine_id=Machine.objects.get(machine_id=mid), active_date_time=site_time1)
                except:
                    MachineStatus.objects.filter(machine_id=Machine.objects.get(machine_id=mid)).update(active_date_time=site_time1)
                if(ts != "999"):
                    site_time1 = tsdatetime+timedelta(hours=5,minutes=30)
                shiftstart1 = site_time1.replace(
                    hour=7, minute=0, second=0, microsecond=0)
                shiftend1 = site_time1.replace(
                    hour=14, minute=59, second=59, microsecond=0)
                shiftstart2 = site_time1.replace(
                    hour=15, minute=0, second=0, microsecond=0)
                shiftend2 = site_time1.replace(
                    hour=22, minute=59, second=59, microsecond=0)
                if shiftstart1 <= site_time1 and site_time1 <= shiftend1:
                    shift = "1"
                elif shiftstart2 <= site_time1 and site_time1 <= shiftend2:
                    shift = "2"
                else:
                    shift = "3"

                machine_details = Machine.objects.get(machine_id = mid)
                shift1_time = (machine_details.shift1_start_time,machine_details.shift1_end_time)
                shift1_time_duration = machine_details.shift1_time_duration
                shift2_time = (machine_details.shift2_start_time,machine_details.shift2_end_time)
                shift2_time_duration = machine_details.shift2_time_duration
                shift3_time = (machine_details.shift3_start_time,machine_details.shift3_end_time)
                shift3_time_duration = machine_details.shift3_time_duration

                shiftstart1 = site_time1.replace(hour=shift1_time[0].hour, minute=shift1_time[0].minute, second=shift1_time[0].second, microsecond=0)
                shiftend1 = site_time1.replace(hour=shift1_time[1].hour, minute=shift1_time[1].minute, second=shift1_time[1].second, microsecond=0)
                shiftstart2 = site_time1.replace(hour=shift2_time[0].hour, minute=shift2_time[0].minute, second=shift2_time[0].second, microsecond=0)
                shiftend2 = site_time1.replace(hour=shift2_time[1].hour, minute=shift2_time[1].minute, second=shift2_time[1].second, microsecond=0)

                if shift3_time[0] != None and shift3_time[1] != None:
                    machine_total_time_duration = int(shift1_time_duration + shift2_time_duration + shift3_time_duration)
                    shiftstart3 = site_time1.replace(hour=shift3_time[0].hour, minute=shift3_time[0].minute, second=shift3_time[0].second, microsecond=0)
                    shiftend3 = site_time1.replace(hour=shift3_time[1].hour, minute=shift3_time[1].minute, second=shift3_time[1].second, microsecond=0)
                    if shiftstart1 <= site_time1 and site_time1 <= shiftend1:
                        shift = "1"
                    elif shiftstart2 <= site_time1 and site_time1 <= shiftend2:
                        shift = "2"
                    else:
                        shift = "3"
                elif shift3_time[0] == None and shift3_time[1] == None:
                    if shiftstart1 <= site_time1 and site_time1 <= shiftend1:
                        shift = "1"
                    else :
                        shift = "2"

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
            if str(mid)=='16' or str(mid)=='21' or str(mid)=='20':
                b=str(b)
                st_type_code=b[1:3]
                stc=StandardTypeClassification.objects.get(basic_metarial=bms, code=int(st_type_code))
                standard_type_classification = stc.standard_type_classification
            else:    
                stc = StandardTypeClassification.objects.filter(
                    basic_metarial=bms, code=b[1])[0]
                standard_type_classification = stc.toDic().get("standard_type_classification")
        except:
            stc = None
            standard_type_classification = None
        try:
            b=str(b)
            if(len(b) == 4):
                if str(mid)=='16' or str(mid)=='21' or str(mid)=='20':
                    pts_code = int(b[3])
                    pts = PressureTypeSpecification.objects.get(basic_metarial=bms, standard_type_classification=stc, code=pts_code)
                    pressure_type_specification=pts.pressure_type_specification
                else:
                    pts_code = int(b[2] + b[3])

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
            PipeDataProcessed.objects.create(machine_id=mid, basic_metarial=basic_metarial, standard_type_classification=standard_type_classification, pressure_type_specification=pressure_type_specification, outer_diameter=outer_diameter, outer_diameter_unit=outer_diameter_unit, length = length, length_unit = length_unit, timestamp = int(ts), count = int(count), weight = int(weight), maxweight = int(d), minweight = int(e), weightgain = weightgain, weightloss = weightloss, pass_status = pass_status, site_time = site_time1,site_local_time = site_time1, shift = shift)
        except Exception as excep:
            print(excep)
    try:
        site_time = site_time1.isoformat()
    except:
        pass
    try:
        PipeData.objects.create(mid=mid, b=b, c=c, d=d, e=e, ts=ts, count=count,
                                weight=weight, ps=ps, site_time=site_time1, shift=shift)
    except:
        print("PipeData.objects.create ERROR")
    #return HttpResponse(status=200)
    return HttpResponse("Okay")


def ipptv2_data(request):
    try:
        ipptv2_error_details = open("ipptv2_error_details",'a+')
        ipptv2_error_details.write('\n 0: '+str(request.get_full_path()))
    except:
        pass

    try:
        machine_id = request.GET.get('a')
        basic_material_code = request.GET.get('b')
        standerd_type_classification_code = request.GET.get('c')
        pressure_rating = request.GET.get('d')
        outer_diameter_code = request.GET.get('e')
        pipe_length = request.GET.get('f')
        pipe_max_weight = request.GET.get('g')
        pipe_min_weight = request.GET.get('h')
        i,j,k = request.GET.get('i'),request.GET.get('j'),request.GET.get('k')
        time_stamp = request.GET.get('l')
        pipe_count = request.GET.get('m')
        pipe_weight = request.GET.get('n')
        pipe_pass_status_code = request.GET.get('o')

        ipptv2_error_details.write(str(machine_id))
        ipptv2_error_details.write(str(basic_material_code))
        ipptv2_error_details.write(str(standerd_type_classification_code))
        ipptv2_error_details.write(str(pressure_rating))
        ipptv2_error_details.write(str(outer_diameter_code))
        ipptv2_error_details.write(str(pipe_length))
        ipptv2_error_details.write(str(pipe_max_weight))
        ipptv2_error_details.write(str(pipe_min_weight))
        ipptv2_error_details.write(str(i))
        ipptv2_error_details.write(str(j))
        ipptv2_error_details.write(str(k))
        ipptv2_error_details.write(str(time_stamp))
        ipptv2_error_details.write(str(pipe_count))
        ipptv2_error_details.write(str(pipe_weight))
        ipptv2_error_details.write(str(pipe_pass_status_code))

    except:
        ipptv2_error_details.write('\n 12: '+sys.exc_info())
        """machine_id = None
        basic_material_code = None
        standerd_type_classification_code = None
        pressure_rating = None
        outer_diameter_code = None
        pipe_length = None
        pipe_max_weight = None
        pipe_min_weight = None
        i,j,k = None,None,None
        time_stamp = None
        pipe_count = None
        pipe_weight = None
        pipe_pass_status = None"""

    #Process basic material data
    try:
        basic_material_data = BasicMetarialStandard.objects.filter(code = basic_material_code)[0]
        basic_material_standard = basic_material_data.toDic().get("basic_metarial")
    except:
        basic_material_standard = None

    #Process standard type classification data
    try:
        standerd_type_classification_data = StandardTypeClassification.objects.filter(basic_metarial = basic_material_data,code = standerd_type_classification_code)[0]
        standerd_type_classification = standerd_type_classification_data.toDic().get('standard_type_classification')
    except:
        ipptv2_error_details.write('\n 2: '+str(sys.exc_info()))
        standerd_type_classification = None

    #Process pressure type classification data
    try:
        pressure_type_classificaion_data = PressureTypeSpecification.objects.filter(basic_metarial=basic_material_data, standard_type_classification=standerd_type_classification_data, code=pressure_rating)[0]
        pressure_type_classificaion = pressure_type_classificaion_data.toDic().get('pressure_type_specification')
    except:
        ipptv2_error_details.write('\n 3: '+str(sys.exc_info()))
        pressure_type_classificaion = None

    #process pipe outer diameter data
    try:
        ipptv2_error_details.write('\n 9: '+str(standerd_type_classification))
        pipe_outer_diameter_data = PipeOuterDiameter.objects.filter(standard_type_classification=standerd_type_classification_data, code=outer_diameter_code)[0]
        ipptv2_error_details.write('\n 8: '+ str(pipe_outer_diameter_data))
        pipe_outer_diameter_data_dic = pipe_outer_diameter_data.toDic()
        pipe_outer_diameter_unit = str(pipe_outer_diameter_data_dic.get("unit"))
        pipe_outer_diameter_value = float(pipe_outer_diameter_data_dic.get("outer_diameter"))
    except:
        ipptv2_error_details.write('\n 4: '+str(sys.exc_info()))
        pipe_outer_diameter_unit = None
        pipe_outer_diameter_value = None
    
    #Process pipe length
    try:
        pipe_length_data = PipeLength.objects.filter(standard_type_classification=standerd_type_classification_data, code=pipe_length)[0]
        pipe_length_value = float(pipe_length_data.toDic().get('length'))
        pipe_length_unit = str(pipe_length_data.toDic().get('unit'))
    except:
        ipptv2_error_details.write('\n 9: '+str(sys.exc_info()))
        pipe_length_value = None
        pipe_length_unit = None

    #no need to process pipe weight , maxweight, minweight, count

    #process weightgain and weight loss
    try:
        pipe_weight = int(pipe_weight)
        pipe_max_weight = int(pipe_max_weight)
        if pipe_weight > pipe_max_weight:
            pipe_weight_loss = pipe_max_weight - pipe_weight
            pipe_weight_gain = 0
        elif pipe_weight <= pipe_max_weight:
            pipe_weight_gain = pipe_max_weight - pipe_weight
            pipe_weight_loss = 0
        ipptv2_error_details.write('\n 10: '+'machine_id'+str(machine_id)+' : '+str(pipe_weight_gain))
    except:
        pipe_weight_gain = None
        ipptv2_error_details.write('\n 10: '+'machine_id'+str(machine_id)+' : '+str(sys.exc_info()))

    #Process Pipe Pass status
    try:
        pipe_pass_status_data = PipePassStatus.objects.filter(pipe_pass_status_code = int(pipe_pass_status_code))[0]
        ipptv2_error_details.write('\n 11: '+str(PipePassStatus.objects.filter(pipe_pass_status_code = int(pipe_pass_status_code))))
        pipe_pass_status = pipe_pass_status_data.toDic().get('pipe_pass_status')
    except:
        ipptv2_error_details.write('\n 12: '+str(sys.exc_info()))
        pipe_pass_status = None


    #process pipe weight time
    try:
        machine_timezone = MachineTimeZone.objects.get(machine_id = machine_id)#Get machine timezone from database
        ipptv2_error_details.write('\n 13: '+str(machine_timezone))
        pipe_weight_time = datetime.datetime.fromtimestamp(int(time_stamp), tz=pytz.timezone(machine_timezone.machine_timezone))#Convert Pipe weight timestamp to datetime in local time of that machine
        pipe_weight_time_no_timezone = pipe_weight_time.replace(tzinfo = None)
        ipptv2_error_details.write('\n 14: '+str(pipe_weight_time_no_timezone))
    except:
        ipptv2_error_details.write('\n 5: '+str(sys.exc_info()))

    #Process current machine shift
    try:
        machine_details = Machine.objects.get(machine_id = machine_id)
        shift1_time = (machine_details.shift1_start_time,machine_details.shift1_end_time)
        shift1_time_duration = machine_details.shift1_time_duration
        shift2_time = (machine_details.shift2_start_time,machine_details.shift2_end_time)
        shift2_time_duration = machine_details.shift2_time_duration
        shift3_time = (machine_details.shift3_start_time,machine_details.shift3_end_time)
        shift3_time_duration = machine_details.shift3_time_duration

        shiftstart1 = pipe_weight_time_no_timezone.replace(hour=shift1_time[0].hour, minute=shift1_time[0].minute, second=shift1_time[0].second, microsecond=0)
        shiftend1 = pipe_weight_time_no_timezone.replace(hour=shift1_time[1].hour, minute=shift1_time[1].minute, second=shift1_time[1].second, microsecond=0)
        shiftstart2 = pipe_weight_time_no_timezone.replace(hour=shift2_time[0].hour, minute=shift2_time[0].minute, second=shift2_time[0].second, microsecond=0)
        shiftend2 = pipe_weight_time_no_timezone.replace(hour=shift2_time[1].hour, minute=shift2_time[1].minute, second=shift2_time[1].second, microsecond=0)

        if shift3_time[0] != None and shift3_time[1] != None:
            machine_total_time_duration = int(shift1_time_duration + shift2_time_duration + shift3_time_duration)
            shiftstart3 = pipe_weight_time_no_timezone.replace(hour=shift3_time[0].hour, minute=shift3_time[0].minute, second=shift3_time[0].second, microsecond=0)
            shiftend3 = pipe_weight_time_no_timezone.replace(hour=shift3_time[1].hour, minute=shift3_time[1].minute, second=shift3_time[1].second, microsecond=0)
            if shiftstart1 <= pipe_weight_time_no_timezone and pipe_weight_time_no_timezone <= shiftend1:
                shift = "1"
            elif shiftstart2 <= pipe_weight_time_no_timezone and pipe_weight_time_no_timezone <= shiftend2:
                shift = "2"
            else:
                shift = "3"
        elif shift3_time[0] == None and shift3_time[1] == None:
            if shiftstart1 <= pipe_weight_time_no_timezone and pipe_weight_time_no_timezone <= shiftend1:
                shift = "1"
            else :
                shift = "2"
    except:
        ipptv2_error_details.writ('\n 16: '+str(sys.exc_info()))

    #Process data entry to Machine status table
    try:
        MachineStatus.objects.create(machine_id = Machine.objects.get(machine_id = machine_id), active_date_time = pipe_weight_time_no_timezone)
    except:
        MachineStatus.objects.filter(machine_id = Machine.objects.get(machine_id = machine_id)).update(active_date_time = pipe_weight_time_no_timezone)

    #Save machine status
    try:
        MachineStatus.objects.create(machine_id=Machine.objects.get(machine_id=machine_id), active_date_time=pipe_weight_time_no_timezone)
    except:
        MachineStatus.objects.filter(machine_id=Machine.objects.get(machine_id=machine_id)).update(active_date_time=pipe_weight_time_no_timezone)
    
    #process data entry to Pipedataprocess table
    try:
        ipptv2_error_details.write('\n 6: '+str(machine_id))
        ipptv2_error_details.write('\n 15: '+str(pipe_weight_time))
        ipptv2_error_details.write('\n 17: '+str(pipe_weight_time_no_timezone))
        if pipe_weight_time_no_timezone != None:
            PipeDataProcessed.objects.create(site_local_time = pipe_weight_time_no_timezone,machine_id=machine_id, basic_metarial=basic_material_standard, standard_type_classification=standerd_type_classification, pressure_type_specification=pressure_type_classificaion,
                outer_diameter=pipe_outer_diameter_value, outer_diameter_unit=pipe_outer_diameter_unit, length = pipe_length_value, count=pipe_count, length_unit = pipe_length_unit,
                 weight = int(pipe_weight), maxweight = int(pipe_max_weight), minweight = int(pipe_min_weight), weightgain = pipe_weight_loss, pass_status = pipe_pass_status,weightloss = pipe_weight_gain,
                 timestamp = int(time_stamp), site_time = pipe_weight_time, shift = shift)

            ipptv2_error_details.close()
            return HttpResponse("Okay")
        else:
            return HttpResponse("Not okay")
    except:
        ipptv2_error_details.write('\n 7: '+str(sys.exc_info()))
        ipptv2_error_details.close()
        return HttpResponse("Not okay")


        """try:
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



    return HttpResponse("Working on it.")"""






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
            b=str(b)
            if len(b)==4:
                if str(mid)=='16' or str(mid)=='20' or str(mid)=='21':
                    st_type_code = b[1:3]
                    stc = StandardTypeClassification.objects.get(basic_metarial=bms, code=int(st_type_code))
                    standard_type_classification = stc.standard_type_classification
            else:
                b=int(b)
                stc = StandardTypeClassification.objects.get(
                basic_metarial=bms, code=b[1])
                standard_type_classification = stc.standard_type_classification
        except:
            stc = None
            standard_type_classification = None
        try:
            b=str(b)
            if(len(b) == 4):
                if str(mid)=='16' or str(mid)=='20' or str(mid)=='21':
                    pts_code=int(b[3])
                else:
                    pts_code = b[2] + b[3]
            else:
                b=int(b)
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
        site_time=timezone.make_aware(datetime.datetime.strptime(site_time[:19], "%Y-%m-%dT%H:%M:%S"))
        machine_details = Machine.objects.get(machine_id = mid)
        shift1_time = (machine_details.shift1_start_time,machine_details.shift1_end_time)
        shift1_time_duration = machine_details.shift1_time_duration
        shift2_time = (machine_details.shift2_start_time,machine_details.shift2_end_time)
        shift2_time_duration = machine_details.shift2_time_duration
        shift3_time = (machine_details.shift3_start_time,machine_details.shift3_end_time)
        shift3_time_duration = machine_details.shift3_time_duration

        """if machine_details.machine_total_shift == 2:
            shift1_time_duration = machine_details.shift1_time_duration
            shift1_time = (machine_details.shift1_start_time,machine_details.shift1_start_time+timedelta(hours=int(shift1_time_duration)))
            shift2_time_duration = machine_details.shift2_time_duration
            shift2_time = (machine_details.shift2_start_time,machine_details.shift2_start_time+timedelta(hours=int(shift2_time_duration)))
            shiftstart1 = site_time.replace(hour=shift1_time[0].hour, minute=shift1_time[0].minute, second=shift1_time[0].second, microsecond=0)
            shiftend1 = site_time.replace(hour=shift1_time[1].hour, minute=shift1_time[1].minute, second=shift1_time[1].second, microsecond=0)
            shiftstart2 = site_time.replace(hour=shift2_time[0].hour, minute=shift2_time[0].minute, second=shift2_time[0].second, microsecond=0)
            shiftend2 = site_time.replace(hour=shift2_time[1].hour, minute=shift2_time[1].minute, second=shift2_time[1].second, microsecond=0)
            if shiftstart1 <= site_time and site_time <= shiftend1:
                shift = "1"
            else :
                shift = "2"
        elif machine_details.machine_total_shift == 3:
            shift1_time_duration = machine_details.shift1_time_duration
            shift1_time = (machine_details.shift1_start_time,machine_details.shift1_start_time+timedelta(hours=int(shift1_time_duration)))
            shift2_time_duration = machine_details.shift2_time_duration
            shift2_time = (machine_details.shift2_start_time,machine_details.shift2_start_time+timedelta(hours=int(shift2_time_duration)))
            shift3_time_duration = machine_details.shift3_time_duration
            shift3_time = (machine_details.shift3_start_time,machine_details.shift3_start_time+timedelta(hours=int(shift3_time_duration)))
            shiftstart1 = site_time.replace(hour=shift1_time[0].hour, minute=shift1_time[0].minute, second=shift1_time[0].second, microsecond=0)
            shiftend1 = site_time.replace(hour=shift1_time[1].hour, minute=shift1_time[1].minute, second=shift1_time[1].second, microsecond=0)
            shiftstart2 = site_time.replace(hour=shift2_time[0].hour, minute=shift2_time[0].minute, second=shift2_time[0].second, microsecond=0)
            shiftend2 = site_time.replace(hour=shift2_time[1].hour, minute=shift2_time[1].minute, second=shift2_time[1].second, microsecond=0)
            shiftstart3 = site_time.replace(hour=shift3_time[0].hour, minute=shift3_time[0].minute, second=shift3_time[0].second, microsecond=0)
            shiftend3 = site_time.replace(hour=shift3_time[1].hour, minute=shift3_time[1].minute, second=shift3_time[1].second, microsecond=0)

            if shiftstart1 <= site_time and site_time <= shiftend1:
                shift = "1"
            elif shiftstart2 <= site_time and site_time <= shiftend2:
                shift = "2"
            else:
                shift = "3"""




        print(site_time)
        print(shift1_time[0])
        shiftstart1 = site_time.replace(hour=shift1_time[0].hour, minute=shift1_time[0].minute, second=shift1_time[0].second, microsecond=0)
        shiftend1 = site_time.replace(hour=shift1_time[1].hour, minute=shift1_time[1].minute, second=shift1_time[1].second, microsecond=0)
        shiftstart2 = site_time.replace(hour=shift2_time[0].hour, minute=shift2_time[0].minute, second=shift2_time[0].second, microsecond=0)
        shiftend2 = site_time.replace(hour=shift2_time[1].hour, minute=shift2_time[1].minute, second=shift2_time[1].second, microsecond=0)

        """f = open("pipe_data.txt",'a+')
        f.write("{}     {}     {}     {}     {}:{}     {}:{} \n".format(str(mid),str(site_time),str(count),str(shift),str(shiftstart1),str(shiftend1),str(shiftstart2),str(shiftend2)))
        f.close()"""

        """if shiftstart1 <= site_time and site_time <= shiftend1:
            shift = "1"
        elif shiftstart2 <= site_time and site_time <= shiftend2:
            shift = "2"""

        if shift3_time[0] != None and shift3_time[1] != None:
            machine_total_time_duration = int(shift1_time_duration + shift2_time_duration + shift3_time_duration)
            shiftstart3 = site_time.replace(hour=shift3_time[0].hour, minute=shift3_time[0].minute, second=shift3_time[0].second, microsecond=0)
            shiftend3 = site_time.replace(hour=shift3_time[1].hour, minute=shift3_time[1].minute, second=shift3_time[1].second, microsecond=0)
            if shiftstart1 <= site_time and site_time <= shiftend1:
                shift = "1"
            elif shiftstart2 <= site_time and site_time <= shiftend2:
                shift = "2"
            else:
                shift = "3"
        elif shift3_time[0] == None and shift3_time[1] == None:
            if shiftstart1 <= site_time and site_time <= shiftend1:
                shift = "1"
            else :
                shift = "2"
        else:
            shift="1"
        

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
                site_time=site_time,#timezone.make_aware(datetime.datetime.strptime(site_time[:19], "%Y-%m-%dT%H:%M:%S")),
                #site_local_time = site_local_time,
                site_local_time = site_time,
                shift=shift
            )
        except Exception as exception:
            print(str(exception))
        try:
            b=int(b)
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

def check_codes(request,code):
    try:
        data = Code.objects.get(code=code)
        return HttpResponse(f"your pipe with code {data} manufactured by Supreme.")
    except Exception as error:
        return HttpResponse("Sorry we can not verify this pipe. ")






