import datetime
import pytz
from datetime import timedelta
from django.utils import timezone

from django.db.models import Sum, Avg, Count, F, ExpressionWrapper, FloatField
from django.db.models.functions import TruncDay

from api.models import *


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
    try:
        starttimestamp = int(datetime.datetime.strptime(
            startdate + ' 00:00:00', "%Y-%m-%d %H:%M:%S").timestamp())
        endtimestamp = int(datetime.datetime.strptime(
            enddate + ' 23:59:59', "%Y-%m-%d %H:%M:%S").timestamp())
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
