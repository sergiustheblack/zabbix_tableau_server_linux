# zabbix_tableau_server_linux
Zabbix template for Tableau Server on Linux


## Requirements:
Python (tested on Centos 7 with Python 2.7 and 3.7) and Python modules:
- PyYAML
- requests

## Usage
[Enable remote access to your sever](https://onlinehelp.tableau.com/current/server-linux/en-us/service_remote.htm) and make sure it is accessible from localhost. `curl -L http://your.server.com:port/admin/systeminfo.xml`
Put script onto server, for example
```
cp ./tableau-services-web.py /etc/zabbix/zabbix_agentd.scripts/ ; chmod +x /etc/zabbix/zabbix_agentd.scripts/tableau-services-web.py
```
Add the following to your zabbix_agentd.conf
```
UserParameter=tableau.services.web[*], /etc/zabbix/zabbix_agentd.scripts/tableau-services-web.py "$1"
UserParameter=tableau.service.web[*], /etc/zabbix/zabbix_agentd.scripts/tableau-services-web.py "$1" "$2" "$3" "$4"
```
Import template to your zabbix server

## Adjust Template to your needs
- Set custom port in item template or replace {HOST.HOST} to something that suite yout needs. 
- Tune trigger prototypes.
- Look up under Items and enable/disable those you need.

## How it works 
Script invokes get request to http://{HOST.HOST}/admin/systeminfo.xml

If called with one argument, it produces JSON for LLD.

If called with 4 arguments, tries to look up for requested service status and maps text status to integer value sent to Zabbix.
If called with 3rd argument 'Status', returns server status (integer).

If web status is unavailable, it returns 100.

### .sh script
I have uploaded first .sh script that uses tsm utility directly. It is *possible* to use only after Tableau Server 2019.2 release, since it doesn't ask for password under root and members of tsmadmin user.

But I strongly advise you to NOT to use it since calling tsm every minute (multiple times per minute) produces high CPU load. Probably you'll need to tune it first. 
