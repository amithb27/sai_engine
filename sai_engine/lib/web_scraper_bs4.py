"""
Author: Amith Bhonsle (amith@saisei.com)
Description:
"""
from bs4 import BeautifulSoup
from .base_utilities import BaseUtilities
from .jenkins_utilities import JenkinsUtilities
from .scraper_utilities import webScraper_utilities
import re
import heapq

class webScraper(webScraper_utilities):
    """
    """    
    def get_script_testcases(self, stm_version, script_name, job_build_num=0, log_file_path=''):
        """
        Gets all the testcases of the given script, for a job_build number , for a particular stm_version
        stm_version    : Version of STM
        script name    : Name of the script whose testcases are to be accessed
        job_build_num  : (optional) Specifies the job_build number for the job if given. else the api takes the latest job_build_number
        log_file_path  : (optional) Specifies the full path of the log file if given else we build a file path using the other arguments
        
        To find all testcases in given html page. 
        Inspecting the page we find, testcases are defined with <div> tag having "class" attribute "test" and 
        testcase_names are defined within the above tags  in <span> tag with "class" attribute "name"
        We then extract text
        """
        self.logger.info('Running ' + BaseUtilities().get_function_name() + '(' + \
                  str(BaseUtilities().get_function_parameters_and_values()) +')')
        jenkins_obj = JenkinsUtilities()
        if log_file_path == '':
             if job_build_num == 0:
                 job_build_num = str(jenkins_obj.get_latest_build_number(stm_version))
             else:
                 job_build_num = str(job_build_num)
             url = self.get_page_url(stm_version, script_name,  job_build_num)
        else:
             url = log_file_path
        valid_log_file = self.validate_log_file(url)
        if not valid_log_file:
            self.logger.info(f'Turns out the file does not exist...Downloading the files')
            self.logger.info(jenkins_obj.download_log_files_wget(stm_version, job_build_num=job_build_num))
        page_handle = self.get_page_handle(url)
        testcase_list = []
        testcases  = page_handle.find_all("div", {"class" : "test"})
        for tc in testcases:
            testcase_name = tc.find("span",{"class" : "name"}).text
            testcase_list.append(testcase_name)
        self.logger.info(f'Testcase list of script {script_name} : {testcase_list}')
        return testcase_list

    def get_stm_build(self, stm_version, script_name='alarms', job_build_num=0, log_file_path=''):
        '''
        This function returns the stm_build number that was run for a specific job_build_num
        stm_version       :  Version of STM
        script_name       :  The script to be scraped inorder to get the STM_build number
        job_build_num     :  (optional)Build number of the jenkins job from where the details are to be scraped
                             If 0, takes the latest job build number 
        log_file_path     :  Full path of the file that is to be scraped
        '''
        self.logger.info('Running ' + BaseUtilities().get_function_name() + '(' + \
                  str(BaseUtilities().get_function_parameters_and_values()) +')')
        jenkins_obj = JenkinsUtilities()
        if job_build_num in [0,'0']:
             job_build_num = str(jenkins_obj.get_latest_build_number(stm_version))
        else:
             job_build_num = str(job_build_num)
        STM_build_number =  jenkins_obj.get_stm_build_from_map(stm_version, job_build_num)
        if STM_build_number: 
            print('Found the stm build from the mappings file {}:{}'.format(job_build_num,STM_build_number))
            jenkins_obj.update_build_map(stm_version, {STM_build_number:[job_build_num]})
            return STM_build_number
        if not log_file_path:     
             url = self.get_page_url(stm_version, script_name, job_build_num)
        else:
             url = log_file_path
        if not self.validate_log_file(url):
            print(f'Turns out the file [{url}]does not exist...Downloading the files')
            self.logger.info(jenkins_obj.download_log_files_wget(stm_version, job_build_num = job_build_num))
        retry_count = 0
        while retry_count<2:
            self.logger.info(f'Page url to be scraped {url}')
            """
            To get the stm build number we will have to scrape the content of some elements that are visible only onclick
            Thus we use the following approach where we handle onclick() events by using webdriver(using selenium for page interaction) 
            to click on element & then extract the desired information and then parse with BeautifulSoup
            """
            tdata = []
            driver = self.get_webdriver(url)
            driver = self.click_element(driver,"CLASS_NAME","element-header-right")
            driver = self.click_element(driver,"CSS_SELECTOR","#s1 > div:nth-child(1) > div:nth-child(2) > a:nth-child(1)")
            #Get the page source after onclick() event
            html_page = driver.page_source
            soup = BeautifulSoup(html_page, "html.parser")
            Testbed_Info_keyword = soup.find("div",{"id":"s1-k1-k1"})
            tables = Testbed_Info_keyword.find_all("table",{"class":"messages info-message"})
            for table in tables:
                tdata.append(table.find("td",{"class":"message"}).text)
            self.logger.info(f'data captured : {tdata}')
            for data in tdata:
                if "STM Software Version" in data:
                    STM_Version = data
                    self.logger.info('STM version captured: {}'.format(STM_Version))
            if not STM_Version or 'False' in STM_Version or 'false' in STM_Version:
                self.logger.error('Failed to capture STM version ({}). Trying with a different log file.'.format(STM_Version))
                url = self.get_page_url(stm_version, 'accesspoints', job_build_num)
                if not self.validate_log_file(url):
                    print(f'Given file [{url}] does not exist...Downloading the files.')
                    self.logger.info(jenkins_obj.download_log_files_wget(stm_version, job_build_num=job_build_num, script_names=['log_ap.html']))
                driver.quit()
                retry_count += 1
            else:
                break
        STM_build_number = re.search(r'-(\d+)', STM_Version, re.M).group(1)
        self.logger.info(f'STM_BUILD_NUMBER  : {STM_build_number}')
        driver.quit()
        jenkins_obj.update_build_map(stm_version, {STM_build_number:[job_build_num]})
        print('Found the stm build by scrapping through log file {}:{}'.format(job_build_num, STM_build_number))
        return STM_build_number        

    def stm_build_statistics(self, stm_version, stm_build):
        """
        This function checks if the mapping for stm build vs jenkins build is available in order to get the statistics
        from the right jenkins job. This is required because the stm build number informations in available inside the
        jenkins build logs.
        Input Argumenst:- stm_version :- The version of stm. Ex: "7_3_1"
                        stm_build   :- The stm build number. Ex: "11234"
        Output:- 
        stats ={"Total_Testcases_In_Suite": {},
                 "Testcases": {},
                 "Stm_Build_Number": '11234'
                 }
        """
        self.logger.info('Running ' + BaseUtilities().get_function_name() + '(' + \
                  str(BaseUtilities().get_function_parameters_and_values()) +')')
        jenkins_obj = JenkinsUtilities()
        if stm_build in [0,'0']:
            print('stm_build is 0 and hence, looking for latest jenkins build and its stm build...')
            jenkins_build_number = str(jenkins_obj.get_latest_build_number(stm_version))
            print('Found the latest build: ', jenkins_build_number)
            stm_build = self.get_stm_build(stm_version)
            print('Latest jenkins build is {} stm build is {} for stm version {}'
                  .format(jenkins_build_number, stm_build, stm_version))
        else:
            jenkins_build_number = jenkins_obj.get_jenkins_build_from_map(stm_version, stm_build)
            #If the stm build vs jenkins build map is not available.
            if not jenkins_build_number:
                print('No Jenkins job mapping found for stm build {}'.format(stm_build))
                self.logger.info('No Jenkins job mapping found for stm build {}'.format(stm_build))
                available_jenkins_maps = jenkins_obj.get_current_jenkins_build_mappings(stm_version)
                all_jenkins_builds = jenkins_obj.get_jobs_build_list(stm_version)
                builds_to_scrap = set(all_jenkins_builds) - set(available_jenkins_maps)
                print('Mapped builds: {}\nAll builds from jenkins: {}'
                      .format(available_jenkins_maps, all_jenkins_builds))
                for job_build_num in builds_to_scrap:
                    print('Looking for stm build {} in jenkins build {}'.format(stm_build, job_build_num))
                    cur_stm_build = self.get_stm_build(stm_version, job_build_num=job_build_num)
                    if not cur_stm_build:
                        print('Didnt get stm build for jenkins build', job_build_num)
                        continue
                    if cur_stm_build == stm_build:
                        print("Found the stm build {}.".format(cur_stm_build))
                        jenkins_build_number = job_build_num
                        break
            else:
                print('Jenkins job mapping found for stm build {}:-{}'.format(stm_build, jenkins_build_number))
        if not jenkins_build_number:
            print('Unable to find Jenkins build number for {}. Please make sure you have the right STM build'
                  .format(stm_build))
            return {}
        stats = {"Total_Testcases_In_Suite": {},
                 "Testcases": {},
                 "Stm_Build_Number": stm_build
                 }
        soup = self.get_driver_handle(stm_version, jenkins_build_number, 'consolidated_report.html')
        table = soup.find("table",{"id":"suite-stats"}).tbody
        rows = table.find_all("tr")
        for row in rows:
             name = row.find("a").text
             data = row.find_all("td", {"class":"stats-col-stat"})
             Total_tc = data[0].text
             Pass_tc = data[1].text
             Fail_tc = data[2].text
             if '.' in name:
                stats["Testcases"].update({
                    name.split(" . ")[1]:{"Total_tc" : Total_tc, "Pass_tc" : Pass_tc, "Fail_tc" : Fail_tc}
                    })
             else:
                stats["Total_Testcases_In_Suite"]={"Total_tc" : Total_tc, "Pass_tc" : Pass_tc, "Fail_tc" : Fail_tc}
        self.logger.info(f'Suite Statistics : {stats}')
        return stats

    def get_last_stm_build_tested(self, stm_version):
        """
        This function returns the stm build number that is run on latest jenkins job build for a specific stm_version 
        """
        self.logger.info('Running ' + BaseUtilities().get_function_name() + '(' + \
                  str(BaseUtilities().get_function_parameters_and_values()) +')')
        latest_job_build_number = str(JenkinsUtilities().get_latest_build_number(stm_version))
        if not latest_job_build_number: raise ValueError('Failed to get latest job build number for', stm_version)
        last_stm_build_tested = self.get_stm_build(stm_version, job_build_num=latest_job_build_number)
        self.logger.info(f'Last STM_BUILD_Tested : {last_stm_build_tested}')
        return last_stm_build_tested
    
    def get_builds_trend(self, stm_version, count=10):
        """
        This function retuurns the dictionary with all the suite statistics(total testcases, pass) of jobs that are executed for specific stm_version on specific stm_build
        """ 
        self.logger.info('Running ' + BaseUtilities().get_function_name() + '(' + \
                  str(BaseUtilities().get_function_parameters_and_values()) +')')
        print('Get builds trend for stm version', stm_version)
        build_list = JenkinsUtilities().get_jobs_build_list(stm_version)
        self.logger.info(f'Builds run on stm_version {stm_version} so far : {build_list}')
        count = int(count)
        if len(build_list) >= count:
            build_list = heapq.nlargest(count, build_list)
        if len(build_list) < count:
            build_list = build_list
        build_pass_percent_map = {}
        for job_build in build_list:
            self.logger.info(f'Getting build details of build number {job_build} of stm {stm_version}')
            stm_build = self.get_stm_build(stm_version, job_build_num=str(job_build))
            suite_statistics = self.stm_build_statistics(stm_version, stm_build)               
            pass_percentage = round(int(suite_statistics["Total_Testcases_In_Suite"]["Pass_tc"])/int(suite_statistics["Total_Testcases_In_Suite"]["Total_tc"])*100, 2)
            if stm_build in build_pass_percent_map.keys():
                if build_pass_percent_map[stm_build] < pass_percentage:
                     build_pass_percent_map.update({stm_build : pass_percentage})
            else:
                build_pass_percent_map.update({stm_build : pass_percentage})
        self.logger.info(f'BUILD VS PASS PERCENTAGE : {build_pass_percent_map}')     
        return build_pass_percent_map

    def get_latest_builds_total_TC(self, stm_version):
        """
        Returns the latest build total testcases for a specific stm_version
        """
        self.logger.info('Running ' + BaseUtilities().get_function_name() + '(' + \
                  str(BaseUtilities().get_function_parameters_and_values()) +')')
        suite_statistics = self.stm_build_statistics(stm_version, stm_build=0)               
        total_tc = int(suite_statistics["Total_Testcases_In_Suite"]["Total_tc"])
        self.logger.info(f'Total nmber of Testcases in suite : {total_tc}')
        return total_tc
    
    def get_latest_builds_pass_TC_no(self,stm_version):
        """
        Returns the latest build passed testcases number
        """
        self.logger.info('Running ' + BaseUtilities().get_function_name() + '(' + \
                  str(BaseUtilities().get_function_parameters_and_values()) +')')
        suite_statistics = self.stm_build_statistics(stm_version, stm_build=0)               
        pass_tc = int(suite_statistics["Total_Testcases_In_Suite"]["Pass_tc"])
        self.logger.info(f'Number of Passed Testcases in suite : {pass_tc}')
        return pass_tc
        
    def get_latest_builds_fail_TC_no(self,stm_version):
        """
        Returns the latest build failed testcases number
        """
        self.logger.info('Running ' + BaseUtilities().get_function_name() + '(' + \
                  str(BaseUtilities().get_function_parameters_and_values()) +')')
        suite_statistics = self.stm_build_statistics(stm_version, stm_build=0)               
        fail_tc = int(suite_statistics["Total_Testcases_In_Suite"]["Fail_tc"])
        self.logger.info(f'Number of Failed Testcases in suite : {fail_tc}')
        return fail_tc
    
    def get_scripts_test_info(self, stm_version, stm_build, scripts=[]):
        """_summary_
        Args:
            stm_version (str): Stm version for which the testcases failed info is required.
            stm_build (str): stm build for which the testcases failed info is required.
            scripts (list):  List of scripts for which info is required.
                            Empty list will mean that info for all scripts should be returned.
        return:-
         {
            'Alarms' :[
                    {
                    'TC101' : 'Alarms Configurations And Traffic Setup',
                    'message' : 'Expected Ping to Pass, But It Failed.'
                    },
                    {
                    'TC102' : 'Alarms Configurations And Traffic Setup',
                    'message' : 'Expected Ping to Pass, But It Failed.'
                    }
                ],
            'Bypass' : []
        }
        """
        self.logger.info('Running ' + BaseUtilities().get_function_name() + '(' + \
                  str(BaseUtilities().get_function_parameters_and_values()) +')')
        jenkins_obj = JenkinsUtilities()
        valid_stm_builds = jenkins_obj.get_stm_builds_from_map(stm_version)
        if not stm_build in valid_stm_builds:
            self.logger.error('STM build {} not valid. Please recheck the number or populate data.'
                              .format(stm_build))
            print("Invalid build number", stm_build)
            return {}
        print("Getting test info for scripts of stm {} build {}.".format(stm_version,stm_build))
        jenkins_build_number = jenkins_obj.get_jenkins_build_from_map(stm_version, stm_build)
        if not jenkins_build_number:
            print('Unable to find Jenkins build number for {}. \
                  Please make sure you have the right STM build'.format(stm_build))
            return {}
        soup, driver = self.get_driver_handle(stm_version, jenkins_build_number, 'consolidated_report.html', quit_driver=False)
        #Get the list of scripts for which info needs to be parsed.
        failed_scripts_info = {}
        if scripts:
            if not isinstance(scripts, list):
                scripts = [scripts]
        parsed_data = soup.find("table",{"id":"suite-stats"}).tbody
        parsed_data = parsed_data.find_all("tr")
        for td_data in parsed_data:
            script_name_tag = td_data.find("a").text
            if len(script_name_tag) > 9:
                script_name = script_name_tag.split('ConOut . ')[1]
                if scripts and script_name not in scripts:
                    continue
                driver = self.click_element(driver,"LINK_TEXT",script_name_tag)
                html_page = driver.page_source
                new_soup = BeautifulSoup(html_page, "html.parser")
                
                test_details = new_soup.find("table",{"id":"test-details"})
                test_details_body = test_details.find("tbody")
                test_details_status = test_details_body.findAll("tr")
                for status_tag_td in test_details_status:
                    status_tag_span = status_tag_td.find("td",{"class":"details-col-status"})
                    status = status_tag_span.find("span")
                    if status.text == "FAIL":
                        if not failed_scripts_info.get(script_name, None):
                            failed_scripts_info[script_name] = []
                        #Get the Fail test message
                        message_class = status_tag_td.find("td",{"class":"details-col-msg"})
                        message = message_class.find("div")
                        #Get the test Tag number and name
                        test_name_class = status_tag_td.find("td",{"class":"details-col-name"})
                        test_tag_name = test_name_class.find("a")
                        failed_scripts_info[script_name].append(
                            {
                                "status" : status.text, 
                                'detail':(test_tag_name.text[len(script_name_tag)+3:len(script_name_tag)+9].strip() ,
                                test_tag_name.text[len(script_name_tag)+9:].strip()),
                                "message" : message.text
                            }
                        )
                self.logger.info("Build:- {}.Got the testcase failure details of: {}".format(stm_build,script_name))
                print("Build:- {}.Details collected for script: {}".format(stm_build,script_name))
        driver.quit()
        return failed_scripts_info
                
                

    def get_driver_handle(self, stm_version, jenkins_build_number, log_file_name, quit_driver=True):
        """_summary_

        Args:
            stm_version (_type_): _description_
            jenkins_build_number (_type_): _description_
            log_file_name (_type_): _description_
        """
        consolidated_report = self.__base_dir__ + self.__jenkins_log_path_map__[stm_version] + \
        str(jenkins_build_number) + '/' +log_file_name
        driver = self.get_webdriver(consolidated_report)
        html_page = driver.page_source
        if quit_driver:
            driver.quit()
            return BeautifulSoup(html_page, "html.parser")
        else:
            return (BeautifulSoup(html_page, "html.parser"), driver)
         

if __name__ == '__main__':
    obj = webScraper()
