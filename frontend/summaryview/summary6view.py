import datetime
import pytz
from datetime import timedelta
from django.utils import timezone

from django.db.models import Sum, Avg, Count, F, ExpressionWrapper, BigIntegerField
from django.db.models.functions import TruncDay, TruncYear, TruncQuarter, TruncMonth, TruncWeek


from api.models import *


def summary_6_view(user, startdate, enddate, viewformat):
    machine = Machine.objects.filter(user=user)
    machine_list = []
    for i in machine:
        machine_list.append(i.toDic()["machine_id"])

    starttimestamp = int(datetime.datetime.strptime(
        str(startdate) + ' 00:00:00', "%Y-%m-%d %H:%M:%S").timestamp())
    endtimestamp = int(datetime.datetime.strptime(
        str(enddate) + ' 23:59:59', "%Y-%m-%d %H:%M:%S").timestamp())

    if viewformat == 'Day' or viewformat == 'Week' or viewformat == 'Month':
        downtime = PipeShiftDuration.objects.annotate(group_day=TruncDay('shift_date')).values('group_day').annotate(shift_1_downtime__sum=ExpressionWrapper(Sum('shift_1_downtime'), output_field=BigIntegerField()), shift_2_downtime__sum=ExpressionWrapper(
            Sum('shift_2_downtime'), output_field=BigIntegerField()), shift_3_downtime__sum=ExpressionWrapper(Sum('shift_3_downtime'), output_field=BigIntegerField())).filter(shift_date__range=(startdate, enddate), user=user)
    elif viewformat == 'Quarter' or viewformat == 'Year':
        downtime = PipeShiftDuration.objects.annotate(group_day=TruncMonth('shift_date')).values('group_day').annotate(shift_1_downtime__sum=ExpressionWrapper(Sum('shift_1_downtime'), output_field=BigIntegerField()), shift_2_downtime__sum=ExpressionWrapper(
            Sum('shift_2_downtime'), output_field=BigIntegerField()), shift_3_downtime__sum=ExpressionWrapper(Sum('shift_3_downtime'), output_field=BigIntegerField())).filter(shift_date__range=(startdate, enddate), user=user)

    print(startdate, enddate, viewformat)

    downtimedic = {
        "downdate": [],
        "down1": [],
        "down2": [],
        "down3": []
    }
    for i in downtime:
        i['shift_1_downtime__sum'] = timedelta(
            microseconds=i['shift_1_downtime__sum'])
        i['shift_2_downtime__sum'] = timedelta(
            microseconds=i['shift_2_downtime__sum'])
        i['shift_3_downtime__sum'] = timedelta(
            microseconds=i['shift_3_downtime__sum'])

    down1 = down2 = down3 = timedelta(seconds=0)
    index = 0
    for i in downtime:
        if viewformat == 'Day' or viewformat == 'Week' or viewformat == 'Month':
            downtimedic["downdate"].append(
                i['group_day'].strftime("%d/%m/%Y %A"))
        else:
            downtimedic["downdate"].append(i['group_day'].strftime("%B, %Y"))
        down1 += i['shift_1_downtime__sum']
        downtimedic["down1"].append(
            round(int(i['shift_1_downtime__sum'].total_seconds()) / 3600, 2))
        down2 += i['shift_2_downtime__sum']
        downtimedic["down2"].append(
            round(int(i['shift_2_downtime__sum'].total_seconds()) / 3600, 2))
        down3 += i['shift_3_downtime__sum']
        downtimedic["down3"].append(
            round(int(i['shift_3_downtime__sum'].total_seconds()) / 3600, 2))
        index += 1
        if (viewformat == 'Month' or viewformat == 'Week') and index == 7:
            downtimedic["downdate"].append("Total")
            downtimedic["down1"].append(
                round(int(down1.total_seconds()) / 3600, 2))
            downtimedic["down2"].append(
                round(int(down2.total_seconds()) / 3600, 2))
            downtimedic["down3"].append(
                round(int(down3.total_seconds()) / 3600, 2))

            downtimedic["downdate"].append("")
            downtimedic["down1"].append('')
            downtimedic["down2"].append('')
            downtimedic["down3"].append('')
            downtimedic["downdate"].append("")
            downtimedic["down1"].append('')
            downtimedic["down2"].append('')
            downtimedic["down3"].append('')
            down1 = down2 = down3 = timedelta(seconds=0)
            index = 0

    if ((viewformat == 'Month' or viewformat == 'Week') and index != 7) or ((viewformat == 'Day' or viewformat == 'Year' or viewformat == 'Quarter')):
        downtimedic["downdate"].append("Total")
        downtimedic["down1"].append(
            round(int(down1.total_seconds()) / 3600, 2))
        downtimedic["down2"].append(
            round(int(down2.total_seconds()) / 3600, 2))
        downtimedic["down3"].append(
            round(int(down3.total_seconds()) / 3600, 2))

    return 'summary_6.html', {
        "machine": machine,
        "startdate": startdate,
        "enddate": enddate,
        "viewformat": viewformat,
        "summary_name": "MIS 6: DOWN TIME SUMMARY",
        "pipecountsum": zip(
            downtimedic["downdate"],
            downtimedic["down1"],
            downtimedic["down2"],
            downtimedic["down3"]
        )
    }
