import datetime
import pytz
from datetime import timedelta
from django.utils import timezone as util_timezone

from django.db.models import Sum, Avg, Count, F, ExpressionWrapper, FloatField
from django.db.models.functions import TruncDay

from api.models import *
from pytz import timezone

def summary_8_view(request):
    startdate = request.GET.get('startdate')
    enddate = request.GET.get('enddate')
    basic_metarial = request.GET.get('basic_metarial')
    standard_type_classification = request.GET.get(
        'standard_type_classification')
    pressure_type_specification = request.GET.get(
        'pressure_type_specification')
    length = request.GET.get('length')
    outer_diameter = request.GET.get('outer_diameter')
    outer_diameter_unit = request.GET.get('outer_diameter_unit')
    length_unit = 'M'
    machine = Machine.objects.filter(user=request.user)
    machine_list = []
    for i in machine:
        machine_list.append(i.toDic()["machine_id"])
       #----Souren---20/04/21-------#    
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
    if(startdate == None and enddate == None):
        timezone_localtime = util_timezone.localtime(util_timezone.now())
        enddate = startdate = timezone_localtime.strftime('%Y-%m-%d')  
        starttime = starttime
        endtime = endtime    
    if (shift1_time_duration+shift2_time_duration+shift3_time_duration==24.00):
        enddate = (datetime.datetime.strptime(enddate, '%Y-%m-%d')+timedelta(days=1)).strftime('%Y-%m-%d')
            
    basic_metarial_list = BasicMetarialStandard.objects.values_list(
        'basic_metarial', flat=True).distinct().order_by('basic_metarial')
    standard_type_classification_list = StandardTypeClassification.objects.values_list(
        'standard_type_classification', flat=True).distinct().order_by('standard_type_classification')
    pressure_type_specification_list = PressureTypeSpecification.objects.values_list(
        'pressure_type_specification', flat=True).distinct().order_by('pressure_type_specification')
    length_list = PipeLength.objects.values_list(
        'length', flat=True).distinct().order_by('length')
    outer_diameter_list = PipeOuterDiameter.objects.values_list(
        'outer_diameter', flat=True).distinct().order_by('outer_diameter')
    outer_diameter_unit_list = Unit.objects.values_list(
        'unit', flat=True).distinct().order_by('unit')

    local_zone = MachineTimeZone.objects.get(machine_id=machine_list[0]).machine_timezone
    try:
        starttimestamp = int(timezone(local_zone).localize(datetime.datetime.strptime(
            startdate + ' ' + str(starttime), "%Y-%m-%d %H:%M:%S")).timestamp())
        endtimestamp = int(timezone(local_zone).localize(datetime.datetime.strptime(
            enddate + ' ' + str(endtime), "%Y-%m-%d %H:%M:%S")).timestamp())
        productwisereport = PipeDataProcessed.objects.annotate(
            group_day=TruncDay('site_time')).values('group_day').annotate(
                weight__sum__kg=ExpressionWrapper(Sum(F('weight') * 1.0 / 1000), 
                output_field=FloatField()), 
                weight__count=Count('weight'), 
                length__sum=Sum('length'), 
                weight__avg__kg=ExpressionWrapper(Avg(F('weight') * 1.0 / 1000), 
                output_field=FloatField()), 
                min_weight__sum__kg=ExpressionWrapper(Sum(F('minweight') * 1.0 / 1000), 
                output_field=FloatField()), 
                max_weight__sum__kg=ExpressionWrapper(Sum(F('maxweight') * 1.0 / 1000), 
                output_field=FloatField()), 
                weight_gain__sum__kg=ExpressionWrapper(Sum(F('weightgain') * 1.0 / 1000), 
                output_field=FloatField()), 
                weigt_loss__sum__kg=ExpressionWrapper(Sum(F('weightloss') * 1.0 / 1000), 
                output_field=FloatField()), 
                netgain__sum__kg=ExpressionWrapper(Sum(F('weightgain') + F('weightloss')) * 1.0 / 1000, 
                output_field=FloatField())).filter(
                    timestamp__gte=starttimestamp, 
                    timestamp__lte=endtimestamp, 
                    machine_id__in=machine_list, 
                    basic_metarial=basic_metarial, 
                    standard_type_classification=standard_type_classification, 
                    pressure_type_specification=pressure_type_specification, 
                    length=float(length), length_unit=length_unit,
                    outer_diameter=float(outer_diameter),
                    outer_diameter_unit=outer_diameter_unit
                    )
        productwisereport.query.clear_ordering(force_empty=True)
        wrongmessege = None
    except Exception as ex:
        print(ex)
        starttimestamp = None
        endtimestamp = None
        productwisereport = None
        if(startdate == None and enddate == None):
            wrongmessege = None
        else:
            wrongmessege = {"message": str(ex)}

    print(starttimestamp, endtimestamp)
    summary8dic = {
        "machine": machine,
        "summary_name": "MIS 8 : PRODUCT WISE ANALYSIS REPORT",
        "startdate": startdate,
        "enddate": enddate,
        "productwisereport": productwisereport,
        "basic_metarial_list": basic_metarial_list,
        "standard_type_classification_list": standard_type_classification_list,
        "pressure_type_specification_list": pressure_type_specification_list,
        "length_list": length_list,
        "outer_diameter_list": outer_diameter_list,
        "outer_diameter_unit_list": outer_diameter_unit_list,
        "wrongmessege": wrongmessege,
        "standard_type_classification": standard_type_classification,
        "pressure_type_specification": pressure_type_specification,
        "length": length,
        "basic_metarial": basic_metarial,
        "outer_diameter": outer_diameter,
        "outer_diameter_unit": outer_diameter_unit
    }
    # print(summary8dic)
    return 'summary_8.html', summary8dic
