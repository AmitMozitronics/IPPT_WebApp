import datetime
import pytz
from datetime import timedelta
from django.utils import timezone as util_timezone

from django.db.models import Sum, Avg, Count, F, ExpressionWrapper, BigIntegerField
from django.db.models.functions import TruncDay, TruncYear, TruncQuarter, TruncMonth, TruncWeek

import time

from api.models import *

import xlwt
import sys
import pandas as pd
from . import downtime
from pytz import timezone
def summary_6_view(user, startdate, enddate, viewformat):
    print("knjvfk")

    print("-------format------", startdate, enddate, viewformat)
    machine = Machine.objects.filter(user=user)
    machine_list = []
    for i in machine:
        machine_list.append(i.toDic()["machine_id"])

    #----Souren---20/04/21-------#
    startdate_samp = datetime.datetime.strptime(startdate, "%Y-%m-%d")
    enddate_samp = datetime.datetime.strptime(enddate, "%Y-%m-%d")
    deltaDay = (enddate_samp - startdate_samp).days+1
    print(">>>>>>>>>>>delta day>>>>>>>>>>>>>>", deltaDay)
    machine_details = Machine.objects.get(machine_id=machine_list[0])
    starttime = machine_details.shift1_start_time
    machine_total_shift = machine_details.machine_total_shift
    if machine_total_shift == 2:
        endtime=machine_details.shift2_end_time
    else:
        endtime = machine_details.shift3_end_time
    shift1_time_duration = machine_details.shift1_time_duration
    shift2_time_duration = machine_details.shift2_time_duration
    if machine_total_shift==3:
        shift3_time_duration = machine_details.shift3_time_duration
    else:
        shift3_time_duration=0
    if (shift1_time_duration+shift2_time_duration+shift3_time_duration==24.00):
        enddate = (datetime.datetime.strptime(enddate, '%Y-%m-%d')+timedelta(days=1)).strftime('%Y-%m-%d')

    local_zone=MachineTimeZone.objects.get(machine_id=machine_list[0]).machine_timezone

    starttimestamp = int(timezone(local_zone).localize(datetime.datetime.strptime(str(startdate) + ' ' + str(starttime), "%Y-%m-%d %H:%M:%S")).timestamp())
    endtimestamp = int(timezone(local_zone).localize(datetime.datetime.strptime(str(enddate) + ' ' + str(endtime), "%Y-%m-%d %H:%M:%S")).timestamp())
    try:
        total_pipe = PipeDataProcessed.objects.filter(site_local_time_range=(starttimestamp, endtimestamp), machine_id_in=machine_list).count()
    except:
        total_pipe=None
    #Day wise downtime
    print("startdate is------", startdate, enddate)
    DowntimeDic={
    "viewformat":[],
    "shift1":[],
    "shift2":[],
    "shift3":[],
    "total":[],
    }
    week_s1_downtime=0
    week_s2_downtime=0
    week_s3_downtime=0
    month_s1_downtime=0
    month_s2_downtime=0
    month_s3_downtime=0
    year_s1_downtime=0
    year_s2_downtime=0
    year_s3_downtime=0
    day_wise_starttime = datetime.datetime.strptime(str(startdate)+' '+str(starttime), "%Y-%m-%d %H:%M:%S")
    day_wise_endtime = day_wise_starttime+timedelta(hours=shift1_time_duration+shift2_time_duration+shift3_time_duration) 
    print("day_wise_starttime", day_wise_starttime)
    print("day_wise_end_time", day_wise_endtime)
    #getting number of days in a month
    c3=startdate_samp
    x_date = datetime.datetime.strptime(str(startdate) + " " + str(starttime), '%Y-%m-%d %H:%M:%S')
    next_mon = (x_date+pd.offsets.MonthEnd(1))+timedelta(days=1) #using pandas for the next month
    c1=(datetime.datetime.strptime(str(next_mon), '%Y-%m-%d %H:%M:%S')).strftime('%Y-%m-%d') #striping of the time section from the date
    c2=datetime.datetime.strptime(c1, "%Y-%m-%d") #converting the strf object into datetime object
    month_days = (c2-c3).days
    z=1
    #will write a if statement to check whether the format is week and day, otherwise block should increase execute time---
    if viewformat=="Day" or viewformat=="Week" or viewformat=="Month" or viewformat=="Year" or viewformat=="Quarter":
        for i in range(deltaDay):
            if  machine_total_shift == 3:
                try:
                    shift1_data = PipeDataProcessed.objects.filter(site_local_time_range=(day_wise_starttime, day_wise_endtime), machine_id_in = machine_list, shift="1")
                    shift1_df = pd.DataFrame.from_records(shift1_data.values())
                    shift1_downtime = downtime.calculate_downtime(shift1_df)
                    s1_downtime = shift1_downtime
                except:
                    shift1_downtime = 0
                    s1_downtime = 0
                try:
                    shift_data = PipeDataProcessed.objects.filter(site_local_time_range=(day_wise_starttime, day_wise_endtime), machine_id_in=machine_list, shift='2')
                    shift2_df = pd.DataFrame.from_records(shift2_data.values())
                    shift2_downtime = downtime.calculate_downtime(shift2_df)
                    s2_downtime = shift2_downtime
                except:
                    shift2_downtime = 0
                    s2_downtime = 0

                try:
                    shift_data = PipeDataProcessed.objects.filter(site_local_time_range=(day_wise_starttime, day_wise_endtime), machine_id_in=machine_list, shift='3')
                    shift3_df = pd.DataFrame.from_records(shift3_data.values())
                    shift3_downtime = downtime.calculate_downtime(shift3_df)
                    s3_downtime = shift3_downtime
                except:
                    shift3_downtime = 0
                    s3_downtime = 0
                totaldowntime = shift1_downtime+shift2_downtime+shift3_downtime
                t_downtime = totaldowntime
            elif machine_total_shift == 2:
                try:
                    shift1_data = PipeDataProcessed.objects.filter(site_local_time__range=(day_wise_starttime, day_wise_endtime), machine_id__in = machine_list, shift='1')
                    shift1_df = pd.DataFrame.from_records(shift1_data.values())
                    shift1_downtime = downtime.calculate_downtime(shift1_df)
                    s1_downtime = shift1_downtime
                except:
                    shift1_downtime = 0
                    s1_downtime = 0
                try:
                    shift2_data = PipeDataProcessed.objects.filter(site_local_time__range=(day_wise_starttime, day_wise_endtime), machine_id__in = machine_list, shift='2')
                    shift2_df = pd.DataFrame.from_records(shift2_data.values())
                    shift2_downtime = downtime.calculate_downtime(shift2_df)
                    s2_downtime = shift2_downtime
                except:
                    shift2_downtime = 0
                    s2_downtime =0
                shift3_downtime = 0
                s3_downtime=0
                totaldowntime = shift1_downtime+shift2_downtime+shift3_downtime
                t_downtime = totaldowntime
            totaldowntime = time.strftime('%H:%M', time.gmtime(totaldowntime*3600))
            shift2_downtime = time.strftime('%H:%M', time.gmtime(shift2_downtime*3600))
            shift1_downtime = time.strftime('%H:%M', time.gmtime(shift1_downtime*3600))
            shift3_downtime =  time.strftime('%H:%M', time.gmtime(shift3_downtime*3600))
            if viewformat=="Day":
                DowntimeDic['viewformat'].append(day_wise_starttime)
                DowntimeDic['shift1'].append(shift1_downtime)
                DowntimeDic['shift2'].append(shift2_downtime)
                DowntimeDic['shift3'].append(shift3_downtime)
                DowntimeDic['total'].append(totaldowntime)

            if viewformat=="Week":
                if i%6 != 0 or i == 0 :
                    week_s1_downtime += s1_downtime
                    week_s2_downtime += s2_downtime
                    week_s3_downtime += s3_downtime
                    week_total = week_s1_downtime+week_s2_downtime+week_s3_downtime
                else:
                    week_s1_downtime += s1_downtime
                    week_s2_downtime += s2_downtime
                    week_s3_downtime += s3_downtime
                    week_start = day_wise_starttime-timedelta(days=6)
                    DowntimeDic['viewformat'].append(str(week_start) + " to " + str(day_wise_starttime))
                    DowntimeDic['shift1'].append(week_s1_downtime)
                    DowntimeDic['shift2'].append(week_s2_downtime)
                    DowntimeDic['shift3'].append(week_s3_downtime)
                    DowntimeDic['total'].append(week_total)
                    week_s1_downtime=0
                    week_s2_downtime=0
                    week_s3_downtime=0
            if viewformat=="Month":
                if i%(deltaDay-1) != 0 or i == 0 :
                    month_s1_downtime += s1_downtime
                    month_s2_downtime += s2_downtime
                    month_s3_downtime += s3_downtime
                    month_total = month_s1_downtime+month_s2_downtime+month_s3_downtime
                else:
                    month_s1_downtime += s1_downtime
                    month_s2_downtime += s2_downtime
                    month_s3_downtime += s3_downtime
                    DowntimeDic['viewformat'].append(str(day_wise_starttime) + " to " + str(day_wise_endtime))
                    DowntimeDic['shift1'].append(month_s1_downtime)
                    DowntimeDic['shift2'].append(month_s2_downtime)
                    DowntimeDic['shift3'].append(month_s3_downtime)
                    DowntimeDic['total'].append(month_total)
                    month_s1_downtime=0
                    month_s2_downtime=0
                    month_s3_downtime=0
            if viewformat=="Year" or viewformat=="Quarter":
                if z%month_days != 0:
                    year_s1_downtime += s1_downtime
                    year_s2_downtime += s2_downtime
                    year_s3_downtime += s3_downtime
                    year_total = year_s1_downtime+year_s2_downtime+year_s3_downtime
                    z+=1
                else:
                    year_s1_downtime += s1_downtime
                    year_s2_downtime += s2_downtime
                    year_s3_downtime += s3_downtime
                    DowntimeDic['viewformat'].append(str(c3.strftime("%B, %Y")) + " to " + str(c2.strftime("%B, %Y")))
                    DowntimeDic['shift1'].append(year_s1_downtime)
                    DowntimeDic['shift2'].append(year_s2_downtime)
                    DowntimeDic['shift3'].append(year_s3_downtime)
                    DowntimeDic['total'].append(year_total)
                    c3=c2
                    next_mon = (c2+pd.offsets.MonthEnd(1))+timedelta(days=1) #using pandas for the next month
                    c1=(datetime.datetime.strptime(str(next_mon), '%Y-%m-%d %H:%M:%S')).strftime('%Y-%m-%d')
                    c2=datetime.datetime.strptime(c1, "%Y-%m-%d")
                    month_days=(c2-c3).days
                    print(">>>>", month_days)
                    year_s1_downtime=0
                    year_s2_downtime=0
                    year_s3_downtime=0
                    z=1
                # if i==deltaDay-2:
                #     DowntimeDic['viewformat'].append(str(c3) + " to " + str(c2))
                #     DowntimeDic['shift1'].append(year_s1_downtime)
                #     DowntimeDic['shift2'].append(year_s2_downtime)
                #     DowntimeDic['shift3'].append(year_s3_downtime)
                #     DowntimeDic['total'].append(year_total)


            day_wise_starttime = day_wise_starttime+timedelta(days=1)
            day_wise_endtime = day_wise_endtime+timedelta(days=1)


    if viewformat=="can be deleted":
        format_startdate = datetime.datetime.strptime(str(startdate) + " " + str(starttime), '%Y-%m-%d %H:%M:%S')
        if (shift1_time_duration+shift2_time_duration+shift3_time_duration==24.00):
            if viewformat=="Month":
                format_enddate = (format_startdate+pd.offsets.MonthEnd(1))+timedelta(days=1) 
                next_month = format_startdate+pd.offsets.MonthEnd(1)+timedelta(days=1) #format_endate and next_month are same viewformat month
            else:
                format_enddate = format_startdate+pd.offsets.MonthEnd(12)+timedelta(days=1)
                next_month = format_startdate+pd.offsets.MonthEnd(1)+timedelta(days=1)
        else:
            if viewformat=="Month":
                format_enddate = format_startdate+pd.offsets.MonthEnd(1)
                next_month = format_startdate+pd.offsets.MonthEnd(1)
            else:
                format_enddate = format_startdate+pd.offsets.MonthEnd(12)
                next_month = format_startdate+pd.offsets.MonthEnd(1)
        monthnum = (format_enddate.year-format_startdate.year)*12 + (format_enddate.month-format_startdate.month)
        print("month num is--------", monthnum)
        for m in range(monthnum):
            if  machine_total_shift == 3:
                try:
                    shift1_data = PipeDataProcessed.objects.filter(site_local_time_range=(format_startdate, next_month), machine_id_in = machine_list, shift="1")
                    shift1_df = pd.DataFrame.from_records(shift1_data.values())
                    shift1_downtime = downtime.calculate_downtime(shift1_df)
                    s1_downtime = shift1_downtime
                    print("-------------------------------shift1 downtime", shift1_downtime)
                except:
                    shift1_downtime = 0
                    s1_downtime = 0
                try:
                    shift_data = PipeDataProcessed.objects.filter(site_local_time_range=(format_startdate, next_month), machine_id_in=machine_list, shift='2')
                    shift2_df = pd.DataFrame.from_records(shift2_data.values())
                    shift2_downtime = downtime.calculate_downtime(shift2_df)
                    s2_downtime = shift2_downtime
                except:
                    shift2_downtime = 0
                    s2_downtime = 0

                try:
                    shift_data = PipeDataProcessed.objects.filter(site_local_time_range=(format_startdate, next_month), machine_id_in=machine_list, shift='3')
                    shift3_df = pd.DataFrame.from_records(shift3_data.values())
                    shift3_downtime = downtime.calculate_downtime(shift3_df)
                    s3_downtime = shift3_downtime
                except:
                    shift3_downtime = 0
                    s3_downtime = 0
                totaldowntime = shift1_downtime+shift2_downtime+shift3_downtime
                t_downtime = totaldowntime
            elif machine_total_shift == 2:
                try:
                    print("@@@@@@@@@@@@@@@@@@", format_startdate, format_enddate)
                    shift1_data = PipeDataProcessed.objects.filter(site_local_time__range=(format_startdate, next_month), machine_id__in = machine_list, shift='1')
                    shift1_df = pd.DataFrame.from_records(shift1_data.values())     
                    print("____________________________________", shift1_df)                    

                    shift1_downtime = downtime.calculate_downtime(shift1_df)

                    s1_downtime = shift1_downtime
                    print("____________________________________shif1 downtime", shift1_downtime)
                except:
                    shift1_downtime = 0
                    s1_downtime = 0

                try:
                    shift2_data = PipeDataProcessed.objects.filter(site_local_time__range=(format_startdate, next_month), machine_id__in = machine_list, shift='2')
                    shift2_df = pd.DataFrame.from_records(shift2_data.values())
                    shift2_downtime = downtime.calculate_downtime(shift2_df)
                    s2_downtime = shift2_downtime
                except:
                    shift2_downtime = 0
                    s2_downtime =0
                shift3_downtime = 0
                s3_downtime=0
                totaldowntime = shift1_downtime+shift2_downtime+shift3_downtime
                t_downtime = totaldowntime
            totaldowntime = time.strftime('%H:%M', time.gmtime(totaldowntime*3600))
            shift2_downtime = time.strftime('%H:%M', time.gmtime(shift2_downtime*3600))
            shift1_downtime = time.strftime('%H:%M', time.gmtime(shift1_downtime*3600))
            shift3_downtime =  time.strftime('%H:%M', time.gmtime(shift3_downtime*3600))


            DowntimeDic["viewformat"].append(str(format_startdate) + " to " + str(next_month))
            DowntimeDic["shift1"].append(shift1_downtime)
            DowntimeDic["shift2"].append(shift2_downtime)
            DowntimeDic["shift3"].append(shift3_downtime)
            DowntimeDic["total"].append(totaldowntime)
            #if total shift is 24 than end time of a month is same as starttime of the another month
            if shift1_time_duration+shift2_time_duration+shift3_time_duration==24.00:
                format_startdate = next_month                
                next_month = next_month+pd.offsets.MonthEnd(1)+timedelta(days=1)
            #if total shift is less than 24 then we have to add a day to get to the next month
            else:
                format_startdate = next_month+timedelta(days=1)                
                next_month = next_month+pd.offsets.MonthEnd(1)+timedelta(days=1)


    return 'summary_6.html', {
        "machine": machine,
        "startdate": startdate_samp,
        "enddate": enddate_samp,
        "viewformat": viewformat,
        "summary_name": "MIS 6: DOWN TIME SUMMARY",
        "pipecountsum": zip(
            DowntimeDic['viewformat'],
            DowntimeDic['shift1'],
            DowntimeDic['shift2'],
            DowntimeDic['shift3'],
            DowntimeDic['total']
        )
    }
