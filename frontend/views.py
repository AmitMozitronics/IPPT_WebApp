from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_protect

import datetime, pytz
from datetime import timedelta
from django.utils import timezone

from django.contrib.auth.models import User

from django.contrib.gis.geoip2 import GeoIP2
from django.views import View




import xlwt

from api.models import *

from .summaryview.summary1view import summary_1_view
from .summaryview.summary2view import summary_2_view
from .summaryview.summary3view import summary_3_view
from .summaryview.summary4view import summary_4_view, summary_4_view_all
from .summaryview.summary5view import summary_5_view
from .summaryview.summary6view import summary_6_view
from .summaryview.summary7view import summary_7_view
from .summaryview.summary8view import summary_8_view
from .summaryview.home_view import excel_response, home_response

from .summaryview_v2 import home_view_v2, production_summary_result_v2, size_wise_output_v2,pipe_count_summary_v2,material_reconsiliation_report_v2, total_output_vs_weight_gain_or_loss_v2, downtime_summary_v2
from .summaryview_v2 import size_wise_length_v2, product_wise_analysis_report_v2


# Create your views here.
def showUserTime(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    g = GeoIP2()
    ip_details = g.city(ip)
    user_time_zone = ip_details['time_zone']
    return user_time_zone   
@login_required(login_url='/')
def home(request):
    if request.user.is_superuser:
        return redirect('/admin')
    machine = Machine.objects.get(user=request.user)
    if machine.machine_version == 2:
        url = "http://pipetrackerlive.com/v2/"
        return redirect(url)
    htmlfile, homedic = home_response(request)
    return render(request, 'frontend/' + htmlfile, homedic)

@login_required(login_url = '/')
def homev2(request):
    if request.user.is_superuser:
        return redirect('/admin')
    htmlfile, homedic = home_view_v2.home_response(request)
    return render(request, 'frontend_v2/' + htmlfile, homedic)

@login_required(login_url = '/')
def home_xls(request):
    t = showUserTime(request)
    #return HttpResponse(t)
    if request.user.is_superuser:
        return redirect('/admin')
    return excel_response(request)

@login_required(login_url = '/')
def download_excel_report(request):
    if request.user.is_superuser:
        return redirect('/admin')
    return home_view_v2.excel_response(request)

@login_required(login_url='/')
def summary(request):
    if request.user.is_superuser:
        return redirect('/admin')
    return render(request, 'frontend/summary.html', {"summary_name": "MIS SUMMARY REPORT", "machine": Machine.objects.filter(user=request.user)})

@login_required(login_url = '/')
def summaryv2(request):
    if request.user.is_superuser:
        return redirect('/admin')
    return render(request, 'frontend_v2/summary.html', {"summary_name": "MIS SUMMARY REPORT", "machine": Machine.objects.filter(user=request.user)})




@login_required(login_url='/')
def summary_1(request):
    if request.user.is_superuser:
        return redirect('/admin')
    htmlfile, summary_1_dic = summary_1_view(request)
    logged_in_user_id = request.user.id
    machine = Machine.objects.get(user = logged_in_user_id)
    machine_id = Machine.objects.get(machine_id = machine.machine_id)
    #machine_details = Machine.objects.values().filter(machine_id=machine_id)
    #return HttpResponse(machine_id.shift1_start_time)
    summary_1_dic['md'] = machine_id
    summary_1_dic['mdt'] = 'Asia/Kolkata'
    return render(request, 'frontend/' + htmlfile, summary_1_dic)

@login_required(login_url = '/')
def production_summary_v2(request):
    if request.user.is_superuser:
        return redirect('/admin')
    htmlfile,summary_1_dic = production_summary_result_v2.summary_1_view(request)
    logged_in_user_id = request.user.id
    machine = Machine.objects.get(user = logged_in_user_id)
    machine_id = Machine.objects.get(machine_id = machine.machine_id)
    summary_1_dic['md'] = machine_id
    
    return render(request, 'frontend_v2/' + htmlfile, summary_1_dic)


@login_required(login_url='/')
def summary_2(request):
    if request.user.is_superuser:
        return redirect('/admin')
    htmlfile, summary2dic = summary_2_view(request)
    return render(request, 'frontend/' + htmlfile, summary2dic)

#MIS 2
#Size wise report
@login_required(login_url = '/')
def size_wise_report_v2(request):
    if request.user.is_superuser:
        return redirect('/admin')
    htmlfile, summary2dic = size_wise_output_v2.summary_2_view(request)
    return render(request, 'frontend_v2/' + htmlfile, summary2dic)


@login_required(login_url='/')
def summary_4(request):
    if request.user.is_superuser:
        return redirect('/admin')
    htmlfile, summary_4_dic = summary_4_view(request)
    return render(request, 'frontend/' + htmlfile, summary_4_dic)

@login_required(login_url = '/')
def summary_4_v2(request):
    if request.user.is_superuser:
        return redirect('/admin')
    htmlfile, summary_4_dic = material_reconsiliation_report_v2.summary_4_view(request)
    return render(request, 'frontend_v2/' + htmlfile, summary_4_dic)


@login_required(login_url='/')
def summary_7(request):
    if request.user.is_superuser:
        return redirect('/admin')
    htmlfile, summary7dic = summary_7_view(request)
    return render(request, 'frontend/' + htmlfile, summary7dic)

@login_required(login_url = '/')
def summary_7_v2(request):
    if request.user.is_superuser:
        return redirect('/admin')
    htmlfile, summary7dic = size_wise_length_v2.summary_7_view(request)
    return render(request, 'frontend_v2/'+htmlfile, summary7dic)


@login_required(login_url='/')
def summary_8(request):
    if request.user.is_superuser:
        return redirect('/admin')
    htmlfile, summary8dic = summary_8_view(request)
    return render(request, 'frontend/' + htmlfile, summary8dic)

@login_required(login_url = '/')
def summary_8_v2(request):
    if request.user.is_superuser:
        return redirect('/admin')
    htmlfile, summary8dic = product_wise_analysis_report_v2.summary_8_view(request)
    return render(request, 'frontend_v2/'+htmlfile, summary8dic)







@login_required(login_url='/')
def summary_format(request):
    if request.user.is_superuser:
        return redirect('/admin')
    summarytype = request.GET.get('summarytype')
    if request.method == 'POST':
        # try:
            startdate = request.POST['startdate']
            enddate = request.POST['enddate']
            viewformat = request.POST['viewformat'] 
            if summarytype == 'summary_3':
                htmlfile, summarydic = summary_3_view(request.user, startdate, enddate, viewformat)
            elif summarytype == 'summary_4':
                htmlfile, summarydic = summary_4_view_all(request.user, startdate, enddate, viewformat)
            elif summarytype == 'summary_5':
                htmlfile, summarydic = summary_5_view(request.user, startdate, enddate, viewformat)
            elif summarytype == 'summary_6':
                htmlfile, summarydic = summary_6_view(request.user, startdate, enddate, viewformat)
            else:
                raise Exception("Wrong Summary")
            return render(request, 'frontend/' + htmlfile, summarydic)
        # except Exception as ex:
        #     print(ex)
        #     return render(request, 'frontend/summary_format.html', {"message": str(ex), "summarytype": summarytype})
    return render(request, 'frontend/summary_format.html', {"summarytype": summarytype})



@login_required(login_url = '/')
def summary_format_v2(request):
    if request.user.is_superuser:
        return redirect('/admin')
    summarytype = request.GET.get('summarytype')
    if request.method == 'POST':
        startdate = request.POST['startdate']
        enddate = request.POST['enddate']
        viewformat = request.POST['viewformat']
        if summarytype == 'summary_3':
            htmlfile, summarydic = pipe_count_summary_v2.summary_3_view(request.user, startdate, enddate, viewformat)
            return render(request, 'frontend_v2/' + htmlfile, summarydic)
        elif summarytype == 'summary_4':
            htmlfile, summarydic = material_reconsiliation_report_v2.summary_4_view_all(request.user, startdate, enddate, viewformat)
            return render(request, 'frontend_v2/' + htmlfile, summarydic)
        elif summarytype == 'summary_5':
            htmlfile, summarydic = total_output_vs_weight_gain_or_loss_v2.summary_5_view(request.user, startdate, enddate, viewformat)
            return render(request, 'frontend_v2/' + htmlfile, summarydic)
        elif summarytype == 'summary_6':
            htmlfile, summarydic = downtime_summary_v2.summary_6_view(request.user, startdate, enddate, viewformat)
            return render(request, 'frontend_v2/' + htmlfile, summarydic)

        else:
            return HttpResponse("HELLO")

    return render(request, 'frontend_v2/summary_format.html', {"summarytype": summarytype})



@login_required(login_url = '/')
def pipe_count_summary(request):
    if request.user.is_superuser:
        return redirect('/admin')
    if request.method == "GET":
        return render(request, 'frontend_v2/summary_format.html')
    elif request.method == "POST":
        startdate = request.POST['startdate']
        enddate = request.POST['enddate']
        viewformat = request.POST['viewformat'] 
        htmlfile, summarydic = pipe_count_summary_v2.summary_3_view(request.user, startdate, enddate, viewformat)
        return render(request, 'frontend_v2/' + htmlfile, summarydic)
    return HttpResponse("working")



@csrf_protect
@login_required(login_url='/')
def pipeshiftduration_summary_1(request):
    if request.user.is_superuser:
        return redirect('/admin')
    shiftdate = request.POST['shiftdate']
    shift1 = request.POST['shift1']
    shift2 = request.POST['shift2']
    shift3 = request.POST['shift3']
    shift1 = datetime.timedelta(seconds = int(shift1[0 : 2]) * 3600 + int(shift1[3 : 5]) * 60 )
    shift2 = datetime.timedelta(seconds = int(shift2[0 : 2]) * 3600 + int(shift2[3 : 5]) * 60 )
    shift3 = datetime.timedelta(seconds = int(shift3[0 : 2]) * 3600 + int(shift3[3 : 5]) * 60 )
    shift_1_downtime = datetime.timedelta(minutes=480) - shift1
    shift_2_downtime = datetime.timedelta(minutes=480) - shift2
    shift_3_downtime = datetime.timedelta(minutes=480) - shift3
    try:
        PipeShiftDuration.objects.create(user = request.user, shift_date = shiftdate, shift_1 = shift1, shift_1_downtime = shift_1_downtime, shift_2 = shift2, shift_2_downtime = shift_2_downtime, shift_3 = shift3, shift_3_downtime = shift_3_downtime)  
    except:
        pass
    try:
        PipeShiftDuration.objects.filter(user = request.user, shift_date = shiftdate).update(shift_1 = shift1, shift_1_downtime = shift_1_downtime, shift_2 = shift2, shift_2_downtime = shift_2_downtime, shift_3 = shift3, shift_3_downtime = shift_3_downtime)
    except:
        pass
    return HttpResponseRedirect('summary_1?shiftdate=' + shiftdate)



@csrf_protect
@login_required(login_url='/')
def material_issue_summary_4(request):
    if request.user.is_superuser:
        return redirect('/admin')
    shiftdate = request.POST['shiftdate']
    try:
        shift1 = int(request.POST['shift1'])
        shift2 = int(request.POST['shift2'])
        shift3 = int(request.POST['shift3'])
    except:
        shift1 = 0
        shift2 = 0
        shift3 = 0
    try:
        MetarialIssueShift.objects.create(user = request.user, shift_date = shiftdate, shift_1 = shift1, shift_2 = shift2, shift_3 = shift3)  
    except:
        pass
    try:
        MetarialIssueShift.objects.filter(user = request.user, shift_date = shiftdate).update(shift_1 = shift1, shift_2 = shift2, shift_3 = shift3)
    except Exception as ex:
        print(ex)
    return HttpResponseRedirect('summary_4?shiftdate=' + shiftdate)

@csrf_protect
@login_required(login_url='/')
def material_issue_summary_4_v2(request):
    if request.user.is_superuser:
        return redirect('/admin')
    shiftdate = request.POST['shiftdate']
    try:
        shift1 = int(request.POST['shift1'])
        shift2 = int(request.POST['shift2'])
        shift3 = int(request.POST['shift3'])
    except:
        shift1 = 0
        shift2 = 0
        shift3 = 0
    try:
        MetarialIssueShift.objects.create(user = request.user, shift_date = shiftdate, shift_1 = shift1, shift_2 = shift2, shift_3 = shift3)  
    except:
        pass
    try:
        MetarialIssueShift.objects.filter(user = request.user, shift_date = shiftdate).update(shift_1 = shift1, shift_2 = shift2, shift_3 = shift3)
    except Exception as ex:
        print(ex)
    return HttpResponseRedirect('summary_4_v2?shiftdate=' + shiftdate)


#>-----Souren/25/03/2021-------->
@csrf_protect
@login_required(login_url='/')
def rejectedPipeCountByQc(request):
    print(request.user)
    print("######", request.POST)
    machine_id=Machine.objects.get(user=request.user).machine_id
    shiftdate = request.POST['shiftdate']
    if request.user.is_superuser:
        return redirect('/admin')
    if request.method=='POST':
        try:
            rejected_pipe_shift1 = int(request.POST['shift1reject'])
            rejected_pipe_shift2 = int(request.POST['shift2reject'])
            try:
                rejected_pipe_shift3 = int(request.POST['shift3reject'])
            except:
                rejected_pipe_shift3 = 0

        except:
            rejected_pipe_shift1 = 0
            rejected_pipe_shift2 = 0
            rejected_pipe_shift3 = 0
        print("@@Rejected Pipe Count For each Shift", rejected_pipe_shift1, rejected_pipe_shift2, rejected_pipe_shift3)
        q_rejected = rejectedPipeByQc.objects.filter(machine_id=machine_id, shift_date=shiftdate).exists()
        try:
            if q_rejected is False:
                rejectedPipeByQc.objects.create(machine_id=machine_id, shift_date=shiftdate, rejected_pipe_shift1=rejected_pipe_shift1, rejected_pipe_shift2=rejected_pipe_shift2, rejected_pipe_shift3=rejected_pipe_shift3)
            else:
                rejectedPipeByQc.objects.filter(machine_id=machine_id, shift_date=shiftdate).update(rejected_pipe_shift1=rejected_pipe_shift1, rejected_pipe_shift2=rejected_pipe_shift2, rejected_pipe_shift3=rejected_pipe_shift3)
        except Exception as ex:
            print(ex)
        return HttpResponseRedirect('production_summary_v2/?shiftdate=' + shiftdate)



















@csrf_protect
def index(request):
    from django.contrib.auth import authenticate, login
    wrongUser = {}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_superuser:
                wrongUser = {"message": "Wrong username or password"}
            else:
                login(request, user)
        else: 
            wrongUser = {"message": "Wrong username or password"}
    if request.user.is_authenticated:
        return redirect('/home')
    return render(request, 'frontend/index.html', wrongUser)


@login_required(login_url='/')
def log_out(request):
    from django.contrib.auth import logout
    if request.user.is_superuser:
        return redirect('/admin')
    logout(request)
    return redirect('/')

def get_dt(request):
    dt = CheckDateTime.objects.all()
    return render(request,'frontend/dt.html',{'dt':dt})


def check_codes(request,code):
    try:
        data = Code.objects.get(code=code)
        code_details = data.to_dict()
        #{'code': '123456','mfd_date': datetime.datetime(2021, 1, 8, 10, 6, 52, tzinfo=<UTC>),'company_name': 'Supreme','product_detail': 'ASDFGHJKL','shift_engineer': 'SAFAKAT','shift': '2','batch_no': 'qaz2020','standard_CML_No': 'thnmlp120'}

        return render(request, "frontend/bisleri.html",code_details)
    except Exception as error:
        columns = [c.name for c in  Code._meta.get_fields()] 
        code_details = {}
        for i in columns:
            code_details[i] = "Not Found"
        return render(request,"frontend/bisleri.html",code_details)

def under_process(request):
    return HttpResponse("This page is in under construction.")