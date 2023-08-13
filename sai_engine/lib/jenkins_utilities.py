'''
Author: Amith Bhonsle
Description: 
'''

from django.conf import settings
from jenkins import Jenkins
from os import system, path
from .base_utilities import BaseUtilities
from .testbed_reservation import testbed_controller
import pylogging
import json

class JenkinsUtilities(object):
    '''
    Base class that contains all the functions of jenkins api using python wrappers.
    Required parameters:-
    jenkins_username : The username of the jenkins instance running.
    jenkins_password : The password of the jenkins instance running.
    jenkins_ip : The ip address where jenkins instance is running.
    jenkins_port : The port on which the jenkins instance is running.
    '''
    def __init__(self):
        '''
        Function to initialise all the parameter values and create connection object.
        '''
        self.__base_dir__ = str(settings.BASE_DIR)
        self.__config_filepath__ = self.__base_dir__ + '/sai_engine/data/config.json'
        self.__auth_filepath__ = self.__base_dir__ + '/sai_engine/data/auth.json'
        self.__build_map_filepath__ = self.__base_dir__ + '/sai_engine/data/stm_jenkins_build_map.json'
        with open(self.__auth_filepath__, 'r') as fobj:
            self.jenkins_configs = json.load(fobj)['jenkins']
        self.__jenkins_username__ = self.jenkins_configs['username']
        self.__jenkins_password__ = self.jenkins_configs['password']
        self.__jenkins_ip__ = self.jenkins_configs['ip']
        self.__jenkins_port__ = self.jenkins_configs['port']
        with open(self.__config_filepath__, 'r') as fobj:
            self.node_configs = json.load(fobj)['NODES']
        self.__jenkins_log_path_map__ = self.node_configs['jenkins']['ver_log_path_map']
        self.__jenkins_version_job_map__ = self.node_configs['jenkins']["version_job_map"]
        self.__jenkins_valid_script_names__ = self.node_configs['jenkins']["valid_script_names"]
        self.__jenkins_regression_testbeds__ = self.node_configs['regression_testbeds']
        self.__jenkins_run_script_name__ = self.node_configs['jenkins']['script_run_job_name']
        with open(self.__build_map_filepath__, 'r') as fobj:
            self.__sbuild_jbuild_map__ = json.load(fobj)
        self.server_obj = Jenkins(
            'http://' + 
            self.__jenkins_ip__ + ':' + self.__jenkins_port__, 
            username = self.__jenkins_username__, 
            password = self.__jenkins_password__
        )
        self.__jenkins_log_filepath__ = self.__base_dir__ + self.node_configs['pylogger']['jenkins_log_file']
        self.logger = pylogging.PyLogging(LOG_FILE_PATH = self.__jenkins_log_filepath__ + '/log_file_', LOG_FILE_FORMAT = '%d-%m-%y')
        return

    def get_job_input_parameters(self, job_name):
        """_summary_
        Args:
            job_name (_type_): _description_
        """
        params = {}
        for parameter in self.server_obj.get_job_info(job_name)['property'][0]['parameterDefinitions']:
            params.update(
                {
                    parameter['name']: parameter['defaultParameterValue']['value']
                }
            )
        return params
            
    def build_jenkins_job(self, parameters={}):
        """This function triggers jenkins job
        Args:
            STM_VERSION (str):                      stm_7.3.1
            STM_IP (str) :                          10.1.11.76
            SCRIPT_FILE_NAME (str) :                accesspoint-hierarchy
            CUSTOM_BUILD_PATH (str) :               LATEST
                                                    /11449/stm-install-18.04-7.3.1-11448-202010613.tgz

            BRANCH (str, optional) :                default
                                                    build/builds/stm_7.3.1
            EXIT_ON_FAILURE (boolean, optional) :   True
            DEPLOY_BUILD (boolena, optional) :      False
            EXCLUDE_TESTCASES (boolean, optional):  False
            TESTCASES_TO_EXCLUDE (str, optional) :  TC0000
            INCLUDE_TESTCASES (boolean, optional):  False
            TESTCASES_TO_INCLUDE (str, optional) :  TC0000
            LAG (booelan, optional) :               False
        Usage:
            build_jenkins_job('api-test', {'param1': 'test value 1', 'param2': 'test value 2'})
        """
        self.logger.info('Running ' + BaseUtilities().get_function_name() + '(' + \
                  str(BaseUtilities().get_function_parameters_and_values()) +')')
        
        required_parameters = ('STM_VERSION', 'STM_IP', 'SCRIPT_FILE_NAME', 'CUSTOM_BUILD_PATH')
        if not set(required_parameters) <= set(parameters):
            self.logger.error('Required parameters not provided. Required: {}\nProvided: {}'.format(
                required_parameters, parameters
            ))
            return False
        other_parameters = self.get_job_input_parameters(self.__jenkins_run_script_name__)
        all_parameters = {**other_parameters,**parameters}
        all_parameters['STM_IP'] = all_parameters['STM_IP'].replace("_",".")
        all_parameters['BRANCH'] = 'default' if not all_parameters['BRANCH'] else all_parameters['BRANCH']
        del all_parameters['STM_VERSION']
        all_parameters['CUSTOM_BUILD_PATH'] = 'LATEST' if not all_parameters['CUSTOM_BUILD_PATH']\
                                                        else all_parameters['CUSTOM_BUILD_PATH']
        all_parameters['DEPLOY_BUILD'] = True
        
        print('\nFinal', all_parameters)
        ret = self.server_obj.build_job(self.__jenkins_run_script_name__, all_parameters)
        print('This is the output of build_job', ret)
        return True
        
    def get_all_regression_testbeds(self, stm_version=''):
        """This API returns all the testbeds that are available.

        Args:
            stm_version (str, optional): Name of the stm version. Defaults to ''.
        
        Returns:
            {
                "7_3_1" : ["10.1.11.76", "10.1.11.106"],
                "8_0_1" : ["10.1.11.80", "10.1.12.90", "10.1.12.119", "10.1.15.60"]
            }
        """
        self.logger.info('Running ' + BaseUtilities().get_function_name() + '(' + \
                  str(BaseUtilities().get_function_parameters_and_values()) +')')
        return self.__jenkins_regression_testbeds__ if not stm_version else sorted(self.__jenkins_regression_testbeds__[stm_version])
        
    def get_all_script_names(self, stm_version):
        """_summary_

        Args:
            stm_version (_type_): _description_
        """
        return self.__jenkins_valid_script_names__[stm_version]

    def validate_data(self, data):
        """
        Method to validate the structure of data that is updated in the config file.
        This is to avoid disturbing the structure of the data.
        """
        if not data:
            self.logger.error('Data you are trying to update is empty.')
            return False
        else:
            if isinstance(list(data.keys())[0], str) and (isinstance(list(data.values())[0], str) or isinstance(list(data.values())[0], list)):
                return True
            else:
                self.logger.error('Data you are trying to update is in wrong format.:- {}'.format(data))
                return False
    
    def update_build_map(self, stm_version, data):
        """
        This function will create stm vs jenkins build mappin gif both stm build and jenkins build are provided.
        If only stm_build is provided and it's mapping doesn't exist, then mapping for that stm build is created.
        Input arguments: stm_version :- Stm version
                    data = {
                            stm_build :- The stm build number whose mapping is to be created
                            jenkins_build:-  The jenkins job build number whose mapping is to be created.
                            }
        Output:- True
        """
        if not self.validate_data(data):
            return False
        map_data = {}
        with open(self.__build_map_filepath__) as fobj:
            map_data = json.load(fobj)
            print('Map data before updating: ', map_data)
            for k,v in data.items():
                    if map_data[stm_version].get(k, None):
                        if isinstance(v, list):
                            map_data[stm_version][k].extend(v)
                            map_data[stm_version][k] = list(set(map_data[stm_version][k]))
                        else:
                            if v not in map_data[stm_version][k]:
                                map_data[stm_version][k].append(v)
                            else:
                                print('Build map {} already exists.'.format({k,v}))
                                return True
                    else:
                        if isinstance(v, list):
                            map_data[stm_version].update({k:v})
                        else:
                            map_data[stm_version].update({k:[v]})
            print('Map data after updating: ', map_data)
        with open(self.__build_map_filepath__, 'w') as fobj:
            json.dump(map_data, fobj, indent=4)
            fobj.close()
        return True
    
    def get_stm_builds_from_map(self, stm_version):
        """_summary_
        This function will return a list of all the stm versions from the stm build vs jenkins build maps.
        Args:
            stm_version (_type_): _description_

        Returns:
            lsit: list of al the stm builds
            example: [123123,123123,12312234,35434,354234]
        """
        self.logger.info('Running ' + BaseUtilities().get_function_name() + '(' + \
                  str(BaseUtilities().get_function_parameters_and_values()) +')')
        
        if self.__sbuild_jbuild_map__.get(stm_version):
            return list(self.__sbuild_jbuild_map__[stm_version].keys())
        else:
            self.logger.error('Unsupported argument specified. {} doesnt exists.'.format(stm_version))
            print('------>logger', 'Unsupported argument specified. {} doesnt exists.'.format(stm_version))
            return {}

    def get_stm_build_from_map(self, stm_version, jenkins_build):
        """_summary_

        Args:
            stm_version (_type_): _description_
            jenkins_build (_type_): _description_

        Returns:
            _type_: _description_
        """
        self.logger.info('Running ' + BaseUtilities().get_function_name() + '(' + \
                  str(BaseUtilities().get_function_parameters_and_values()) +')')
        if self.__sbuild_jbuild_map__.get(stm_version):
            stm_build = None
            sbuild_jbuild_map = self.__sbuild_jbuild_map__[stm_version]
            for k,v in sbuild_jbuild_map.items():
                if jenkins_build in v:
                    print('Found the build {} == {}'.format(jenkins_build, v))
                    stm_build = k
                    break
        else:
            self.logger.error('Unsupported argument specified. {} doesnt exists.'.format(stm_version))
            stm_build = None
        return stm_build

    def get_jenkins_build_from_map(self, stm_version, stm_build):
        '''
        jenkins builds are different from stm builds. Jenkins builds are the number of times a particular job is executed.
        Where as stm builds are the builds generated by the build server. The information about stm build is saved inside the 
        log files of jenkins builds and hence it is important to keep a mapping of stm build vs jenkins build.
        This API is used to get the jenkins build number using the stm build number.
        Arguments:- stm_version : version of the stm (7_3_1, 8_0_1)
                    stm_build : Build number of the stm_version
        Return:- None : if the stm build does not exist
                jenkins_builds : A list containing the jenkins build number as string. It can have multiple values if jenkins
                job was run multiple times on same stm build.
                ex 1: jenkins_builds = "51"
        '''
        self.logger.info('Running ' + BaseUtilities().get_function_name() + '(' + \
                  str(BaseUtilities().get_function_parameters_and_values()) +')')
        if self.__sbuild_jbuild_map__.get(stm_version):
            sbuild_jbuild_map = self.__sbuild_jbuild_map__[stm_version]
            if sbuild_jbuild_map.get(stm_build):
                jenkins_build = sbuild_jbuild_map[stm_build][0]
            else:
                self.logger.error('Unsupported argument specified. {} doesnt exists.'.format(stm_build))
                jenkins_build = None
        else:
            self.logger.error('Unsupported argument specified. {} doesnt exists.'.format(stm_version))
            jenkins_build = None
        return jenkins_build
        
    def download_log_files_wget(self, stm_version, source_full_path='', destination_path='', job_build_num=0, script_names=[]):
        '''
        Function to download all the log files and consolidated report that is required to populate the database
        stm_version      :  Version of stm
        source_full_path :  (optional) Path of the file from where the log files are to be downloaded
        destination_path :  (optional) Path where the log files are to bbe stored
        job_name         :  (optional) Name of the jenkins job whose log files are to be downloaded
                            If empty, the job_name is mapped using stm_version
        job_build_num    :  (optional) The build number of the particular jenkins job
                            If empty, the job_number is the latest/last build number of the job(of job_name) that is executed
        '''
        self.logger.info('Running ' + BaseUtilities().get_function_name() + '(' + \
                  str(BaseUtilities().get_function_parameters_and_values()) +')')
        job_name =  self.__jenkins_version_job_map__[stm_version]
        if not job_build_num: job_build_num = self.get_latest_build_number(stm_version)
        if not destination_path: destination_path = self.__base_dir__ + self.__jenkins_log_path_map__[stm_version] + f'{job_build_num}/'
        if not script_names:
            script_names = ['consolidated_report.html', 'log_alarms.html']
        commands = []
        exit_codes=[]
        if not source_full_path:
            for script in script_names:
                source_full_path = '/job/' + job_name + '/' + str(job_build_num) + '/robot/report/' + str(script)
                cut_dir_value = len(source_full_path.split('/'))
                if not path.exists(destination_path):
                    self.execute_cmd(f'mkdir -p {destination_path}')
                #Changing the -A parameter from "log_*, consolidated_report*" to "consolidated_report.html" as we are using this file alone
                #and also to increase the response time of the system.
                # cmd1 = """wget -r -np -nH --no-parent --auth-no-challenge --cut-dirs={} -e robots=off -A "log_*, consolidated_report*" \
                #     --http-user={} --http-password={} -P {} http://{}:{}{}"""
                cmd = """wget --no-parent --auth-no-challenge --cut-dirs={} -e robots=off \
                    --http-user={} --http-password={} -P {} http://{}:{}{}""".format(
                        cut_dir_value,
                        self.__jenkins_username__,
                        self.__jenkins_password__,
                        destination_path,
                        self.__jenkins_ip__,
                        self.__jenkins_port__,
                        source_full_path
                    )
                commands.append(cmd)
        else:
            cut_dir_value = len(source_full_path.split('/'))
            if not path.exists(destination_path):
                self.execute_cmd(f'mkdir -p {destination_path}')
            cmd = """wget --no-parent --auth-no-challenge --cut-dirs={} -e robots=off \
                    --http-user={} --http-password={} -P {} http://{}:{}{}""".format(
                        cut_dir_value,
                        self.__jenkins_username__,
                        self.__jenkins_password__,
                        destination_path,
                        self.__jenkins_ip__,
                        self.__jenkins_port__,
                        source_full_path
                    )
            commands.append(cmd)
        for cmd in commands:
            print('Command to download files:-', cmd)
            exit_codes.append(self.execute_cmd(cmd))
        return(exit_codes)

    def execute_cmd(self, cmd):
        '''
        Function to execute the command
        '''
        self.logger.info('Running ' + BaseUtilities().get_function_name() + '(' + \
                  str(BaseUtilities().get_function_parameters_and_values()) +')') 
        if not cmd: raise(ValueError('Value for argument "cmd" cant be empty.'))
        exit_code = system(cmd)
        self.logger.info(f'Executed command: {cmd} with exit code: {exit_code}')
        return(exit_code)

    def get_jobs(self):
        '''
        This function returns the list of jobs created in jenkins server. 
        '''
        self.logger.info('Running ' + BaseUtilities().get_function_name() + '(' + \
                  str(BaseUtilities().get_function_parameters_and_values()) +')') 
        all_jobs = self.server_obj.get_jobs()
        ret = []
        if not all_jobs:
            pass
        else:
            for job in all_jobs:
                ret.append(job['name'])
        self.logger.info(f'List of jobs created on jenkins server are {ret}')
        return ret

    def get_job_info(self, name, attributes=[]):
        '''
        This function returns all the info of a selected job.
        Arguments:-
        name :- Name of the job
        return :- [dict] Dictionary of all attributes
        attributes :- Required attributes of the job in list data type. Leave it empty([]) to get all the attributes
        or choose from the available attributes.
        All attributes:- ['_class', 'actions', 'description', 'displayName', 'displayNameOrNull', 'fullDisplayName',
        'fullName', 'name', 'url', 'buildable', 'builds', 'color', 'firstBuild', 'healthReport', 'inQueue',
        'keepDependencies', 'lastBuild', 'lastCompletedBuild', 'lastFailedBuild', 'lastStableBuild', 'lastSuccessfulBuild',
        'lastUnstableBuild', 'lastUnsuccessfulBuild', 'nextBuildNumber', 'property', 'queueItem', 'concurrentBuild',
        'disabled', 'downstreamProjects', 'labelExpression', 'scm', 'upstreamProjects']
        1) get_job_info('regression_job_8_0_1', [])
        2) get_job_info('regression_job_8_0_1', ['lastCompletedBuild','healthReport'])

        '''
        self.logger.info('Running ' + BaseUtilities().get_function_name() + '(' + \
                  str(BaseUtilities().get_function_parameters_and_values()) +')') 
        job_data = self.server_obj.get_job_info(name, depth=1)
        if not attributes:
            self.logger.info(job_data)
            return job_data
        else:
            ret = {}
            for key in attributes:
                ret.update({key:job_data.get(key)})
            self.logger.info(f'Job details of job {name} : {ret}')
            return ret

    def get_jobs_build_list(self, stm_version):
        '''
        This function returns the list of jenkins build numbers that is executed so for for given stm version
        '''
        self.logger.info('Running ' + BaseUtilities().get_function_name() + '(' + \
                  str(BaseUtilities().get_function_parameters_and_values()) +')') 
        builds_list = []
        job_name = self.__jenkins_version_job_map__[stm_version]
        builds = self.get_job_info(job_name, ["builds"]).get("builds")
        for i in range(len(builds)):
            build_number = builds[i]["number"]
            if not self.check_build_is_aborted(builds, i):
                builds_list.append(build_number)
            else:
                self.logger.error(f"Build number {build_number} aborted, Hence ignoring the build")
        self.logger.info(f'Build list of job {job_name}: ')
        return builds_list
 
    def check_build_is_aborted(self, builds, i):
        actions = builds[i]["actions"]      #list of dictionaries
        abort = True
        for action in actions:
            if not bool(action): continue 
            if action['_class'] == "hudson.plugins.robot.RobotBuildAction":    
                 abort = False
                 break
            else:
                 continue
        if abort:
            return True
        else:
            return False
                   
    def get_latest_build_number(self, stm_version):
        '''
        This function returns the last executed build number of the given job 
        '''
        self.logger.info('Running ' + BaseUtilities().get_function_name() + '(' + \
                  str(BaseUtilities().get_function_parameters_and_values()) +')') 
        job_name = self.__jenkins_version_job_map__[stm_version]
        latest_build_number = (self.get_job_info(job_name,["lastCompletedBuild"]).get("lastCompletedBuild"))["number"]
        return latest_build_number

    def get_current_jenkins_build_mappings(self, stm_version):
        available_jenkins_maps = self.__sbuild_jbuild_map__[stm_version].values()
        return sum(available_jenkins_maps, [])

    def build_vs_pass_percentage_test(self, stm_version):
        '''
        Dummy function used for version testing
        '''
        self.logger.info('Running ' + BaseUtilities().get_function_name() + '(' + \
                  str(BaseUtilities().get_function_parameters_and_values()) +')') 
        if stm_version == "8_0_1":
            build_pass = {
                 1870 : 80,
                 1871 : 82.5,
                 1872 : 88,
                 1873 : 80,
                 1874 : 82,
                 1875 : 85,
                 1876 : 88.5,
                 1877 : 80,
                 1878 : 80,
                 1879 : 88,
                 1880 : 91
                 }
        elif stm_version == "7_3_1":
            build_pass = {
                 1570 : 80,
                 1571 : 82.5,
                 1572 : 88,
                 1573 : 80,
                 1574 : 82,
                 1575 : 85,
                 1576 : 88.5,
                 1577 : 80,
                 1578 : 80,
                 1579 : 88,
                 1580 : 91
                 }
        else:
            self.logger.error('Unsupported argument specified.')
            build_pass = {}
        return build_pass

    def get_all_stm_builds(self, stm_version):
        '''
        This function returns the list of stm build numbers that is executed so for for given stm version
        '''
        self.logger.info('Running ' + BaseUtilities().get_function_name() + '(' + \
                  str(BaseUtilities().get_function_parameters_and_values()) +')') 
        builds_list = []
        with open(self.__build_map_filepath__) as fobj:
            map_data = json.load(fobj)
            builds_list = list(map_data[stm_version].keys())
        return builds_list

if __name__ == '__main__':
    obj = JenkinsUtilities()
    # for k in obj.get_job_info('regression_8_0_1')['builds']:
    #      print(k, end='\n\n')
    # print(obj.download_log_files_wget(stm_version='8_0_1', job_name='regression_8_0_1', job_build_num=8))
    #obj.download_log_files_wget('7_3_1')
    #obj.get_job_info("regression_8_0_1")  
    #obj.get_jobs_build_list("regression_8_0_1")    
    #obj.get_jobs_build_list("regression_8_0_1")
    #obj.get_latest_build_number("8_0_1") 
    #obj.get_job_info('regression_8_0_1')
    #obj.get_jobs_build_list('regression_8_0_1')
    