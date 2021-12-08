import threading
import time
import json
import requests
import robot

# To build the table at the end
from tabulate import tabulate

### teams Bot ###
from webexteamsbot import TeamsBot
from webexteamsbot.models import Response

### Utilities Libraries
import routers
import useless_skills as useless
import useful_skills as useful
from BGP_Neighbors_Established import BGP_Neighbors_Established
from Monitor_Interfaces import MonitorInterfaces
from ansible_playbook_runner import Runner

#import paramiko/netmiko file
import Paramiko_skill as p

# Create  thread list
threads = list()
# Exit flag for threads
exit_flag = False

# Router Info 
device_address = routers.router['host']
device_username = routers.router['username']
device_password = routers.router['password']

# RESTCONF Setup
port = '443'
url_base = "https://{h}/restconf".format(h=device_address)
headers = {'Content-Type': 'application/yang-data+json',
           'Accept': 'application/yang-data+json'}

# Bot Details
bot_email = 'chouabot@webex.bot' #Fill in your Teams Bot email#
teams_token = 'YTVmMzUxMGItMjA4ZC00OWI2LThmODgtNzkyMTc0M2EzOGZkYWRhYTZiY2MtMTli_P0A1_9c947ef3-ba2a-406e-9976-6a57f8f739b7' #Fill in your Teams Bot Token#
bot_url = "https://f59f-97-90-227-95.ngrok.io" #Fill in the ngrok forwarding address#, NEED TO CHANGE EVERYTIME YOU turn off nGrok
bot_app_name = 'CNIT-381 Network Auto Chat Bot'

# Create a Bot Object
#   Note: debug mode prints out more details about processing to terminal
bot = TeamsBot(
    bot_app_name,
    teams_bot_token=teams_token,
    teams_bot_url=bot_url,
    teams_bot_email=bot_email,
    debug=True,
    webhook_resource_event=[
        {"resource": "messages", "event": "created"},
        {"resource": "attachmentActions", "event": "created"},],
)

# Create a function to respond to messages that lack any specific command
# The greeting will be friendly and suggest how folks can get started.
def greeting(incoming_msg):
    # Loopkup details about sender
    sender = bot.teams.people.get(incoming_msg.personId)

    # Create a Response object and craft a reply in Markdown.
    response = Response()
    response.markdown = "Hello {}, I'm a friendly CSR1100v assistant .  ".format(
        sender.firstName
    )
    response.markdown += "\n\nSee what I can do by asking for **/help**."
    return response

def arp_list(incoming_msg):
    """Return the arp table from device
    """
    response = Response()
    arps = useful.get_arp(url_base, headers,device_username,device_password)

    if len(arps) == 0:
        response.markdown = "I don't have any entries in my ARP table."
    else:
        response.markdown = "Here is the ARP information I know. \n\n"
        for arp in arps:
            response.markdown += "* A device with IP {} and MAC {} are available on interface {}.\n".format(
               arp['address'], arp["hardware"], arp["interface"]
            )

    return response

def sys_info(incoming_msg):
    """Return the system info
    """
    response = Response()
    info = useful.get_sys_info(url_base, headers,device_username,device_password)

    if len(info) == 0:
        response.markdown = "I don't have any information of this device"
    else:
        response.markdown = "Here is the device system information I know. \n\n"
        response.markdown += "Device type: {}.\nSerial-number: {}.\nCPU Type:{}\n\nSoftware Version:{}\n" .format(
            info['device-inventory'][0]['hw-description'], info['device-inventory'][0]["serial-number"], 
            info['device-inventory'][4]["hw-description"],info['device-system-data']['software-version'])

    return response

def get_int_ips(incoming_msg):
    """Return Interface IPs
    """
    response = Response()
    intf_list = useful.get_configured_interfaces(url_base, headers,device_username,device_password)

    if len(intf_list) == 0:
        response.markdown = "I don't have any information of this device"
    else:
        response.markdown = "Here is the list of interfaces with IPs I know. \n\n"
    for intf in intf_list:
        response.markdown +="*Name:{}\n" .format(intf["name"])
        try:
            response.markdown +="IP Address:{}\{}\n".format(intf["ietf-ip:ipv4"]["address"][0]["ip"],
                                intf["ietf-ip:ipv4"]["address"][0]["netmask"])
        except KeyError:
            response.markdown +="IP Address: UNCONFIGURED\n"
            
    return response

def check_bgp(incoming_msg):
    """Return BGP Status
    """
    response = Response()
    response.text = "Gathering BGP Information from BGP peers...\n\n"

    bgp = BGP_Neighbors_Established()
    status = bgp.setup('testbed/routers.yml')
    if status != "":
        response.text += status
        return response

    status = bgp.learn_bgp()
    if status != "":
        response.text += status

    response.text += bgp.check_bgp()

    return response

def check_int(incoming_msg):
    """Find down interfaces
    """
    response = Response()
    response.text = "Gathering  Information...\n\n"

    mon = MonitorInterfaces()
    status = mon.setup('testbed/routers.yml')
    if status != "":
        response.text += status
        return response

    status = mon.learn_interface()
    if status == "":
        response.text += "All Interfaces are OK!"
    else:
        response.text += status

    return response

def monitor_int(incoming_msg):
    """Monitor interfaces in a thread
    """
    response = Response()
    response.text = "Monitoring interfaces...\n\n"
    monitor_int_job(incoming_msg)
    th = threading.Thread(target=monitor_int_job, args=(incoming_msg,))
    threads.append(th)  # appending the thread to the list

    # starting the threads
    for th in threads:
        th.start()

    # waiting for the threads to finish
    for th in threads:
        th.join()

    return response

def monitor_int_job(incoming_msg):
    response = Response()
    msgtxt_old=""
    global exit_flag
    while exit_flag == False:
        msgtxt = check_int(incoming_msg)
        if msgtxt_old != msgtxt:
            print(msgtxt.text)
            useless.create_message(incoming_msg.roomId, msgtxt.text)
        msgtxt_old = msgtxt
        time.sleep(20)

    print("exited thread")
    exit_flag = False

    return response

def stop_monitor(incoming_msg):
    """Monitor interfaces in a thread
    """
    response = Response()
    response.text = "Stopping all Monitors...\n\n"
    global exit_flag
    exit_flag = True
    time.sleep(5)
    response.text += "Done!..\n\n"

    return response

#Ansible skill
def ansible_skill(incoming_msg):
    
    response = Response()
    #               Inventory file,  playbook file
    output = Runner('inventory.txt', 'Ansible_skill.yaml').run()
    opfile = open('router1.txt', 'r')#sets mode to read when the file opens
    response.markdown = (opfile.read())

    return(response)

#Restconf skill gets Used memory
def restconf_skill(incoming_msg):
    response = Response()
    rest = useful.restconf_project(url_base, headers, device_username, device_password)

    if rest == 0:
        response.markdown = "I have no information nerd."
    else:
        response.markdown = "Here's what I got \n\n"
        reststr= str(rest)
        response.markdown += reststr
    return(response)

def restconf_skill2(incoming_msg):
    #response = Response()
    rest= useful.get_cpu(url_base, headers, device_username, device_password)
    
    return(str(rest))
 
 #Check BGP status
def genierobot_skill(incoming_msg):
    response = Response()

    logFile = open('robotLog.txt', 'w')
    robot.run("robotskill.robot", stdout=logFile)
    opfile=open('robotLog.txt', 'r')
    response.markdown = (opfile.read())

    return(response)

# Set the bot greeting.
bot.set_greeting(greeting)

'''
# Add Bot's Commmands
bot.add_command(
    "arp list", "See what ARP entries I have in my table.", arp_list)
bot.add_command(
    "system info", "Checkout the device system info.", sys_info)
bot.add_command(
    "show interfaces", "List all interfaces and their IP addresses", get_int_ips)
bot.add_command("attachmentActions", "*", useless.handle_cards)
bot.add_command("showcard", "show an adaptive card", useless.show_card)
bot.add_command("dosomething", "help for do something", useless.do_something)
bot.add_command("time", "Look up the current time", useless.current_time)
bot.add_command("check bgp", "This job checks that all BGP neighbors are in Established state", check_bgp)
bot.add_command("check interface", "This job will look down interfaces", check_int)
'''

bot.add_command("stop monitoring", "This job will stop all monitor job", stop_monitor)


#Paramiko/netmiko skill
bot.add_command("show ip int brief", "This job performs the show ip int brief command", p.show_ip_int_brief)
#netconf/restconf skill
bot.add_command("get cpu", "This job gets the cpu status at 5 seconds", restconf_skill2)
#second restconf skill
bot.add_command("get used mem", "This job gets the used memory", restconf_skill)
#ansible skill
bot.add_command("show version", "This job performs the show version command", ansible_skill )
#genie robot skill
bot.add_command('bgp status', "This job checks the status of BGP configurations", genierobot_skill)
#genie monitor skill for disaster
bot.add_command("monitor CSR2", "This job will monitor interface status in back ground", monitor_int)

# Every bot includes a default "/echo" command.  You can remove it, or any
bot.remove_command("/echo")

if __name__ == "__main__":
    # Run Bot
    bot.run(host="0.0.0.0", port=5000)
