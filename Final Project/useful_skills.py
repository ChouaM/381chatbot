import os
import sys
### For RESTCONF
import requests
import json

def get_arp(url_base,headers,username,password):
    url = url_base + "/data/Cisco-IOS-XE-arp-oper:arp-data/"

    # this statement performs a GET on the specified url
    response = requests.get(url,
                            auth=(username, password),
                            headers=headers,
                            verify=False
                            )

    # return the json as text
    return response.json()['Cisco-IOS-XE-arp-oper:arp-data']['arp-vrf'][0]['arp-oper']


def get_sys_info(url_base,headers,username,password):
    url = url_base + "/data/Cisco-IOS-XE-device-hardware-oper:device-hardware-data/"

    # this statement performs a GET on the specified url
    response = requests.get(url,
                            auth=(username, password),
                            headers=headers,
                            verify=False
                            )

    # return the json as text
    return response.json()["Cisco-IOS-XE-device-hardware-oper:device-hardware-data"]["device-hardware"]

# Function to retrieve the list of interfaces on a device
def get_configured_interfaces(url_base,headers,username,password):
    url = url_base + "/data/ietf-interfaces:interfaces"

    # this statement performs a GET on the specified url
    response = requests.get(url,
                            auth=(username, password),
                            headers=headers,
                            verify=False
                            )
    return response.json()["ietf-interfaces:interfaces"]["interface"]


if __name__ == "__main__":
    import routers
    # Router Info 
    device_address = routers.router['host']
    device_username = routers.router['username']
    device_password = routers.router['password']
    # RESTCONF Setup
    port = '443'
    url_base = "https://{h}/restconf".format(h=device_address)
    headers = {'Content-Type': 'application/yang-data+json',
            'Accept': 'application/yang-data+json'}

    intf_list = get_configured_interfaces(url_base, headers,device_username,device_password)
    for intf in intf_list:
        print("Name:{}" .format(intf["name"]))
        try:
            print("IP Address:{}\{}\n".format(intf["ietf-ip:ipv4"]["address"][0]["ip"],
                                intf["ietf-ip:ipv4"]["address"][0]["netmask"]))
        except KeyError:
            print("IP Address: UNCONFIGURED\n")


def restconf_project(url_base,headers,username,password):
    url = url_base + "/data/Cisco-IOS-XE-memory-oper:memory-statistics/memory-statistic=Processor"
    response = requests.get(url, auth=(username, password), headers=headers, verify=False)
    data = response.json()["Cisco-IOS-XE-memory-oper:memory-statistic"]
    print("Name: ", data["name"])
    used, free = 0,0
    try:
        used = int(data["used-memory"])
        free = int(data["free-memory"])
    except KeyError:
        print("Json Error")
        used_mem = (used/(used+free)) * 100
        return (used_mem)
    


#Function to retreive the CPU status on a device at five seconds
def get_cpu(url_base,headers,username,password):
    url = url_base + "/data/Cisco-IOS-XE-process-cpu-oper:cpu-usage/cpu-utilization/five-seconds" #get_cpu(5sec)

    #Performs a GET on the specified URL
    response = requests.get(url,auth=(username,password),headers=headers,verify=False)

    print(url)
    return response.json()['Cisco-IOS-XE-process-cpu-oper:five-seconds']