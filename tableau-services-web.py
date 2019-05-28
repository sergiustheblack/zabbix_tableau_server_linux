#!/usr/bin/env python
'''
    tableau-services-web.py "$1" "$2" "$3" "$4"
    $1 = hostname (no proto, port if needed, ex: tableau.example.com)
    $2 = machine name from discovery (ex: tableau.example.com)
    $3 = service (ex: backgrounder)
    $4 = worker (ex: tableau.example.com:8250)
'''
import requests
import sys
import json
from xml.etree import ElementTree

args = len(sys.argv) - 1
try:
    url = 'http://'+sys.argv[1]+'/admin/systeminfo.xml'
    verify = True
except IndexError:
    print("200")
    exit(1)
try:
    targethost = sys.argv[2]
    targetservice = sys.argv[3]
    targetworker = sys.argv[4]
except IndexError:
    pass

try:
    r = requests.get(url, verify =verify, timeout=20)
    # special case if server is unresponsive
    if r.status_code != 200:
        print("100")
        exit(1)
    systeminfo = ElementTree.fromstring(r.content)
except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
    # special case if server is unresponsive
    print("100")
    exit(1)



statusmap = {"Active": 0,
            "Down": 1,  # Fuck
            "StatusNotAvailable": 2,  # let's treat 2-4 as not available
            "StatusNotAvailableSyncing": 3,
            "NotAvailable": 4,
            "Passive": 5,  # >= 5 is WTF
            "Unlicensed": 6,
            "Busy": 7,
            "ReadOnly": 8,
            "ActiveSyncing": 9,
            "DecommisionedReadOnly": 10,
            "DecomisioningReadOnly": 11,
            "DecommissionFailedReadOnly": 12}


if args == 1:
    json2send = {}
    json2send['data'] = []

    for machine in systeminfo.iter('machine'): #.findall('machines'):
        servername = machine.get('name')
        for service in machine:
            jjj = {}
            jjj["{#SERVERNAME}"] = servername
            jjj["{#SERVICE}"] = service.tag
            jjj["{#WORKER}"] = service.attrib['worker']

            json2send['data'].append(jjj)

    print(json.dumps(json2send))
    # Special case for status of server
elif targetservice == 'service':
    print(statusmap[systeminfo[1].attrib['status']])

elif args == 4:
    for machine in systeminfo.iter('machine'):
        for service in machine:
            if machine.get('name') == targethost and service.tag == targetservice and service.attrib['worker'] == targetworker:
                print(statusmap[service.attrib['status']])

else:
    print("200")  # Arguments count wrong
