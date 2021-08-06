import datetime
import pytz
from datetime import timedelta
from django.utils import timezone as util_timezone

from django.db.models import Sum, Avg, Count, F, ExpressionWrapper, FloatField
from django.db.models.functions import TruncDay, TruncYear, TruncQuarter, TruncMonth, TruncWeek

import datetime, pytz
from datetime import timedelta
from api.models import *
from pytz import timezone

def summary_3_view(user, startdate, enddate, viewformat):
    machine = Machine.objects.filter(user=user)
    machine_list = []
    for i in machine:
        machine_list.append(i.toDic()["machine_id"])
    #----Souren 20/04/2021 ---------------------------
    machine_details = Machine.objects.get(machine_id=machine_list[0])
    starttime = machine_details.shift1_start_time
    machine_total_shift = machine_details.machine_total_shift
    if machine_total_shift==2:
        endtime = machine_details.shift2_end_time
    else:
        endtime = machine_details.shift3_end_time
    shift1_time_duration = machine_details.shift1_time_duration
    shift2_time_duration = machine_details.shift2_time_duration
    if machine_total_shift == 3:
        shift3_time_duration = machine_details.shift3_time_duration
    else:
        shift3_time_duration = 0
    if (shift1_time_duration+shift2_time_duration+shift3_time_duration==24.00):
        enddate = (datetime.datetime.strptime(enddate, '%Y-%m-%d')+timedelta(days=1)).strftime('%Y-%m-%d')
    local_zone = MachineTimeZone.objects.get(machine_id=machine_list[0]).machine_timezone


    starttimestamp = int(timezone(local_zone).localize(datetime.datetime.strptime(str(startdate) + ' ' + str(starttime), "%Y-%m-%d %H:%M:%S")).timestamp())
    endtimestamp = int(timezone(local_zone).localize(datetime.datetime.strptime(str(enddate) + ' ' + str(endtime), "%Y-%m-%d %H:%M:%S")).timestamp())
    if viewformat == 'Day' or viewformat == 'Week' or viewformat == 'Month':
        pipecountsum = PipeDataProcessed.objects.annotate(group_day=TruncDay('site_local_time')).values('group_day').annotate(Count('weight'), weight__sum__kg=ExpressionWrapper(
            Sum(F('weight') * 1.0 / 1000), output_field=FloatField())).filter(timestamp__gte=starttimestamp, timestamp__lte=endtimestamp, machine_id__in=machine_list)
        pipecountsum.query.clear_ordering(force_empty=True)
        pipecountsum = pipecountsum.order_by('group_day')
        pipecountsum1 = PipeDataProcessed.objects.annotate(group_day=TruncDay('site_local_time')).values('group_day').annotate(Count(
            'weight')).filter(timestamp__gte=starttimestamp, timestamp__lte=endtimestamp, machine_id__in=machine_list, pass_status='Passed')
        pipecountsum1.query.clear_ordering(force_empty=True)
        pipecountsum1 = pipecountsum1.order_by('group_day')
        pipecountsum2 = PipeDataProcessed.objects.annotate(group_day=TruncDay('site_local_time')).values('group_day').annotate(Count(
            'weight')).filter(timestamp__gte=starttimestamp, timestamp__lte=endtimestamp, machine_id__in=machine_list, pass_status='Overweight')
        pipecountsum2.query.clear_ordering(force_empty=True)
        pipecountsum2 = pipecountsum2.order_by('group_day')
        pipecountsum3 = PipeDataProcessed.objects.annotate(group_day=TruncDay('site_local_time')).values('group_day').annotate(Count('weight')).filter(
            timestamp__gte=starttimestamp, timestamp__lte=endtimestamp, machine_id__in=machine_list, pass_status='Underweight')
        pipecountsum3.query.clear_ordering(force_empty=True)
        pipecountsum3 = pipecountsum3.order_by('group_day')
    elif viewformat == 'Quarter' or viewformat == 'Year':
        pipecountsum = PipeDataProcessed.objects.annotate(group_day=TruncMonth('site_local_time')).values('group_day').annotate(Count('weight'), weight__sum__kg=ExpressionWrapper(
            Sum(F('weight') * 1.0 / 1000), output_field=FloatField())).filter(timestamp__gte=starttimestamp, timestamp__lte=endtimestamp, machine_id__in=machine_list)
        pipecountsum.query.clear_ordering(force_empty=True)
        pipecountsum = pipecountsum.order_by('group_day')
        pipecountsum1 = PipeDataProcessed.objects.annotate(group_day=TruncMonth('site_local_time')).values('group_day').annotate(Count(
            'weight')).filter(timestamp__gte=starttimestamp, timestamp__lte=endtimestamp, machine_id__in=machine_list, pass_status='Passed')
        pipecountsum1.query.clear_ordering(force_empty=True)
        pipecountsum1 = pipecountsum1.order_by('group_day')
        pipecountsum2 = PipeDataProcessed.objects.annotate(group_day=TruncMonth('site_local_time')).values('group_day').annotate(Count(
            'weight')).filter(timestamp__gte=starttimestamp, timestamp__lte=endtimestamp, machine_id__in=machine_list, pass_status='Overweight')
        pipecountsum2.query.clear_ordering(force_empty=True)
        pipecountsum2 = pipecountsum2.order_by('group_day')
        pipecountsum3 = PipeDataProcessed.objects.annotate(group_day=TruncMonth('site_local_time')).values('group_day').annotate(Count(
            'weight')).filter(timestamp__gte=starttimestamp, timestamp__lte=endtimestamp, machine_id__in=machine_list, pass_status='Underweight')
        pipecountsum3.query.clear_ordering(force_empty=True)
        pipecountsum3 = pipecountsum3.order_by('group_day')
    else:
        raise Exception("Please select proper format")

    print(starttimestamp, endtimestamp, viewformat)

    pipecountsumdic = {
        "countdate": [],
        "weight": [],
        "count": [],
        "overweight": [],
        "underweight": [],
        "passed": []
    }

    count = weight = overweight = underweight = passed = 0
    index = 0
    for i in pipecountsum:
        if viewformat == 'Day' or viewformat == 'Week' or viewformat == 'Month':
            pipecountsumdic["countdate"].append(
                i['group_day'].strftime("%d/%m/%Y %A"))
        else:
            pipecountsumdic["countdate"].append(
                i['group_day'].strftime("%B, %Y"))
        pipecountsumdic["count"].append(i['weight__count'])
        count += i['weight__count']
        pipecountsumdic["weight"].append(
            round(i['weight__sum__kg'], 2) if i['weight__sum__kg'] != None else 0)
        weight += i['weight__sum__kg']
        flag = False
        for j in pipecountsum1:
            if i['group_day'] == j['group_day']:
                flag = True
                break
        if flag:
            pipecountsumdic["passed"].append(j['weight__count'])
            passed += j['weight__count']
        else:
            pipecountsumdic["passed"].append(0)
            passed += 0
        flag = False
        for j in pipecountsum2:
            if i['group_day'] == j['group_day']:
                flag = True
                break
        if flag:
            pipecountsumdic["overweight"].append(j['weight__count'])
            overweight += j['weight__count']
        else:
            pipecountsumdic["overweight"].append(0)
            overweight += 0
        flag = False
        for j in pipecountsum3:
            if i['group_day'] == j['group_day']:
                flag = True
                break
        if flag:
            pipecountsumdic["underweight"].append(j['weight__count'])
            underweight += j['weight__count']
        else:
            pipecountsumdic["underweight"].append(0)
            underweight += 0
        index += 1
        if (viewformat == 'Month' or viewformat == 'Week') and index == 7:
            pipecountsumdic["countdate"].append("Total")
            pipecountsumdic["count"].append(count)
            pipecountsumdic["weight"].append(weight)
            pipecountsumdic["passed"].append(passed)
            pipecountsumdic["overweight"].append(overweight)
            pipecountsumdic["underweight"].append(underweight)
            pipecountsumdic["countdate"].append("%")
            pipecountsumdic["count"].append(" ")
            pipecountsumdic["weight"].append(" ")
            pipecountsumdic["passed"].append(
                0 if passed == 0 or count == 0 else round((passed / count) * 100, 2))
            pipecountsumdic["overweight"].append(
                0 if overweight == 0 or count == 0 else round((overweight / count) * 100, 2))
            pipecountsumdic["underweight"].append(
                0 if underweight == 0 or count == 0 else round((underweight / count) * 100, 2))
            pipecountsumdic["countdate"].append('')
            pipecountsumdic["count"].append('')
            pipecountsumdic["weight"].append('')
            pipecountsumdic["passed"].append('')
            pipecountsumdic["overweight"].append('')
            pipecountsumdic["underweight"].append('')
            pipecountsumdic["countdate"].append('')
            pipecountsumdic["count"].append('')
            pipecountsumdic["weight"].append('')
            pipecountsumdic["passed"].append('')
            pipecountsumdic["overweight"].append('')
            pipecountsumdic["underweight"].append('')
            index = 0
            count = weight = overweight = underweight = passed = 0
    if ((viewformat == 'Month' or viewformat == 'Week') and index != 7) or ((viewformat == 'Day' or viewformat == 'Year' or viewformat == 'Quarter')):
        pipecountsumdic["countdate"].append("Total")
        pipecountsumdic["count"].append(count)
        pipecountsumdic["weight"].append(round(weight, 2))
        pipecountsumdic["passed"].append(passed)
        pipecountsumdic["overweight"].append(overweight)
        pipecountsumdic["underweight"].append(underweight)
        pipecountsumdic["countdate"].append("%")
        pipecountsumdic["count"].append(" ")
        pipecountsumdic["weight"].append(" ")
        pipecountsumdic["passed"].append(
            0 if passed == 0 or count == 0 else round((passed / count) * 100, 2))
        pipecountsumdic["overweight"].append(
            0 if overweight == 0 or count == 0 else round((overweight / count) * 100, 2))
        pipecountsumdic["underweight"].append(
            0 if underweight == 0 or count == 0 else round((underweight / count) * 100, 2))

    return 'summary_3.html', {
        "machine": machine,
        "startdate": startdate,
        "enddate": enddate,
        "pipecountsum": zip(
            pipecountsumdic["countdate"],
            pipecountsumdic["weight"],
            pipecountsumdic["count"],
            pipecountsumdic["overweight"],
            pipecountsumdic["underweight"],
            pipecountsumdic["passed"]
        ),
        "viewformat": viewformat,
        "summary_name": "MIS 3 : PIPE COUNT SUMMARY"
    }
