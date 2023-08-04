"""sai_engine URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from sailytics import views
"""
{"l": {"Total_tc" : 23423, "Pass_tc" : 414, "Fail_tc" : 423}},
"Testcases": {"Alarms":{"Total_tc" : 10, "Pass_tc" : 5, "Fail_tc" : 5}},
"Stm_Build_Number": 11456
}

"""

urlpatterns = [
    
    path('admin/', admin.site.urls),
    path('latest_build/<stm_version>/', views.get_last_stm_build_tested, name="get_last_stm_build_tested"),
    path('jen/', views.get_jenkins_jobs),
    path('stm_builds_trend_test/<stm_version>/', views.get_builds_trend_test, name="get_builds_trend_test"),
    path('stm_builds_trend/<stm_version>/<count>/', views.get_builds_trend, name="get_builds_trend"),
    path('build_statistics/<stm_version>/<stm_build>/', views.get_stm_build_statistics, name="get_stm_build_statistics"),
    path('get_stm_builds/<stm_version>/', views.get_stm_builds, name="get_stm_builds"),
    path('total_tc/<stm_version>/', views.get_latest_builds_total_TC, name="get_latest_builds_total_TC"),
    path('pass_tc/<stm_version>/', views.get_latest_builds_pass_TC_no, name="get_latest_builds_pass_TC_no"),
    path('fail_tc/<stm_version>/', views.get_latest_builds_fail_TC_no, name="get_latest_builds_fail_TC_no"),
    path('get_build_array/<stm_version>/' ,views.get_build_array, name="get_build_array"),
    path('populate_build_statistics/<stm_version>/<stm_build>' , views.populate_build_statistics , name = 'populate_build_statistics'),
    path('populate_scripts_test_details/<stm_version>/<stm_build>' , views.populate_scripts_test_details, name='populate_scripts_test_details'),
    path('get_regression_testbeds/<stm_version>/' , views.get_regression_testbeds, name='get_regression_testbeds'),
    path('testbed_reserve/<stm_host>/<user>/<message>', views.reserve_testbed, name='reserve_testbed'),
    path('testbed_release/<stm_host>/', views.release_testbed, name='release_testbed'),
    path('testbed_status/<stm_host>/', views.testbed_status, name='testbed_status')
    # path('generate_latest_data/<stm_version>', views.generate_latest_data, name="generate_latest_data")
    ]
