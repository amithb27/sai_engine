'''
Author:
Description:
'''
from os import path
import scrapy
import json

class JenkinsLogSpider(scrapy.Spider):
    '''
    '''
    global start_urls
    name = 'jenkinsScrapper'
    allowed_domains = []
    start_urls = []
    def __init__(self):
        global start_urls
        with open('config.json', 'r') as fobj:
            self.node_configs = json.load(fobj)['NODES']
        self.__jenkins_log_path__ = self.node_configs['scrapy']['jenkins_log_path'] + 'log_kni.html'
        start_urls.append(self.__jenkins_log_path__)

    def load_configs(self, node):
        return self.node_configs[node]

    def validate_file(self, file_path):
        if path.exists(file_path):
            return True
        else:
            return False

    def parse(self,response):
        print(dir(response))
    
obj = JenkinsLogSpider()
obj.parse()
# print(json.load('config.json'))