from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('home', views.home, name='home'),
    path('home_xls', views.home_xls, name='home_xls'),
    path('summary/summary_1', views.summary_1, name='summary_1'),
    path('summary/pipeshiftduration_summary_1', views.pipeshiftduration_summary_1, name='pipeshiftduration_summary_1'),
    path('summary/summary_2', views.summary_2, name='summary_2'),
    path('summary/summary_4', views.summary_4, name='summary_4'),
    path('summary/material_issue_summary_4', views.material_issue_summary_4, name='material_issue_summary_4'),
    path('summary/summary_7', views.summary_7, name='summary_7'),
    path('summary/summary_8', views.summary_8, name='summary_8'),
    path('summary/summary_format', views.summary_format, name='summary_format'),
    path('summary', views.summary, name='summary'),
    path('logout', views.log_out, name='log_out'),
    path('get_data/',views.get_dt,name = "get_data"),
    path('check/<str:code>/',views.check_codes,name="check_codes"),
    path('under_process/',views.under_process,name = "under_process"),
    path('v2/', views.homev2, name = 'homev2'),
    path('v2/download_excel_report/', views.download_excel_report, name = 'download_excel_report'),
    path('summaryv2/', views.summaryv2, name = 'summaryv2'),
    path('summary/production_summary_v2/', views.production_summary_v2, name = 'production_summary_v2'),
    path('size_wise_report_v2/', views.size_wise_report_v2, name = 'size_wise_report_v2'),
    path('pipe_count_summary/',views.pipe_count_summary, name = "pipe_count_summary"),#Not using v2 because it creating problems in function call because of file and folder names and structure
    path('summary/summary_format_v2', views.summary_format_v2, name = 'summary_format_v2'),
    path('summary/summary_4_v2', views.summary_4_v2, name = 'summary_4_v2'),
    path('summary/summary_7_v2', views.summary_7_v2, name = 'summary_7_v2'),
    path('summary/summary_8_v2', views.summary_8_v2, name = 'summary_8_v2'),
    path('summary/material_issue_summary_4_v2', views.material_issue_summary_4_v2, name='material_issue_summary_4_v2'),
    path('summary/rejected_pipe', views.rejectedPipeCountByQc, name='rejected_pipe_count'),
]