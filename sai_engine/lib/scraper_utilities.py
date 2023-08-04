"""
Author: Amith Bhonsle (amith@saisei.com)
Description:
"""
from os import path
from django.conf import settings
from bs4 import BeautifulSoup
from .base_utilities import BaseUtilities
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
import json
import pylogging

class webScraper_utilities(object):
    """
    Base class that contains all the basic functions required for web_scraping.
    """
    def __init__(self):
        '''
        Function to initialise all the parameter values and create connection object.
        '''  
        #self.__base_dir__ = "/home/jenkins/sailytics/production_server/sailytics-django/sai_engine"
        self.__base_dir__ = str(settings.BASE_DIR)
        self.__config_filepath__ = self.__base_dir__ + '/sai_engine/data/config.json'
        with open(self.__config_filepath__, 'r') as fobj:
            self.node_configs = json.load(fobj)['NODES']
        self.__jenkins_log_path_map__ = self.node_configs['jenkins']['ver_log_path_map']
        self.__jenkins_valid_scripts__ = self.node_configs['jenkins']['valid_script_names']
        self.__jenkins_script_log_map__ = self.node_configs['jenkins']['script_log_map']
        self.__jenkins_version_job_map__ = self.node_configs['jenkins']["version_job_map"]    
        self.__scraper_log_filepath__ = self.__base_dir__ + self.node_configs['pylogger']['web_scraper_log_file']
        self.logger = pylogging.PyLogging(LOG_FILE_PATH = self.__scraper_log_filepath__ + '/log_file_', LOG_FILE_FORMAT='%d-%m-%Y %H:%M')
        
    def get_page_url(self, stm_version, script_name, job_build_num):
        '''
        Gets the page url, builds the jenkins url using required parameter. Url of the log file or report file that needto be scraped        
        stm_version   : Specifies the stm version, so that the required job data is accessed
                        Acceptable values = '7_3_1' or '8_0_1'
        job_build_num : Specifies the build number of job whose data is to be accessed
        script_name   : Name of the script
        '''
        self.logger.info('Running ' + BaseUtilities().get_function_name() + '(' + \
                  str(BaseUtilities().get_function_parameters_and_values()) +')') 
        self.logger.info(f'Validating script name {script_name}')
        if not self.validate_script(stm_version, script_name):
            self.logger.error(f'{stm_version} and {script_name} seem to have ambiguity, Check if you have valid script_name provided')
            raise(ValueError(f'Value {stm_version} and {script_name} seem to have ambiguity.'))
        url = self.__base_dir__ + self.__jenkins_log_path_map__[stm_version] + job_build_num + '/' + self.__jenkins_script_log_map__[script_name]
        self.logger.info(f'Page Url : {url}')
        print('This is get page UURL -----------------', url)
        return url

    def get_webdriver(self, url):
        """
        Gets the webdriver instance to the given url
        """
        self.logger.info('Running ' + BaseUtilities().get_function_name() + '(' + \
                  str(BaseUtilities().get_function_parameters_and_values()) +')') 
        opts = ChromeOptions()
        opts.add_argument("--headless")
        opts.add_argument("--disable-gpu")
        driver = webdriver.Chrome(options=opts)
        driver.get("file://" + url)
        return driver

    def click_element(self, driver, element_locator_type, value):
        """
        Clicks element with attribute_name=element_locator_type and attribute value = value
        element_locator_type : specify which attribute is used to locate elements on a page.
        value : specify attribute value
        """
        self.logger.info('Running ' + BaseUtilities().get_function_name() + '(' + \
                  str(BaseUtilities().get_function_parameters_and_values()) +')') 
        #Find an element on the page with an onclick_event()
        if element_locator_type == "ID":
            element = driver.find_element(By.ID, value) 
        if element_locator_type == "NAME":
            element = driver.find_element(By.NAME, value)
        if element_locator_type == "CLASS_NAME":
            element = driver.find_element(By.CLASS_NAME, value)
        if element_locator_type == "TAG_NAME":
            element = driver.find_element(By.TAG_NAME, value)
        if element_locator_type == "CSS_SELECTOR":
            element = driver.find_element(By.CSS_SELECTOR, value)
        if element_locator_type == "XPATH":
            element = driver.find_element(By.XPATH, value)
        if element_locator_type == "LINK_TEXT":
            element = driver.find_element(By.LINK_TEXT, value)
        if element_locator_type == "PARTIAL_LINK_TEXT":
            element = driver.find_element(By.PARTIAL_LINK_TEXT, value)
        element.click()                                                #Clicks element
        self.logger.info(f'Element clicked {element.get_attribute("outerHTML")}')
        return driver

    def validate_script(self, stm_ver, script_name):
        '''
        Validates if the script name matches the one specified in jenkins_valid_scripts for a particular stm_version
        '''
        self.logger.info('Running ' + BaseUtilities().get_function_name() + '(' + \
                  str(BaseUtilities().get_function_parameters_and_values()) +')') 
        if script_name in self.__jenkins_valid_scripts__[stm_ver]:
            return True
        else:
            return False
    
    def validate_log_file(self, full_path):
        '''
        Validates if the log file exists in our jenkins log directory
        '''
        self.logger.info('Running ' + BaseUtilities().get_function_name() + '(' + \
                  str(BaseUtilities().get_function_parameters_and_values()) +')') 
        if self.check_file_exists(full_path):
            return True
        else:
            self.logger.error(f'Log file , {full_path} does not exist. Please recheck if file is downloaded')
            return False

    def check_file_exists(self, full_path):
        '''
        Checks if the file with the path exists
        '''
        self.logger.info('Running ' + BaseUtilities().get_function_name() + '(' + \
                  str(BaseUtilities().get_function_parameters_and_values()) +')') 
        if path.exists(str(full_path)):
            return True
        else:
            return False

    def write_data(self, data):
        """
        Writes data to a file scrape_data.json that stores all data that is scraped
        data : Data that is to be stored takes dictionary type
        """
        self.logger.info('Running ' + BaseUtilities().get_function_name() + '(' + \
                  str(BaseUtilities().get_function_parameters_and_values()) +')') 
        # Serializing json
        json_object = json.dumps(data, indent=4)
 
        # Writing to scrape_data.json
        with open(self.__filename__, "w") as outfile:
             outfile.write(json_object)

    def read_data(self):
        """
        Read data from scrape_data.json file to check if data to be scrapped already exists in a file
        """
        self.logger.info('Running ' + BaseUtilities().get_function_name() + '(' + \
                  str(BaseUtilities().get_function_parameters_and_values()) +')') 
        with open(self.__filename__, 'r') as openfile:                 # Opening JSON file
             json_object = json.load(openfile)                         # Reading from json file
        return json_object 

    def get_page_handle(self,url):
        self.logger.info('Running ' + BaseUtilities().get_function_name() + '(' + \
                  str(BaseUtilities().get_function_parameters_and_values()) +')') 
        driver = self.get_webdriver(url)
        page = driver.page_source
        return BeautifulSoup(page, 'html.parser')
    
    
if __name__ == '__main__':
    obj = webScraper_utilities()
    obj.get_page_url('8_0_1', 8, 'accesspoints')
