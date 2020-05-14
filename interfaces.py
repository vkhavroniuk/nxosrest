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

    def cli_show(self,cmd):
        data = {'ins_api': {'chunk': '0', 'version': '1.0', 'sid': '1',
                            'input': 'show ver', 'type': 'cli_show',
                            'output_format': 'json'}}
        data['ins_api']['input'] = cmd
        url = 'https://'+self.mgmtip+'/ins'
        try:
            ret = self.s.request('post', url, data=json.dumps(data))
        except requests.exceptions.RequestException as e:
            return RequestsCustomError(999)

        if ret.status_code == 200:
            return json.loads(ret.text)['ins_api']['outputs']['output']['body']
        
    
def main():
    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

    ip='1.1.1.1'
    user='admin'
    password='admin'
   
    nx = Switch(user,password,ip)
    nx.login()

    intf_status = nx.cli_show('show interface status')['TABLE_interface']['ROW_interface']
    for i in intf_status:
       print(i['interface'],i['state'],'switchport' if i['vlan']!='routed' else 'routed')


    cdp = nx.cli_show('show cdp neighbors')['TABLE_cdp_neighbor_brief_info']['ROW_cdp_neighbor_brief_info']
    for i in cdp:
        print(i['intf_id'],i['device_id'])


if __name__ == '__main__':
    main()
