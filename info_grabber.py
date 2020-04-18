#!/usr/local/bin/python3

'''
This script uses the Nornir framework to collect discovery information from 
Cisco network devices and save the output to file. Devices and parameters are 
provided by the SimpleInventory plugin for Nornir using YAML files. 
'''

import sys
from getpass import getpass
from datetime import datetime
from nornir import InitNornir
from nornir.core.filter import F
from nornir.plugins.tasks import text, files
from nornir.plugins.functions.text import print_result
from nornir.plugins.tasks.networking import netmiko_send_command


# print formatting function
def c_print(printme):
    # Print centered text with newline before and after
    print(f"\n" + printme.center(80, ' ') + "\n")


# Nornir kickoff
def kickoff():
    # print banner
    print()
    print('~'*80)
    c_print('This script will gather discovery information from Cisco devices')

    if len(sys.argv) < 2:
        site = ""

    else:
        site = sys.argv[1] + "_"

    # initialize The Norn
    nr = InitNornir(
        inventory={
            "plugin": "nornir.plugins.inventory.simple.SimpleInventory",
            "options": {
                "host_file": f"inventory/{site}hosts.yaml",
                "group_file": f"inventory/{site}groups.yaml",
                "defaults_file": "inventory/defaults.yaml"
            }
        }
    )
    
    # filter The Norn
    nr = nr.filter(platform="ios")

    c_print('Checking inventory for credentials')
    # check for existing credentials in inventory

    if nr.inventory.defaults.username == None or nr.inventory.defaults.password == None:
        c_print('Please enter device credentials:')

    if nr.inventory.defaults.username == None:
        nr.inventory.defaults.username = input("Username: ")
    
    if nr.inventory.defaults.password == None:
        nr.inventory.defaults.password = getpass()
        print()
    print('~'*80)
    return nr


def grab_info(task):
    # show commands to be run
    commands = [
        "show version",
        "show inventory",
        "show module",
        "show run",
        "show vlan brief",
        "show vlan",
        "show interface status",
        "show interface trunk",
        "show power inline",
        "show ip interface brief",
        "show ip route",
        "show ip arp",
        "show mac address-table",
        "show cdp neighbors",
        "show cdp neighbors detail",
        ]

    c_print(f"*** Collecting data from {task.host} ***")

    # loop over commands
    for cmd in commands:
        # send command to device
        output = task.run(task=netmiko_send_command, command_string=cmd)
        # save results with timestamp to aggregate result
        time_stamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        task.host["info"]="\n"*2+"#"*40+"\n"+cmd+" : "+time_stamp+"\n"+"#"*40+"\n"*2+output.result
        # write output files
        task.run(
            task=files.write_file,
            filename=f"output/{task.host}_info.txt",
            content=task.host["info"],
            append=True
        )


def main():
    # kickoff The Norn 
    nr = kickoff()
    # run The Norn
    nr.run(task=grab_info)

if __name__ == "__main__":
    main()