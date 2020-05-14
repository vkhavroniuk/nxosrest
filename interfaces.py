import json
import requests
from urllib3.exceptions import InsecureRequestWarning
from dataclasses import dataclass

@dataclass
class RequestsCustomError(Exception):
    ''' Class for Custom Exception'''
    status_code: int = 0

@dataclass
class Switch(object):
    ''' Class for NX-OS Switch node'''
    s = requests.Session()
    user: str
    password: str
    mgmtip: str

    def login(self):
        self.s.auth = (self.user, self.password)
        self.s.verify = False
        self.s.headers.update({'Content-Type' : 'application/json'})

    def post(self,data):
        url = 'https://'+self.mgmtip+'/ins'
        try:
            ret = self.s.request('post', url, data=json.dumps(data))
        except requests.exceptions.RequestException as e:
            return RequestsCustomError(999)
        return ret
    
def main():
    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

    ip='192.168.123.230'
    user='admin'
    password='admin'
    data = {'ins_api': {'chunk': '0', 'version': '1.0', 'sid': '1', 'input': 'show interface status', 'type': 'cli_show', 'output_format': 'json'}}

    nx = Switch(user,password,ip)
    nx.login()
    r = nx.post(data)
    if r.status_code == 200:
        output = json.loads(r.text)['ins_api']['outputs']['output']['body']['TABLE_interface']['ROW_interface']
        print(output)
        for i in output:
#            for key,value in i.items():
#                print(key,value)
            print(i['interface'],i['state'],'switchport' if i['vlan']!='routed' else 'routed')
        
    else:
        print('Error Code: ' + str(r.status_code))

if __name__ == '__main__':
    main()
