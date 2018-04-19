import json
import requests
import http.client
import urllib3
from ansible.module_utils import api
from ansible.module_utils.basic import *


def meraki_argument_spec():
    return dict(
    dashboard=dict(type='str', default='dashboard.meraki.com'),
    timespan=dict(type='str', default='86400'),
    api_key=dict(type='str', required=True),
    resources=dict(type='list',
        #choices=['clients', 'uplinks', 'switchports', 'neighbors', 'networks', 'devices'].items,
        default=['clients', 'uplinks', 'switchports', 'neighbors', 'networks', 'devices'],
        ),
    headers=dict(type='bool', default=False),
    )

class DashApi:
    def __init__(self, module):
        self.module = module
        self.params = module.params
        self.headers = {"Content-Type": "application/json"}
        self.headers['x-cisco-meraki-api-key'] = self.params.get('api_key')
        self.baseurl = "https://" + self.params.get('dashboard') + "/api/v0"
        self.organization = self.params.get('organization')
        self.orgname = self.params.get('organization_name')
        self.networkId = self.params.get('networkid')
        self.networkname = self.params.get('networkname')
        self.serial = self.params.get('serial')
        self.timeout = self.params.get('timeout')
        self.timespan = self.params.get('timespan')
        self.resourceslist = self.params.get('resources')
        self.result = {'ansible_facts':{'stdout': {}, 'api-endpoints': {} }}
        self.result_key = ''
        self.urldict={}

        try:
            requests.packages.urllib3.disable_warnings()
        except AttributeError:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def dec_network_elements(self):
        return dict(
        {'neighbors':self.get_device,
        'routes':self.get_route,
        'vlans':self.get_vlan,
        'networks':self.get_network,
        'devices':self.get_device,
            }
        )

    def network_elements(self):
        return dict({
        'neighbors':{
            'action':self.get_device,
            },
        'routes':{
            'action':self.get_route,
            },
        'vlans':{
            'action':self.get_vlan,
            },
        'networks':{
            'action':self.get_network,
            },
        'devices':{
            'action':self.get_device,
            },
        'ssids':{
            'action':self.get_ssid,
            },
        's2svpn':{
            'action':self.get_s2svpn,
            },
        })

    def device_elements(self):
        return dict({
        'clients':{
            'action':self.get_client,
            'model':['MS','MX','MR'],
            },
        'uplinks':{
            'action':self.get_uplink,
            'model':['MX'],
            },
        'switchPorts':{
            'action':self.get_switchport,
             'model':['MX'],
            },
         }
        )

    def resource_iterator(self,serial=None, networkid=None, model=None):
        d = self.device_elements()
        n = self.network_elements()
        for item in self.resourceslist:
            if (item in list(d.keys())) and (serial is not None) and (model is not None):
                d[item]['action'](serial=serial, model=model)
            elif (item in list(n.keys())) and (networkid is not None):
                n[item]['action'](networks=networkid)
            #else:
                #self.result['ansible_facts']['stdout'] = [serial, model]
        return




    QUERY = '''
    '''
    def _query (self, datalist, fkey, rrecord, alias=None):
        NOTES = '''
        (data, {'networkId':'L_567890'}, ['serial','model'], alias='mac')

        takes in a list and uses FKEY dictionary to find matching k,v pair
        returns data values that match values in RRECORD list,
        ALIAS is used to create unique top-level keys when needed.

        above example will iterate dataset and match on {'networkId':'L_567890'}
        it will iterate a through ['serial,'model'] and return respective values from dataset,
        also the value for 'mac' key will be store and returned as top-level keys
         [
            {
            "00:18:0a:85:94:58": [
                {"serial": "Q2JN-XXXX-YYYY"},
                {"model": "MX100"}
            ]
        },
            {
            "00:18:0a:85:96:c8": [
                {"serial": "Q2JN-YYYY-ZZZZ"},
                {"model": "MX100"}
            ]
        }
       ]
        '''
        if not isinstance(datalist, list):
            newlist =[]
            newlist.append(datalist)
            datalist = newlist
        d={}
        l=[]
        [(k,v)] = list(fkey.items())
        for item in datalist:
            eachlist=[]
            if item[k] == v:
                for each in rrecord:
                    if alias is None:
                        d[v]={each:item[each]}
                    else:
                        eachlist.append({each:item[each]})
                    if len(rrecord) > 1:
                        d.update({item[alias]:eachlist})
                l.append(d)
                d = {}
        if not l:
            self._query_err(value=v)
        return l

    def _query_err(self, value):
        self.module.fail_json(msg="Query value % s not found" %value)
        return

    def net_nameid_query(self, name):
        # returns an ID from Network Inventory matching Network Name
        data = self.get_orgnetworks('query')
        datalist = self._query(data, {'name':name}, ['id'])
        self.networkId = datalist[0][name]['id']
        return self.networkId

    def org_nameid_query(self, name):
        # returns an ID from Organization Inventory matching Org Name
        data = self.get_organizations('query')
        datalist = self._query(data, {'name':name}, ['id'])
        self.organization = str(datalist[0][name]['id'])
        return self.organization

    def device_idmodel_query(self, serial):
        # returns  Model Number from Device Inventory matching Serial
        data = self.get_networkdevices('query')
        datalist = self._query(data, {'serial':serial}, ['model'])
        keyname=list(datalist[0].keys())
        topkey=str(keyname[0])
        model = datalist[0][serial]['model']
        return model

    def device_netid_query(self, network):
        # returns an hash of Serial, Model from Device Inventory matching NetworkID
        # mac address is used as top-level key
        data = self.get_device('query')
        datalist = self._query(data, {'networkId':network}, ['serial','model'], alias='mac')
        keyname=list(datalist[0].keys())
        topkey=str(keyname[0])
        return datalist

    def net_serialid_query(self, serial):
        # returns Serial Number from Organization Inventory matching NetworkID
        data = self.get_orginventory('query')
        datalist = self._query(data, {'serial':serial}, ['networkId'])
        keyname=list(datalist[0].keys())
        topkey=str(keyname[0])
        self.networkId = datalist[0][serial]['networkId']
        return self.networkId





    ELEMENTS = '''
    '''
    def get_uplink (self, qkey='uplinks',serial='',model=''):
        #Return an array containing the uplink information for a device.
        #'https://dashboard.meraki.com/api/v0/networks/[networkId]/devices/[serial]/uplink'

        d = self.device_elements()
        if model[:2] in d[qkey]['model']:
            if serial:
                self.serial = serial
            self.urldict[qkey + "-" + self.serial] = '/networks/'+ self.networkId + '/devices/'+ self.serial + '/uplink'
            results = self.build_url()
        else:
            results = None
        return results

    def get_client (self, qkey='clients',serial='',model=''):
        #List the clients of a device, up to a maximum of a month ago. The usage
        #of each client is returned in kilobytes. If the device is a switch, the
        #switchport is returned; otherwise the switchport field is null.
        #'https://dashboard.meraki.com/api/v0/devices/[serial]/clients?timespan=86400'

        d = self.device_elements()
        if model[:2] in d[qkey]['model']:
            if serial:
                self.serial = serial
                self.urldict[qkey + "-" + self.serial] = '/devices/'+ self.serial +'/clients?timespan='+ self.timespan
                results = self.build_url()
        else:
            results = None
        return results

    def get_switchport (self, model, qkey='switchPorts',serial=''):
        #List the switch ports for a switch
        #'https://dashboard.meraki.com/api/v0/devices/[serial]/switchPorts'

        d = self.device_elements()
        if model[:2] in d[qkey]['model']:
            if serial:
                self.serial = serial
                self.urldict[qkey] = '/devices/'+ self.serial + '/switchPorts'
                results = self.build_url()
        else:
            results = None
        return results

    def get_device (self, qkey='network_neighbors', networks=''):
        #List devices in a network
        #'https://dashboard.meraki.com/api/v0/networks/[networkId]/devices'
        if networks:
            self.networkId = networks
        self.urldict[qkey] = '/networks/'+ self.networkId + '/devices'
        results = self.build_url()
        return results

    def get_ssid (self, qkey='ssids', networks=''):
        #List devices in a network
        #'https://dashboard.meraki.com/api/v0/networks/[networkId]/ssids'
        if networks:
            self.networkId = networks
        self.urldict[qkey] = '/networks/'+ self.networkId + '/ssids'
        results = self.build_url()
        return results

    def get_network (self, qkey='network',networks=''):
        #Return a network
        #'https://dashboard.meraki.com/api/v0/networks/[id]'
        if networks:
            self.networkId = networks
        self.urldict[qkey] = '/networks/'+ self.networkId
        results = self.build_url()
        return results

    def get_networkdevices(self, qkey='networkdevices',networks=''):
        #Return a single device
        #'https://dashboard.meraki.com/api/v0/networks/[networkId]/devices/[serial]'
        if networks:
            self.networkId = networks
        self.urldict[qkey] = '/networks/'+ self.networkId + '/devices/'+ self.serial
        results = self.build_url()
        return results


    def get_route (self, qkey='routes',networks=''):
        #List the static routes for this network
        #'https://dashboard.meraki.com/api/v0/networks/[networkId]/staticRoutes'
        if networks:
            self.networkId = networks
        self.urldict[qkey] = '/networks/'+ self.networkId + '/staticRoutes'
        results = self.build_url()
        return results

    def get_vlan (self, qkey='vlans',networks=''):
        #List the VLANs for this network
        #'https://dashboard.meraki.com/api/v0/networks/[networkId]/vlans'
        if networks:
            self.networkId = networks
        self.urldict[qkey] = '/networks/'+ self.networkId +'/vlans'
        results = self.build_url()
        return results

    def get_s2svpn (self, qkey='s2svpn', networks=''):
        #List devices in a network
        #'https://dashboard.meraki.com/api/v0/networks/[id]/siteToSiteVpn'
        if networks:
            self.networkId = networks
        self.urldict[qkey] = '/networks/'+ self.networkId + '/siteToSiteVpn'
        results = self.build_url()
        return results



    RESOURCES = '''
    '''
    def get_organizations (self, qkey='organizations'):
        #List the organizations that API key has privileges on
        #'https://dashboard.meraki.com/api/v0/organizations'
        self.urldict[qkey] = '/organizations'
        results = self.build_url()
        return results

    def get_orgnetworks(self, qkey='orgnetworks'):
        #List the networks in an organization
        #'https://dashboard.meraki.com/api/v0/organizations/[organizationId]/networks'
        self.urldict[qkey] = '/organizations/'+ self.organization +'/networks'
        results = self.build_url()
        return results

    def get_orginventory (self, qkey='inventory'):
        #Return the inventory for an organization
        #'https://dashboard.meraki.com/api/v0/organizations/[id]/inventory'
        self.urldict[qkey] = '/organizations/'+ self.organization +'/inventory'
        results = self.build_url()
        return results





    REQUESTS = '''
    '''
    def build_url (self):
        for k, v in list(self.urldict.items()):
            self.resource = str(v)
            self.result_key = str(k)
            results = self.api_get()
        return results

    def dep_build_url (self, urldict=None):
        if urldict is None:
            urldict = self.urldict
        for k, v in list(urldict.items()):
            self.resource = str(v)
            self.result_key = str(k)
            results = self.api_get()
        return results

    def check_api_failure(self, thresholdv=.5000):
        #if more than half of API queries fail or return error
        #the ansible module will return failure.
        f= int()
        l = len(self.result['ansible_facts']['api-endpoints'])
        for k,v in list(self.result['ansible_facts']['api-endpoints'].items()):
            if v != 200:
                f += 1
        d = f/float(l)
        threshold = float(thresholdv)
        if d > threshold:
            self.result['ansible_facts']['stdout'] ='ERROR: exceeded URL request error threshold: '+str(threshold*100)+'%'
            self.module.fail_json(msg=self.result)
        return

    def api_get(self):
        url = self.baseurl + self.resource
        self.result['ansible_facts']['stdout'][self.result_key]={}
        try:
            response = requests.request("GET", url, headers=self.headers, verify=False, timeout=20.001) #need a to define acceptable timeout
            response.raise_for_status()
            self.result['ansible_facts']['stdout'][self.result_key] = response.json()
            self.result['ansible_facts']['api-endpoints'][url]=response.status_code
        except requests.Timeout as e:
            self.result['ansible_facts']['stdout'][self.result_key] = response.status_code
            self.result['ansible_facts']['attempted url'] = url
            self.module.fail_json(msg=self.result['ansible_facts']['stdout'], **self.result)
        except requests.HTTPError as e:
            if self.result_key == 'query':
                self.module.fail_json(msg='API query failed! %s' % str(e))
            else:
                self.result['ansible_facts']['api-endpoints'][url]=str(e)
            return self.result
        except requests.ConnectionError as e:
            self.result['ansible_facts']['stdout'][self.result_key] = str(e)
            self.result['ansible_facts']['attempted url'] = url
            self.module.fail_json(msg=self.result['ansible_facts']['stdout'], **self.result)
        if self.params.get('headers'):
            self.result['ansible_facts']['headers'] = response.headers
        if self.result_key == 'query':
            results = self.result['ansible_facts']['stdout'][self.result_key]
            del self.result['ansible_facts']['stdout'][self.result_key]
            return results
        return self.result
