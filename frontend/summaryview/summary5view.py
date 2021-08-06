import datetime
import pytz
from datetime import timedelta
from django.utils import timezone

from django.db.models import Sum, Avg, Count, F, ExpressionWrapper, FloatField
from django.db.models.functions import TruncDay, TruncYear, TruncQuarter, TruncMonth, TruncWeek


from api.models import *


def summary_5_view(user, startdate, enddate, viewformat):
    machine = Machine.objects.filter(user=user)
    machine_list = []
    for i in machine:
        machine_list.append(i.toDic()["machine_id"])

    starttimestamp = int(datetime.datetime.strptime(
        str(startdate) + ' 00:00:00', "%Y-%m-%d %H:%M:%S").timestamp())
    endtimestamp = int(datetime.datetime.strptime(
        str(enddate) + ' 23:59:59', "%Y-%m-%d %H:%M:%S").timestamp())

    if viewformat == 'Day' or viewformat == 'Week' or viewformat == 'Month':
        weightgainloss = PipeDataProcessed.objects.annotate(group_day=TruncDay('site_time')).values('group_day').annotate(weightloss__sum__kg=ExpressionWrapper(Sum(F('weightloss') * 1.0 / 1000), output_field=FloatField()), weightgain__sum__kg=ExpressionWrapper(Sum(F('weightgain') * 1.0 / 1000), output_field=FloatField(
        )), weight__sum__kg=ExpressionWrapper(Sum(F('weight') * 1.0 / 1000), output_field=FloatField()), weight_net__sum__kg=ExpressionWrapper(Sum(F('weightgain') + F('weightloss')) * 1.0 / 1000, output_field=FloatField())).filter(timestamp__gte=starttimestamp, timestamp__lte=endtimestamp, machine_id__in=machine_list)
        weightgainloss.query.clear_ordering(force_empty=True)
    elif viewformat == 'Quarter' or viewformat == 'Year':
        weightgainloss = PipeDataProcessed.objects.annotate(group_day=TruncMonth('site_time')).values('group_day').annotate(weightloss__sum__kg=ExpressionWrapper(Sum(F('weightloss') * 1.0 / 1000), output_field=FloatField()), weightgain__sum__kg=ExpressionWrapper(Sum(F('weightgain') * 1.0 / 1000), output_field=FloatField(
        )), weight__sum__kg=ExpressionWrapper(Sum(F('weight') * 1.0 / 1000), output_field=FloatField()), weight_net__sum__kg=ExpressionWrapper(Sum(F('weightgain') + F('weightloss')) * 1.0 / 1000, output_field=FloatField())).filter(timestamp__gte=starttimestamp, timestamp__lte=endtimestamp, machine_id__in=machine_list)
        weightgainloss.query.clear_ordering(force_empty=True)
    else:
        raise Exception("Please select proper format")

    print(starttimestamp, endtimestamp, viewformat)

    weightgainlossdic = {
        "weightdate": [],
        "weight": [],
        "weightgain": [],
        "weightloss": [],
        "netgain": []
    }

    weight = weightgain = weightloss = netgain = 0
    index = 0
    for i in weightgainloss:
        if viewformat == 'Day' or viewformat == 'Week' or viewformat == 'Month':
            weightgainlossdic["weightdate"].append(
                i['group_day'].strftime("%d/%m/%Y %A"))
        else:
            weightgainlossdic["weightdate"].append(
                i['group_day'].strftime("%B, %Y"))
        weightgainlossdic["weight"].append(
            round(i['weight__sum__kg'], 2) if i['weight__sum__kg'] != None else 0)
        weight += i['weight__sum__kg']
        weightgainlossdic["weightloss"].append(
            round(i['weightloss__sum__kg'], 2) if i['weightloss__sum__kg'] != None else 0)
        weightloss += i['weightloss__sum__kg']
        weightgainlossdic["weightgain"].append(
            round(i['weightgain__sum__kg'], 2) if i['weightgain__sum__kg'] != None else 0)
        weightgain += i['weightgain__sum__kg']
        weightgainlossdic["netgain"].append(
            round(i['weight_net__sum__kg'], 2) if i['weight_net__sum__kg'] != None else 0)
        netgain += i['weight_net__sum__kg']
        index += 1
        if (viewformat == 'Month' or viewformat == 'Week') and index == 7:
            weightgainlossdic["weightdate"].append("Total")
            weightgainlossdic["weight"].append(
                0 if weight == None else round(weight, 2))
            weightgainlossdic["weightgain"].append(
                0 if weightgain == None else round(weightgain, 2))
            weightgainlossdic["weightloss"].append(
                0 if weightloss == None else round(weightloss, 2))
            weightgainlossdic["netgain"].append(
                0 if netgain == None else round(netgain, 2))
            
            weightgainlossdic["weightdate"].append("%")
            weightgainlossdic["weight"].append('')
            weightgainlossdic["weightgain"].append(
                0 if weightgain == None or weight == 0 else round((weightgain / weight) * 100, 2))
            weightgainlossdic["weightloss"].append(
                0 if weightloss == None or weight == 0 else round((weightloss / weight) * 100, 2))
            weightgainlossdic["netgain"].append(
                0 if netgain == None or netgain == 0 else round((netgain / weight) * 100, 2))

            weightgainlossdic["weightdate"].append("")
            weightgainlossdic["weight"].append('')
            weightgainlossdic["weightgain"].append('')
            weightgainlossdic["weightloss"].append('')
            weightgainlossdic["netgain"].append('')

            weightgainlossdic["weightdate"].append("")
            weightgainlossdic["weight"].append('')
            weightgainlossdic["weightgain"].append('')
            weightgainlossdic["weightloss"].append('')
            weightgainlossdic["netgain"].append('')

            weight = weightgain = weightloss = netgain = 0
            index = 0

    if ((viewformat == 'Month' or viewformat == 'Week') and index != 7) or ((viewformat == 'Day' or viewformat == 'Year' or viewformat == 'Quarter')):
        weightgainlossdic["weightdate"].append("Total")
        weightgainlossdic["weight"].append(0 if weight == None else round(weight, 2))
        weightgainlossdic["weightgain"].append(
            0 if weightgain == None else round(weightgain, 2))
        weightgainlossdic["weightloss"].append(
            0 if weightloss == None else round(weightloss, 2))
        weightgainlossdic["netgain"].append(
            0 if netgain == None else round(netgain, 2))

        weightgainlossdic["weightdate"].append("%")
        weightgainlossdic["weight"].append('')
        weightgainlossdic["weightgain"].append(
            0 if weightgain == None or weightgain == 0 else round((weightgain / weight) * 100, 2))
        weightgainlossdic["weightloss"].append(
            0 if weightloss == None or weightloss == 0 else round((weightloss / weight) * 100, 2))
        weightgainlossdic["netgain"].append(
            0 if netgain == None or netgain == 0 else round((netgain / weight) * 100, 2))

    return 'summary_5.html', {
        "machine": machine,
        "startdate": startdate,
        "enddate": enddate,
        "viewformat": viewformat,
        "summary_name": "MIS 5: TOTAL OUTPUT VS WEIGHTGAIN / LOSS",
        "pipecountsum": zip(
            weightgainlossdic["weightdate"],
            weightgainlossdic["weight"],
            weightgainlossdic["weightgain"],
            weightgainlossdic["weightloss"],
            weightgainlossdic["netgain"]
        )
    }
