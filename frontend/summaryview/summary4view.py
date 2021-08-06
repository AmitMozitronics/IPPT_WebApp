import datetime
import pytz
from datetime import timedelta
from django.utils import timezone

from django.db.models import Sum, Avg, Count, F, ExpressionWrapper, FloatField
from django.db.models.functions import TruncDay, TruncMonth

from api.models import *


def summary_4_view(request):
    machine = Machine.objects.filter(user=request.user)
    machine_list = []
    for i in machine:
        machine_list.append(i.toDic()["machine_id"])
    shiftdate = request.GET.get('shiftdate')
    if shiftdate == None:
        shiftdate = str(timezone.localdate())
    # print(shiftdate)
    try:
        MetarialIssueShift.objects.create(
            user=request.user, shift_date=shiftdate)
    except:
        pass
    try:
        metarialissuedic = MetarialIssueShift.objects.get(
            user=request.user, shift_date=shiftdate).toDic()
        metarialissuedic["shift_1"] = metarialissuedic["shift_1"] / 1000
        metarialissuedic["shift_2"] = metarialissuedic["shift_2"] / 1000
        metarialissuedic["shift_3"] = metarialissuedic["shift_3"] / 1000
    except:
        pass
    try:
        shiftdatestart = datetime.datetime.strptime(
            shiftdate + ' 07:00:00', "%Y-%m-%d %H:%M:%S")
        shiftdateend = datetime.datetime.strptime(
            shiftdate + ' 06:59:59', "%Y-%m-%d %H:%M:%S") + timedelta(days=1)
        starttimestamp = int(shiftdatestart.timestamp())
        endtimestamp = int(shiftdateend.timestamp())
        pipemetarialscrap = []
        pipemetarialscrap.append(PipeDataProcessed.objects.filter(timestamp__gte=starttimestamp, timestamp__lte=endtimestamp, machine_id__in=machine_list,
                                                                  shift='1').aggregate(weight__sum__kg=ExpressionWrapper(Sum(F('weight') * 1.0 / 1000), output_field=FloatField())))
        pipemetarialscrap[0]["issue"] = metarialissuedic["shift_1"]
        pipemetarialscrap[0]["scrap"] = metarialissuedic["shift_1"] - \
            pipemetarialscrap[0]["weight__sum__kg"] if pipemetarialscrap[0]["weight__sum__kg"] != None else 0
        pipemetarialscrap[0]["ratio"] = pipemetarialscrap[0]["scrap"] / \
            pipemetarialscrap[0]["issue"]
        pipemetarialscrap.append(PipeDataProcessed.objects.filter(timestamp__gte=starttimestamp, timestamp__lte=endtimestamp, machine_id__in=machine_list,
                                                                  shift='2').aggregate(weight__sum__kg=ExpressionWrapper(Sum(F('weight') * 1.0 / 1000), output_field=FloatField())))
        pipemetarialscrap[1]["issue"] = metarialissuedic["shift_2"]
        pipemetarialscrap[1]["scrap"] = metarialissuedic["shift_2"] - \
            pipemetarialscrap[1]["weight__sum__kg"] if pipemetarialscrap[1]["weight__sum__kg"] != None else 0
        pipemetarialscrap[1]["ratio"] = pipemetarialscrap[1]["scrap"] / \
            pipemetarialscrap[1]["issue"]
        pipemetarialscrap.append(PipeDataProcessed.objects.filter(timestamp__gte=starttimestamp, timestamp__lte=endtimestamp, machine_id__in=machine_list,
                                                                  shift='3').aggregate(weight__sum__kg=ExpressionWrapper(Sum(F('weight') * 1.0 / 1000), output_field=FloatField())))
        pipemetarialscrap[2]["issue"] = metarialissuedic["shift_3"]
        pipemetarialscrap[2]["scrap"] = metarialissuedic["shift_3"] - \
            pipemetarialscrap[2]["weight__sum__kg"] if pipemetarialscrap[2]["weight__sum__kg"] != None else 0
        pipemetarialscrap[2]["ratio"] = pipemetarialscrap[2]["scrap"] / \
            pipemetarialscrap[2]["issue"]
        pipemetarialscrap.append(PipeDataProcessed.objects.filter(timestamp__gte=starttimestamp, timestamp__lte=endtimestamp, machine_id__in=machine_list).aggregate(
            weight__sum__kg=ExpressionWrapper(Sum(F('weight') * 1.0 / 1000), output_field=FloatField())))
        pipemetarialscrap[3]["issue"] = metarialissuedic["shift_3"] + \
            metarialissuedic["shift_2"] + metarialissuedic["shift_1"]
        pipemetarialscrap[3]["scrap"] = pipemetarialscrap[3]["issue"] - \
            pipemetarialscrap[3]["weight__sum__kg"] if pipemetarialscrap[3]["weight__sum__kg"] != None else 0
        pipemetarialscrap[3]["ratio"] = pipemetarialscrap[3]["scrap"] / \
            pipemetarialscrap[3]["issue"]
    except Exception as ex:
        print(ex)
    print(starttimestamp, endtimestamp)
    # print(pipemetarialscrap)

    try:
        metarialissuedic["shift_1"] = int(metarialissuedic["shift_1"] * 1000)
        metarialissuedic["shift_2"] = int(metarialissuedic["shift_2"] * 1000)
        metarialissuedic["shift_3"] = int(metarialissuedic["shift_3"] * 1000)
    except:
        metarialissuedic = None
    summary_4_dic = {"machine": machine, "summary_name": "MIS 4 : MATERIAL RECONCILIATION REPORT", "shiftdate": shiftdate,
                     "shiftdatestart": shiftdatestart, "shiftdateend": shiftdateend, "metarialissuedic": metarialissuedic, "pipemetarialscrap": pipemetarialscrap}
    return 'summary_4.html', summary_4_dic

















def summary_4_view_all(user, startdate, enddate, viewformat):
    machine = Machine.objects.filter(user=user)
    machine_list = []
    for i in machine:
        machine_list.append(i.toDic()["machine_id"])

    starttimestamp = int(datetime.datetime.strptime(
        str(startdate) + ' 00:00:00', "%Y-%m-%d %H:%M:%S").timestamp())
    endtimestamp = int(datetime.datetime.strptime(
        str(enddate) + ' 23:59:59', "%Y-%m-%d %H:%M:%S").timestamp())

    if viewformat == 'Day' or viewformat == 'Week' or viewformat == 'Month':
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

    elif viewformat == 'Quarter' or viewformat == 'Year':
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
    else:
        raise Exception("Please select proper format")

    print(starttimestamp, endtimestamp, viewformat)

    pipecountsumdic = {
        "date": [],
        "issue": [],
        "weight": [],
        "scrap": [],
        "ratio": [],
    }

    issue = weight = scrap = 0
    index = 0
    jindex = 0
    for i in output:
        if viewformat == 'Day' or viewformat == 'Week' or viewformat == 'Month':
            pipecountsumdic["date"].append(
                i['group_day'].strftime("%d/%m/%Y %A"))
        else:
            pipecountsumdic["date"].append(
                i['group_day'].strftime("%B, %Y"))
        pipecountsumdic["weight"].append(round(i['weight__sum__kg'], 2))
        weight += i['weight__sum__kg']
        flag = False
        for j in misue:
            if i['group_day'].date() == j['group_day']:
                flag = True
                break
        if flag:
            pipecountsumdic["issue"].append(round(j['issue__sum__kg'], 2))
            issue += j['issue__sum__kg']
        else:
            pipecountsumdic["issue"].append(0.0)
            issue += 0
        pipecountsumdic["scrap"].append(
            round(pipecountsumdic["issue"][jindex] - pipecountsumdic["weight"][jindex], 2))
        scrap += pipecountsumdic["scrap"][jindex]
        pipecountsumdic["ratio"].append(round(pipecountsumdic["scrap"][jindex] / pipecountsumdic["issue"][jindex], 2) if float(pipecountsumdic["issue"][jindex]) != 0 else 0)
        index += 1
        jindex += 1
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
        "summary_name": "MIS 4 : MATERIAL RECONCILIATION REPORT"
    }
