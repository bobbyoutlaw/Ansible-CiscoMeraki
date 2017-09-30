## Ansible Module: Cisco Meraki
This module is for use with Cisco Meraki dashboard API.  Meraki uses a unique structure and terminology that slightly differs from traditional networking.  The goal is retrieve a comprehensive set of network related facts from a specific Meraki organization

`meraki.py` is to be used a module_utils library.  it handles basic API requests to meraki dashboard and few handy queries to retrieve a list of networks in an organization or list of devices in a network.

`meraki_network_facts.py` only retrieves data about a specific organization.  it does to make changes to any configuration.  More modules to come.

### Requirements

https://documentation.meraki.com/zGeneral_Administration/Other_Topics/The_Cisco_Meraki_Dashboard_API

### Examples

`ansible-playbook test.yaml`


using a vault encryption for `vars/keys.yaml` for API key protection

`ansible-playbook test.yaml --ask-vault-pass`

```

- name: gather general facts about networks belonging to organization
  meraki_network_facts:
    api_key: 123456789A
    dashboard: dashboard.meraki.com
    organization: 552400
    serial: Q2XX-XXXX-XXXX


- name: gather vlan, client and site to site vpn facts about specifc networks
  meraki_network_facts:
    api_key: 123456789A
    organization: 552400
    networkid: N_1234"
    resources:
          - vlans
          - clients
          - s2svpn

api-endpoints:
  description: nested dictionary of all URL iterated to retrieve state data
  returned: always
  type: dictionary
stdout:
    clients:
      description: List the clients of a device, up to a maximum of a month ago.
      returned: always
      type: list
    network:
      description: List the networks in an organization
      returned: always
      type: list
    network_neighbors:
      description: List the devices in a network
      returned: always
      type: list
    uplinks:
      description: Return an array containing the uplink information for a device.
      returned: always
      type: list
    routes:
      description: List the static routes for this network
      returned: always
      type: list

organizations:
    description: list of networks that belong to organization
    returned: always
    type: list
    sample: {
        "ansible_facts": {
            "api-endpoints": {
                "https://n126.meraki.com/api/v0/devices/Q2XX-XXXX-XXXX/clients?timespan=86400": 200,
                "https://n126.meraki.com/api/v0/networks/N_1234": 200,
                "https://n126.meraki.com/api/v0/networks/N_1234/devices": 200,
                "https://n126.meraki.com/api/v0/networks/N_1234/devices/Q2XX-XXXX-XXXX": 200,
                "https://n126.meraki.com/api/v0/networks/N_1234/devices/Q2XX-XXXX-XXXX/uplink": 200,
                "https://n126.meraki.com/api/v0/organizations/552400/inventory": 200
            },
            "stdout": {
                "clients-Q2XX-XXXX-XXXX": [
                    {
                        "description": null,
                        "dhcpHostname": null,
                        "id": "myPC",
                        "ip": "192.168.20.64",
                        "mac": "24:e9:b3:26:1e:03",
                        "mdnsName": null,
                        "usage": {
                            "recv": 559974.4407867091,
                            "sent": 213858.6550663103
                        },
                        "vlan": ""
                    }
                ],
                "network": {
                    "id": "N_1234",
                    "name": "Branch2313",
                    "organizationId": "552400",
                    "tags": "",
                    "timeZone": "America/Los_Angeles",
                    "type": "appliance"
                },
                "network_neighbors": [
                    {
                        "address": "123 Main St, ME 0000",
                        "lat": 42.3190961,
                        "lng": -83.6827825,
                        "mac": "00:18:0a:85:96:c8",
                        "model": "MX100",
                        "name": null,
                        "networkId": "N_1234",
                        "serial": "Q2XX-XXXX-XXXX",
                        "tags": " recently-added ",
                        "wan1Ip": "192.168.8.9",
                        "wan2Ip": null
                    },
                    {
                        "address": "123 Main St, ME 0000",
                        "lat": 42.3190961,
                        "lng": -83.6827825,
                        "mac": "00:18:0a:85:94:58",
                        "model": "MX100",
                        "name": null,
                        "networkId": "N_1234",
                        "serial": "Q3XX-XXXX-XXXX",
                        "tags": " recently-added ",
                        "wan1Ip": "192.168.8.10",
                        "wan2Ip": null
                    }
                ],
                "uplinks-Q2XX-XXXX-XXXX": [
                    {
                        "dns": "192.168.33.110, 192.168.33.111",
                        "gateway": "192.168.8.1",
                        "interface": "WAN 1",
                        "ip": "192.168.8.9",
                        "publicIp": "1.2.3.4",
                        "status": "Active",
                        "usingStaticIp": true
                    }
                ],
                "uplinks-Q3XX-XXXX-XXXX": [
                    {
                        "dns": "192.168.33.110, 192.168.33.111",
                        "gateway": "192.168.7.1",
                        "interface": "WAN 1",
                        "ip": "192.168.7.9",
                        "publicIp": "2.2.3.4",
                        "status": "Active",
                        "usingStaticIp": true
                    }
                ]
            }


```

#### meraki_network_facts documentation

```
module: meraki_network_facts
short_description: returns facts about meraki network or device object.
options:
    api_key:
            description:
              - authorized API key credentials
            required: true
    dashboard:
            description:
              - URL string that indentifies API endpoint. Typically a unique
                URL is assigned to each company.
            required: false
            default: dashboard.meraki.com
    organization:
            description:
              - 6 digit string that identifies a collection of networks.
            required: true
    networkid:
            description:
              - 20 char string that identifies a container of devices,
                configs, stats, and any client-device information.
                Multiple devices may belong to one netork.
                One of options [networkid, networkname, serial] is required
            required: false
    networkname:
            description:
              - similar to networkid, but uses friendly name string.
                identifies a container of devices, configs, stats,
                and any client-device information. Multiple devices
                may belong to one netork.
                One of options [networkid, networkname, serial] is required
            required: false
    serial:
            description:
                - string that uniquely identifies a specific device.
                  only configs and stats of single device information
                  will be returned.
                  One of options [networkid, networkname, serial] is required
            required: false
    timespan:
            description:
                - The timespan for which clients will be fetched.
                  Must be in seconds and less than or equal to a month
                  (2592000 seconds).
            required: False
            default: 86400
    resources:
            type: list
            description:
                - return values on specific network and /or device resoures. Such as
                  vlans, clients, s2svpn, ssids, etc
            required: False
            default: (all values)
    headers:
            type: Boolean
            description:
                - Useful debugging. displays URL header sent to meraki dashboard.
            required: False
            default: False
```
