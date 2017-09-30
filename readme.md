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
