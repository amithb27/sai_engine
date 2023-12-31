"""
    This file contains APIs required for the automation operations to run seamlessly.
"""
import subprocess

class testbed_controller():
    def __init__(self):
        self.jenkins_ip = '10.1.9.6'
        self.jenkins_user = 'jenkins'
        self.__jenkins_pool_path = "/home/jenkins/files-used-by-robot-regression/testbed_pool/"

    def send(self,cmd,cwd=None, dont=None, shell=False):
        cmd='sshpass ssh -o ConnectTimeout=30  -o StrictHostKeyChecking=no {}@{} {}'.format(self.jenkins_user,self.jenkins_ip,cmd)
        if dont is None:
            cmd_list = cmd.split()
        else:
            cmd_list = []
            shell=True
            cmd_list.append(cmd)
        process = subprocess.Popen(
            cmd_list,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=shell, cwd=cwd
        )
        stdout, stderr = process.communicate()
        print('CMD->{}'.format(cmd))
        if process.returncode != 0 or stderr:
            # print('OUTPUT ERROR->{}'.format(str(stderr)))
            return 'Error:- {}'.format(stderr.decode('utf-8')+stdout.decode('utf-8'))
        else:
            # print('OUTPUT->{}'.format(stdout))
            return stdout

    def is_testbed_free(self, stm_host):
        """_summary_

        Args:
            stm_host (list or str): It can be a single stm ip as string
                                or a list of stm ip addresses

        Returns:
            True = Testbed is free.
            False = Testbed is reserved.
            
            dict: data = [{
                    "stm" : "10_1_11_80",
                    "result" : False,
                    "body" : {"user":"amith","message":"testing"}
                },
                {
                    "stm" : "10_1_11_76",
                    "result" : True,
                    "body" : {}
                }
            ]
        """
        print('Checking if testbed is free', stm_host)
        if isinstance(stm_host, str):
            stm_host = [stm_host]
        data = []
        file_exists_cmd = "cat " + ' '.join([self.__jenkins_pool_path+host for host in stm_host])
        # print("Command is", file_exists_cmd)
        ret = self.send(file_exists_cmd)
        # print('Output', ret)
        ret = ret.decode('utf-8') if type(ret) != str else ret
        # print('Output after type conversion', ret)
        ret_split = ret.split('\n')
        # print('Output after split', ret_split)
        for dev in stm_host:
            for output_line in ret_split:
                dev_data = {
                    "stm": "",
                    "result": False,
                    "user": "",
                    "message": "",
                }
                if dev in output_line:
                    if 'No such file' in output_line:
                        dev_data['stm'] = dev
                        dev_data['result'] = True
                        data.append(dev_data)
                    else:
                        dev_data['stm'] = dev
                        dev_data['result'] = False
                        dev_data['user'] = output_line.split(';')[0]
                        dev_data['message'] = output_line.split(';')[1]
                        data.append(dev_data)
        print('Testbed status:-', data)
        return data
        
    def testbed_reserve(self, stm_host, user, message):
        reserve_cmd = "echo '{};{};{}' | cat > {}{}".format(
            user,message,str(stm_host),self.__jenkins_pool_path,str(stm_host)
        )
        if self.is_testbed_free(stm_host)[0]['result']:
            print('Reserved testbed:- ', stm_host)
            ret = self.send(reserve_cmd)
            if not ret:
                return True
            else:
                print("Testbed is free but reservation failed:- {}".format(ret))
                return False
        else:
            print('Testbed already reserved:- ', stm_host)
            return False
        
    def testbed_release(self, stm_host):
        release_cmd = 'rm ' + self.__jenkins_pool_path + str(stm_host)
        print('Releasing testbed command:- ', release_cmd)
        ret = self.send(release_cmd)
        if 'No such file' in str(ret):
            return True
        elif not ret:
            return True
        else:
            return False
