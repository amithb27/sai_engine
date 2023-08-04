from django.http import JsonResponse
from sai_engine.lib.jenkins_utilities import JenkinsUtilities
from sai_engine.lib.web_scraper_bs4 import webScraper
from sai_engine.lib.testbed_reservation import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import *

@api_view(['GET'])
def get_regression_testbeds(request, stm_version):
    server_obj = JenkinsUtilities()
    data = {
        "value": server_obj.get_all_regression_testbeds(stm_version)
    }
    return Response(data=data,status=status.HTTP_200_OK) 

@api_view(['GET'])
def testbed_status(request, stm_host):
    testbed_obj = testbed_controller()
    data = {
        "value": testbed_obj.is_testbed_free(stm_host)
    }
    return Response(data=data,status=status.HTTP_200_OK)

@api_view(['GET'])
def reserve_testbed(request, stm_host, user, message):
    testbed_obj = testbed_controller()
    data = {
        "value": testbed_obj.testbed_reserve(stm_host,user,message)
    }
    return Response(data=data,status=status.HTTP_200_OK)

@api_view(['GET'])
def release_testbed(request, stm_host):
    testbed_obj = testbed_controller()
    data = {
        "value": testbed_obj.testbed_release(stm_host)
    }
    return Response(data=data,status=status.HTTP_200_OK)

@api_view(['GET', 'POST'])
def get_jenkins_jobs(request):
    server_obj = JenkinsUtilities()
    if request.method == 'GET':
        return JsonResponse(server_obj.get_jobs(), safe=False)

    if request.method == 'POST':
        return Response(server_obj.get_jobs(), status=status.HTTP_200_OK)

@api_view(['GET'])
def get_last_stm_build_tested(request, stm_version):
    server1_obj = webScraper()
    if request.method == 'GET':
        return JsonResponse(server1_obj.get_last_stm_build_tested(stm_version), safe=False)

@api_view(['GET'])
def get_builds_trend_test(request, stm_version):
    print('Request accepted.....')
    version_obj = Version.objects.get(version_name = stm_version)
    buildData = {}
    for build in version_obj.build.all():
        buildData.update({build.build_number:build.pass_percentage})
    data = {
        "value":buildData
    }
    print(data)
    
    return Response(data, status=status.HTTP_200_OK)
        
@api_view(['GET'])
def get_suite_statistics(request, stm_version):
    server1_obj = webScraper()
    buildData = server1_obj.get_statistics_by_suite(stm_version)
    data = {
        "value":buildData
    }
    if request.method == 'GET':
        return Response(data = data , status = status.HTTP_200_OK)

@api_view(['GET'])
def populate_scripts_test_details(request, stm_version, stm_build):
    server_obj = webScraper()
    script_test_info = server_obj.get_scripts_test_info(stm_version,stm_build)
    version_obj = Version.objects.get(version_name = stm_version)
    build_obj = StmBuild.objects.get(version = version_obj , build_number = stm_build)
    for script , value in script_test_info.items():
        script_obj = Script.objects.get(build = build_obj , name = script)
        script_inst = ScriptTestInfo(script = script_obj)
        for fail_reason in value:
            script_inst.status = fail_reason['status']
            script_inst.message = fail_reason['message']
            script_inst.main = fail_reason['detail']
        script_inst.save()
    return Response(data={'value':script_test_info},status= status.HTTP_200_OK)

@api_view(['GET'])
def populate_build_statistics(request, stm_version, stm_build):
    server_obj = webScraper()
    jenkin_obj = JenkinsUtilities()
    all_stm_builds = jenkin_obj.get_stm_builds_from_map(stm_version)
    if not all_stm_builds:
        server_obj.stm_build_statistics(stm_version, '000000')
        all_stm_builds = jenkin_obj.get_stm_builds_from_map(stm_version)
    else:
        all_stm_builds = [0]
    for stm_build in all_stm_builds:
        statistics = server_obj.stm_build_statistics(stm_version, stm_build)
        build_statistics = statistics['Total_Testcases_In_Suite']
        build_number = statistics['Stm_Build_Number']
        testcase_statistics = statistics['Testcases']
        try :
            version = Version.objects.get(version_name = stm_version)
            print('Version already exists.')
        except Exception as e :
            version = Version.objects.create(version_name = stm_version)
        try:
            print('--------->got in ' , build_number)
            build = StmBuild.objects.get(build_number = build_number)
            print('--------->got in ')

            if int(build.passed_testCase) < int(build_statistics['Pass_tc']):
                build.pass_percentage = round((int(build_statistics['Pass_tc'])/int(build_statistics['Total_tc']))*100,2)
                build.save()
                Script.objects.filter(build = build).delete()
                for key,value in testcase_statistics.items():
                    Script.objects.create(build = build,
                                    name = key,
                                    total_testCase = value['Total_tc'] ,
                                    passed_testCase = value['Pass_tc'],
                                    failed_testCase = value['Fail_tc']
                    ) 
        except StmBuild.DoesNotExist as e:
            build = StmBuild.objects.create(version = version ,
                            build_number = build_number ,
                            pass_percentage= round((int(build_statistics['Pass_tc'])/int(build_statistics['Total_tc']))*100,2),
                                total_testCase  = build_statistics['Total_tc'],
                                passed_testCase = build_statistics['Pass_tc'],
                                failed_testCase=build_statistics['Fail_tc']
                                )
            for key,value in testcase_statistics.items():
                Script.objects.create(build = build ,
                                    name = key ,
                                    total_testCase = value['Total_tc'] ,
                                    passed_testCase = value['Pass_tc'],
                                    failed_testCase = value['Fail_tc']
                ) 
    return Response({'message':'created' , 'content':statistics}, status= status.HTTP_200_OK)

@api_view(['GET'])
def get_builds_trend(request, stm_version, count=10):
    server1_obj = webScraper()
    if request.method == 'GET':
        return JsonResponse(server1_obj.get_builds_trend(stm_version, count), safe=False)

@api_view(['GET'])
def get_latest_builds_total_TC(request, stm_version):
    print("hello ")
    server1_obj = webScraper()
    if request.method == 'GET':
        return JsonResponse(server1_obj.get_latest_builds_total_TC(stm_version), safe=False)

@api_view(['GET'])
def get_latest_builds_pass_TC_no(request, stm_version):
    server1_obj = webScraper()
    if request.method == 'GET':
        return JsonResponse(server1_obj.get_latest_builds_pass_TC_no(stm_version), safe=False)

@api_view(['GET'])
def get_latest_builds_fail_TC_no(request, stm_version):
    server1_obj = webScraper()
    if request.method == 'GET':
        return JsonResponse(server1_obj.get_latest_builds_fail_TC_no(stm_version), safe=False)

@api_view(['GET'])
def populate_stm_builds(request, stm_version):
    server_obj = JenkinsUtilities()
    data = {'value' : server_obj.get_all_stm_builds(stm_version)}
    if request.method == 'GET':
        return Response(data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_build_array(request , stm_version):
    server1_obj = webScraper()
    latest_build = server1_obj.get_last_stm_build_tested(stm_version)
    total = server1_obj.get_latest_builds_total_TC(stm_version)
    passed = server1_obj.get_latest_builds_pass_TC_no(stm_version)
    failed = server1_obj.get_latest_builds_fail_TC_no(stm_version)

    build_array  = {
            "build":latest_build,
            'total':total ,
            'passed':passed,
            "failed":failed  
    }
    print(build_array)
    return Response(data=build_array , status= status.HTTP_200_OK)
    
"""
@api_view(['GET'])
def get_script_testcases(request, stm_version, script_name, job_build_num=''):
    server1_obj = webScraper()
    if request.method == 'GET':
        return JsonResponse(server1_obj.get_script_testcases(stm_version, script_name), safe=False)
"""
# @api_view(['GET'])
# def get_stm_build_statistics(request, stm_version, stm_build=0):

#     server_obj = 
#     body = {"value":server_obj.stm_build_statistics(stm_version, stm_build)}
#     if request.method == 'GET':
#         return Response(body, status= status.HTTP_200_OK)

@api_view(['GET'])
def get_stm_build_statistics(request,stm_version,stm_build):
    print('Entered get_stm_build_statistics in views.py file .....')
    data = {}
    try :
        version_inst = Version.objects.get(version_name= stm_version)
        
        if stm_build == '0':
            build_inst_array = StmBuild.objects.filter(version=version_inst ).order_by('build_number')
            build_inst = build_inst_array[build_inst_array.count()-1]
            # print('-------------------------------------------->',
            #       StmBuild.objects.filter(version=version_inst ).order_by('build_number')[-1])
        else:
            build_inst = StmBuild.objects.get(build_number = stm_build , version = version_inst )
    except Exception as e :
        return Response( {'error':f'Version or Build is not available in database.'} , status = status.HTTP_400_BAD_REQUEST)   

    testcases = build_inst.testCases.all()
   
    Total_Testcases_In_Suite={
        "Total_tc" : build_inst.total_testCase, "Pass_tc" : build_inst.passed_testCase, "Fail_tc" : build_inst.failed_testCase}
    Testcases= {}
    for testcase in testcases:
        testCase_obj  = [(testcase.name,{"Total_tc" :testcase.total_testCase , "Pass_tc" : testcase.passed_testCase, "Fail_tc" : testcase.failed_testCase})]
        Testcases.update(testCase_obj)
    data.update([("Stm_Build_Number",build_inst.build_number),
                 ('Total_Testcases_In_Suite',Total_Testcases_In_Suite),
                 ('Testcases',Testcases)])
    print('get_stm_build_statistics: Input Data:- \n{}\nReturn data:-\n{}'.format((stm_version,stm_build),data))
    return Response(data={'value':data},status=status.HTTP_200_OK)

@api_view(['GET'])
def get_stm_builds(request , stm_version):
    try:
        version_obj = Version.objects.get(version_name = stm_version)
    except Exception as e :
       return Response({'error':'No Version found  '},status= status.HTTP_404_NOT_FOUND)
    stm_builds = StmBuild.objects.filter(version = version_obj).values_list('build_number')
    builds_array = [build for (build,) in stm_builds]
    return Response(data={'value':builds_array},status= status.HTTP_200_OK)

@api_view(['GET'])
def get_failed_scripts(request , stm_version):
    try:
        version_obj = Version.objects.get(version_name = stm_version)
    except Exception as e :
       return Response({'error':'No Version found  '},status= status.HTTP_404_NOT_FOUND)
    stm_builds = StmBuild.objects.filter(version = version_obj).values_list('build_number')
    builds_array = [build for (build,) in stm_builds]
    return Response(data={'value':builds_array},status= status.HTTP_200_OK)
    
    
    
