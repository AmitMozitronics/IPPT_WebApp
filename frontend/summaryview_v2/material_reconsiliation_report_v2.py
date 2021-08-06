import datetime
import pytz
from datetime import timedelta
from django.utils import timezone as util_timezone

from django.db.models import Sum, Avg, Count, F, ExpressionWrapper, FloatField
from django.db.models.functions import TruncDay, TruncMonth

from api.models import *
from pytz import timezone

def summary_4_view(request):
    machine = Machine.objects.filter(user=request.user)
    machine_list = []
    for i in machine:
        machine_list.append(i.toDic()["machine_id"])
    shiftdate = request.GET.get('shiftdate')
    if shiftdate == None:
        shiftdate = str(util_timezone.localdate())
    # print(shiftdate)
    try:
        MetarialIssueShift.objects.create(
            user=request.user, shift_date=shiftdate)
    except:
        pass
    try:
        metarialissuedic = MetarialIssueShift.objects.get(
            user=request.user, shift_date=shiftdate).toDic()
        metarialissuedic["shift_1"] = metarialissuedic["shift_1"]
        metarialissuedic["shift_2"] = metarialissuedic["shift_2"]
        metarialissuedic["shift_3"] = metarialissuedic["shift_3"]
    except:
        pass
    
    #--Souren--<24-04-2021>----------------------------
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
        shift3_time_duration = 0
    if (shift1_time_duration+shift2_time_duration+shift3_time_duration==24.00):
        startdate_extended = (datetime.datetime.strptime(shiftdate, '%Y-%m-%d')+timedelta(days=1)).strftime('%Y-%m-%d')
    else:
        startdate_extended = shiftdate

    local_zone = MachineTimeZone.objects.get(machine_id=machine_list[0]).machine_timezone #Like Asis/Kolakata
    starttimestamp = int(timezone(local_zone).localize(datetime.datetime.strptime(shiftdate + ' ' + str(starttime), "%Y-%m-%d %H:%M:%S")).timestamp())
    endtimestamp = int(timezone(local_zone).localize(datetime.datetime.strptime(str(startdate_extended) + ' ' + str(endtime), "%Y-%m-%d %H:%M:%S")).timestamp())
    try:
        pipemetarialscrap = []
        pipemetarialscrap.append(PipeDataProcessed.objects.filter(timestamp__gte=starttimestamp, timestamp__lte=endtimestamp, machine_id__in=machine_list,
                                                                  shift='1').aggregate(weight__sum__kg=ExpressionWrapper(Sum(F('weight') * 1.0 / 1000), output_field=FloatField())))
        pipemetarialscrap[0]["issue"] = metarialissuedic["shift_1"]
        pipemetarialscrap[0]["scrap"] = metarialissuedic["shift_1"] - \
            pipemetarialscrap[0]["weight__sum__kg"] if pipemetarialscrap[0]["weight__sum__kg"] != None else 0
        pipemetarialscrap[0]["ratio"] = pipemetarialscrap[0]["scrap"] / \
            (pipemetarialscrap[0]["issue"] + 0.00001)
        pipemetarialscrap.append(PipeDataProcessed.objects.filter(timestamp__gte=starttimestamp, timestamp__lte=endtimestamp, machine_id__in=machine_list,
                                                                  shift='2').aggregate(weight__sum__kg=ExpressionWrapper(Sum(F('weight') * 1.0 / 1000), output_field=FloatField())))
        pipemetarialscrap[1]["issue"] = metarialissuedic["shift_2"]
        pipemetarialscrap[1]["scrap"] = metarialissuedic["shift_2"] - \
            pipemetarialscrap[1]["weight__sum__kg"] if pipemetarialscrap[1]["weight__sum__kg"] != None else 0
        pipemetarialscrap[1]["ratio"] = pipemetarialscrap[1]["scrap"] / \
            (pipemetarialscrap[1]["issue"]+0.00001)
        pipemetarialscrap.append(PipeDataProcessed.objects.filter(timestamp__gte=starttimestamp, timestamp__lte=endtimestamp, machine_id__in=machine_list,
                                                                  shift='3').aggregate(weight__sum__kg=ExpressionWrapper(Sum(F('weight') * 1.0 / 1000), output_field=FloatField())))
        pipemetarialscrap[2]["issue"] = metarialissuedic["shift_3"]
        pipemetarialscrap[2]["scrap"] = metarialissuedic["shift_3"] - \
            pipemetarialscrap[2]["weight__sum__kg"] if pipemetarialscrap[2]["weight__sum__kg"] != None else 0
        pipemetarialscrap[2]["ratio"] = pipemetarialscrap[2]["scrap"] / \
            (pipemetarialscrap[2]["issue"] + 0.00001)
        pipemetarialscrap.append(PipeDataProcessed.objects.filter(timestamp__gte=starttimestamp, timestamp__lte=endtimestamp, machine_id__in=machine_list).aggregate(
            weight__sum__kg=ExpressionWrapper(Sum(F('weight') * 1.0 / 1000), output_field=FloatField())))
        pipemetarialscrap[3]["issue"] = metarialissuedic["shift_3"] + \
            metarialissuedic["shift_2"] + metarialissuedic["shift_1"]
        pipemetarialscrap[3]["scrap"] = pipemetarialscrap[3]["issue"] - \
            pipemetarialscrap[3]["weight__sum__kg"] if pipemetarialscrap[3]["weight__sum__kg"] != None else 0
        pipemetarialscrap[3]["ratio"] = pipemetarialscrap[3]["scrap"] / \
            (pipemetarialscrap[3]["issue"] + 0.000001)
    except Exception as ex:
        print(ex)
    print(starttimestamp, endtimestamp)
    # print(pipemetarialscrap)

    try:
        metarialissuedic["shift_1"] = int(metarialissuedic["shift_1"])
        metarialissuedic["shift_2"] = int(metarialissuedic["shift_2"])
        metarialissuedic["shift_3"] = int(metarialissuedic["shift_3"])
    except:
        metarialissuedic = None
    summary_4_dic = {"machine": machine, "summary_name": "MIS 4 : MATERIAL RECONCILIATION REPORT", "shiftdate": shiftdate,
                     "shiftdatestart": shiftdate, "shiftdateend": startdate_extended, "metarialissuedic": metarialissuedic, "pipemetarialscrap": pipemetarialscrap}
    return 'summary_4.html', summary_4_dic

















def summary_4_view_all(user, startdate, enddate, viewformat):
    machine = Machine.objects.filter(user=user)
    machine_list = []
    for i in machine:
        machine_list.append(i.toDic()["machine_id"])
  
    #---Souren Ghosh----20/04/2021------#
    machine_details = Machine.objects.get(machine_id=machine_list[0])
    print("Machine Id is--------", machine_details)
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

    local_zone = MachineTimeZone.objects.get(machine_id=machine_list[0]).machine_timezone
    starttimestamp = int(timezone(local_zone).localize(datetime.datetime.strptime(
        str(startdate) + ' ' + str(starttime), "%Y-%m-%d %H:%M:%S")).timestamp())
    endtimestamp = int(timezone(local_zone).localize(datetime.datetime.strptime(
        str(enddate) + ' ' + str(endtime), "%Y-%m-%d %H:%M:%S")).timestamp())

    if viewformat == 'Day' or viewformat == 'Week' or viewformat == 'Month':
        misue_shift1 = MetarialIssueShift.objects.annotate(group_day=F('shift_date')).values('group_day').annotate(
            issue__sum__kg=ExpressionWrapper(
                (F('shift_1')* 1.0/1000),
                output_field=FloatField())).filter(
        shift_date__range=(startdate, enddate),
        user=user,
        )

        print("misue_shift1++++++++++++++++", misue_shift1)

        misue_shift2 = MetarialIssueShift.objects.annotate(group_day=F('shift_date')).values('group_day').annotate(
            issue__sum__kg=ExpressionWrapper(
                (F('shift_2')*1.0/1000),
                output_field=FloatField())).filter(
        shift_date__range=(startdate, enddate),
        user=user,
        )

        output_shift1 = PipeDataProcessed.objects.annotate(
            group_day=TruncDay('site_time')).values('group_day', 'shift').annotate(
                weight__sum__kg=ExpressionWrapper(Sum('weight') * 1.0 / 1000,
                                                  output_field=FloatField())).filter(
            timestamp__gte=starttimestamp,
            timestamp__lte=endtimestamp,
            machine_id__in=machine_list,
            shift="1"

        )
        output_shift1.query.clear_ordering(force_empty=True)
        output_shift1=output_shift1.order_by("group_day")

        output_shift2 = PipeDataProcessed.objects.annotate(
            group_day=TruncDay('site_time')).values('group_day', 'shift').annotate(
                weight__sum__kg=ExpressionWrapper(Sum('weight') * 1.0 / 1000,
                                                  output_field=FloatField())).filter(
            timestamp__gte=starttimestamp,
            timestamp__lte=endtimestamp,
            machine_id__in=machine_list,
            shift="2"
        )
        output_shift2.query.clear_ordering(force_empty=True)
        output_shift2=output_shift2.order_by("group_day")

        print("output shift 2------------------", output_shift2)
        if machine_total_shift==3:

            misue_shift3 = MetarialIssueShift.objects.annotate(group_day=F('shift_date')).values('group_day').annotate(
                issue__sum__kg=ExpressionWrapper(
                    (F('shift_3')*1.0/1000),
                    output_field=FloatField())).filter(
            shift_date__range=(startdate, enddate),
            user=user,
            )

            output_shift3 = PipeDataProcessed.objects.annotate(
                group_day=TruncDay('site_time')).values('group_day', 'shift').annotate(
                    weight__sum__kg=ExpressionWrapper(Sum('weight') * 1.0 / 1000,
                                                      output_field=FloatField())).filter(
                timestamp__gte=starttimestamp,
                timestamp__lte=endtimestamp,
                machine_id__in=machine_list,
                shift="3"
            )
            output_shift3.query.clear_ordering(force_empty=True)
            output_shift3=output_shift3.order_by("group_day")
        else:
            misue_shift3=0
            output_shift3=0

            
        misue = MetarialIssueShift.objects.annotate(group_day=F('shift_date')).values('group_day').annotate(
            issue__sum__kg=ExpressionWrapper(
                ((F('shift_1') + F('shift_2') + F('shift_3')) * 1.0 / 1000),
                output_field=FloatField())).filter(
            shift_date__range=(startdate, enddate),
            user=user
        )

        output = PipeDataProcessed.objects.annotate(
            group_day=TruncDay('site_time')).values('group_day').annotate(
                weight__sum__kg=ExpressionWrapper(Sum('weight') * 1.0 / 1000,
                                                  output_field=FloatField())).filter(
            timestamp__gte=starttimestamp,
            timestamp__lte=endtimestamp,
            machine_id__in=machine_list
        )
        output.query.clear_ordering(force_empty=True)
        output = output.order_by("group_day")

    elif viewformat == 'Quarter' or viewformat == 'Year':
        misue_shift1 = MetarialIssueShift.objects.annotate(
            group_day=TruncMonth('shift_date')).values('group_day').annotate(
                issue__sum__kg=ExpressionWrapper(
                    (Sum(F('shift_1')) * 1.0 / 1000),
                    output_field=FloatField())).filter(
            shift_date__range=(startdate, enddate),
            user=user,
        )
        output_shift1 = PipeDataProcessed.objects.annotate(
            group_day=TruncMonth('site_time')).values('group_day', 'shift').annotate(
                weight__sum__kg=ExpressionWrapper(Sum('weight') * 1.0 / 1000,
                                                  output_field=FloatField())).filter(
            timestamp__gte=starttimestamp,
            timestamp__lte=endtimestamp,
            machine_id__in=machine_list,
            shift="1"
        )
        output_shift1.query.clear_ordering(force_empty=True)
        output_shift1 = output_shift1.order_by("group_day")


        misue_shift2 = MetarialIssueShift.objects.annotate(
            group_day=TruncMonth('shift_date')).values('group_day').annotate(
                issue__sum__kg=ExpressionWrapper(
                    (Sum(F('shift_2')) * 1.0 / 1000),
                    output_field=FloatField())).filter(
            shift_date__range=(startdate, enddate),
            user=user,
        )
        output_shift2 = PipeDataProcessed.objects.annotate(
            group_day=TruncMonth('site_time')).values('group_day', 'shift').annotate(
                weight__sum__kg=ExpressionWrapper(Sum('weight') * 1.0 / 1000,
                                                  output_field=FloatField())).filter(
            timestamp__gte=starttimestamp,
            timestamp__lte=endtimestamp,
            machine_id__in=machine_list,
            shift="2"
        )
        output_shift2.query.clear_ordering(force_empty=True)
        output_shift2 = output_shift2.order_by("group_day")

        if machine_total_shift==3:
            misue_shift3 = MetarialIssueShift.objects.annotate(
                group_day=TruncMonth('shift_date')).values('group_day').annotate(
                    issue__sum__kg=ExpressionWrapper(
                        (Sum(F('shift_3')) * 1.0 / 1000),
                        output_field=FloatField())).filter(
                shift_date__range=(startdate, enddate),
                user=user
            )
            output_shift3 = PipeDataProcessed.objects.annotate(
                group_day=TruncMonth('site_time')).values('group_day', 'shift').annotate(
                    weight__sum__kg=ExpressionWrapper(Sum('weight') * 1.0 / 1000,
                                                      output_field=FloatField())).filter(
                timestamp__gte=starttimestamp,
                timestamp__lte=endtimestamp,
                machine_id__in=machine_list,
                shift="3"
            )
            output_shift3.query.clear_ordering(force_empty=True)
            output_shift3 = output_shift3.order_by("group_day")
        else:
            misue_shift3=0
            output_shift3=0

        misue = MetarialIssueShift.objects.annotate(
            group_day=TruncMonth('shift_date')).values('group_day').annotate(
                issue__sum__kg=ExpressionWrapper(
                    (Sum(F('shift_1') + F('shift_2') + F('shift_3')) * 1.0 / 1000),
                    output_field=FloatField())).filter(
            shift_date__range=(startdate, enddate),
            user=user
        )
        output = PipeDataProcessed.objects.annotate(
            group_day=TruncMonth('site_time')).values('group_day').annotate(
                weight__sum__kg=ExpressionWrapper(Sum('weight') * 1.0 / 1000,
                                                  output_field=FloatField())).filter(
            timestamp__gte=starttimestamp,
            timestamp__lte=endtimestamp,
            machine_id__in=machine_list
        )
        output.query.clear_ordering(force_empty=True)
        output = output.order_by("group_day")
    else:
        raise Exception("Please select proper format")

    print(starttimestamp, endtimestamp, viewformat)

    pipecountsumdic = {
        "date": [],      #[{"wholedate": , "shift1":[0.weight, 1.issue, 2.scrap, 3.ration], "shift2":[]}]
        "issue": [],
        "weight": [],
        "scrap": [],
        "ratio": [],
    }

    issue = weight = scrap = 0
    index = 0
    jindex = 0
    m=0
    u1=0
    u2=0
    u3=0
    u4=0
    u5=0
    u6=0
    print("----------------------//", output)
    for i in output:
        if viewformat == 'Day' or viewformat == 'Week' or viewformat == 'Month':
            pipecountsumdic["date"].append({})
            pipecountsumdic["date"][m]['wholedate'] = i['group_day'].strftime("%d/%m/%Y %A")

        else:
            pipecountsumdic["date"].append({})
            pipecountsumdic["date"][m]['wholedate'] = i['group_day'].strftime("%B, %Y")
        pipecountsumdic["weight"].append(round(i['weight__sum__kg'], 2))
        #date key will contain all parameter for shift1 and shift2 for whole timestamp
        #weight_sum of shift1 for the given viewformat

        weight += i['weight__sum__kg']
        flag = False
        for j in misue:
            if i['group_day'].date() == j['group_day']:
                flag = True
                break
        if flag:
            pipecountsumdic["issue"].append(round(j['issue__sum__kg'], 2))
            #issue for 
            issue += j['issue__sum__kg']
        else:
            pipecountsumdic["issue"].append(0.0)
            issue += 0
        #issue of shift1 for the given viewformat appended in the pipecountsumdic
        flag1=False
        for y1 in  misue_shift1:
            print("################### group_day", i['group_day'])
            print("########+++++++++++", y1['group_day'])
            if i['group_day'].date()==y1['group_day']:
                flag1=True
                break
        if flag1:
            pipecountsumdic["date"][m]["shift1"]=[]
            pipecountsumdic["date"][m]["shift1"].append(y1['issue__sum__kg'])

        else:
            pipecountsumdic["date"][m]["shift1"]=[]
            pipecountsumdic["date"][m]["shift1"].append(0.0)
            #issue of shift2 for the given viewformat appended in the pipecountsumdic
        flag2=False
        for y2 in  misue_shift2:
            if i['group_day'].date()==y2['group_day']:
                flag2=True
                break
        if flag2:
            pipecountsumdic["date"][m]["shift2"]=[]
            pipecountsumdic["date"][m]["shift2"].append(y2['issue__sum__kg'])
        else:
            pipecountsumdic["date"][m]["shift2"]=[]
            pipecountsumdic["date"][m]["shift2"].append(0.0)
        if machine_total_shift==3:
            flag3=False
            for y3 in misue_shift3:
                if i['group_day'].date()==y3['group_day']:
                    flag3=True
                    break
            if flag3:
                pipecountsumdic["date"][m]["shift3"]=[]
                pipecountsumdic["date"][m]["shift3"].append(y1['issue__sum__kg'])
            else:
                pipecountsumdic["date"][m]["shift3"]=[]
                pipecountsumdic["date"][m]["shift3"].append(0.0)

        flag11=False

        for w1 in output_shift1:
            if i['group_day']==w1['group_day']:
                flag11=True
                break
        if flag11:
            pipecountsumdic["date"][m]["shift1"].append(w1["weight__sum__kg"])
        else:
            pipecountsumdic["date"][m]["shift1"].append(0.0)

        flag12=False    
        for w2 in output_shift2:
            if i['group_day']==w2['group_day']:
                flag12 = True
                break
        if flag12:
            pipecountsumdic["date"][m]["shift2"].append(w2["weight__sum__kg"])
        else:
            pipecountsumdic["date"][m]["shift2"].append(0.0)

        if machine_total_shift==3:
            flag13=False
            for w3 in output_shift3:
                if i['group_day']==w3['group_day']:
                    flag13=True
                    break
            if flag13:
                pipecountsumdic["date"][m]["shift3"].append(w3["weight__sum__kg"])
            else:
                pipecountsumdic["date"][m]["shift3"].append(0.0)



        pipecountsumdic["scrap"].append(
            round(pipecountsumdic["issue"][jindex] - pipecountsumdic["weight"][jindex], 2))
        #scrap generated of shifts for the given viewformat appended in the pipesumdic's date key
        pipecountsumdic["date"][m]["shift1"].append(pipecountsumdic["date"][m]["shift1"][1]-pipecountsumdic["date"][m]["shift1"][0])
        pipecountsumdic["date"][m]["shift2"].append(pipecountsumdic["date"][m]["shift2"][1]-pipecountsumdic["date"][m]["shift2"][0])
        if machine_total_shift==3:
            pipecountsumdic["date"][m]["shift3"].append(pipecountsumdic["date"][m]["shift3"][1]-pipecountsumdic["date"][m]["shift3"][0])

        scrap += pipecountsumdic["scrap"][jindex]
        pipecountsumdic["ratio"].append(round(pipecountsumdic["scrap"][jindex] / pipecountsumdic["issue"][jindex], 2) if float(pipecountsumdic["issue"][jindex]) != 0 else 0)
        #ratio generated for each shift for the given viewformat appende into pipecountsumdic's date key
        r11=pipecountsumdic["date"][m]["shift1"][2]
        r12=pipecountsumdic["date"][m]["shift1"][1]
        pipecountsumdic["date"][m]["shift1"].append((pipecountsumdic["date"][m]["shift1"][2]/pipecountsumdic["date"][m]["shift1"][1]) if float(pipecountsumdic["date"][m]["shift1"][1]) != 0 else 0)
        pipecountsumdic["date"][m]["shift2"].append((pipecountsumdic["date"][m]["shift2"][2]/pipecountsumdic["date"][m]["shift2"][1]) if float(pipecountsumdic["date"][m]["shift2"][1]) != 0 else 0)
        if machine_total_shift==3:
            pipecountsumdic["date"][m]["shift3"].append((pipecountsumdic["date"][m]["shift3"][2]/pipecountsumdic["date"][m]["shift3"][1]) if float(pipecountsumdic["date"][m]["shift3"][1]) != 0 else 0)
        index += 1
        jindex += 1
        print("pipecountsumdic______________", pipecountsumdic)
        if (viewformat == 'Month' or viewformat == 'Week') and index == 7:
            jindex += 3
            pipecountsumdic["date"].append("Total")
            pipecountsumdic["weight"].append(weight)
            pipecountsumdic["issue"].append(issue)
            pipecountsumdic["scrap"].append(scrap)
            pipecountsumdic["ratio"].append(
                round(scrap / issue, 2) if issue != 0 else 0)

            pipecountsumdic["date"].append("")
            pipecountsumdic["weight"].append('')
            pipecountsumdic["issue"].append('')
            pipecountsumdic["scrap"].append('')
            pipecountsumdic["ratio"].append('')
            pipecountsumdic["date"].append("")
            pipecountsumdic["weight"].append('')
            pipecountsumdic["issue"].append('')
            pipecountsumdic["scrap"].append('')
            pipecountsumdic["ratio"].append('')
            index = 0
            issue = weight = scrap = 0
            m += 4
        else:
            m += 1
    if ((viewformat == 'Month' or viewformat == 'Week') and index != 7) or ((viewformat == 'Day' or viewformat == 'Year' or viewformat == 'Quarter')):
        pipecountsumdic["date"].append("Total")
        pipecountsumdic["weight"].append(weight)
        pipecountsumdic["issue"].append(issue)
        pipecountsumdic["scrap"].append(scrap)
        pipecountsumdic["ratio"].append(
            round(scrap / issue, 2) if issue != 0 else 0)

    
    return 'summary_4_all.html', {
        "machine": machine,
        "startdate": startdate,
        "enddate": enddate,
        "pipecountsum": zip(
            pipecountsumdic["date"],
            pipecountsumdic["issue"],
            pipecountsumdic["weight"],
            pipecountsumdic["scrap"],
            pipecountsumdic["ratio"]
        ),
        "viewformat": viewformat,
        "summary_name": "MIS 4_2 : MATERIAL RECONCILIATION REPORT"
    }