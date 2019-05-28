#!/bin/bash
# $1 - nodename
# $2 - service name
#

###############
# Item Sender #
###############
if [ $# -eq 2 ] ; then
OIFS=$IFS
IFS=$'\n'
	look=1
	for line in $(timeout 30 tsm status -v || echo $?) ; do 
		# if timeout, send error
		if [ $line -eq '124' ] ; then printf '124' ; exit 1 ; fi
		if echo $line | grep -q "$1" ; then
			look=1
			continue
		elif echo $line | grep -q node ; then
			look=0
			continue
		fi
		if echo $line | grep -q "$2" && [ $look -eq 1 ] ; then 
			if echo $line | grep -q "Status" ; then
				 echo $line | awk -F ': ' '/Status/{gsub("RUNNING",0,$2); gsub("STOPPED",1,$2); gsub("DEGRADED",3,$2); printf $2}' 
			else
				echo $line | awk -v srv="\047$2" -F ' is ' '$0~srv{gsub("^\\s+","") ; gsub("running.*",0,$2); gsub("(stopped).*",1,$2); gsub("(unavailable).*",2,$2);gsub("(in an error state).*",3,$2);printf $2}'
			fi
		fi
	done
exit 0
fi	

######################
# discovery of hosts #
######################

json='{"data":['

OIFS=$IFS
IFS=$'\n'

for line in $(timeout 30 tsm status -v) ; do 
	if echo $line | grep -q node ; then 
		nodepart=$(echo $line | grep node | awk -F ': ' '{ printf "{\"{#NODE}\":\""$2"\"" }') # | sed 's/,$//'
	elif echo $line | grep -qEv "(Backup|Maintenance|Import|Status)" ; then
		json+="$nodepart"
		json+="$(echo $line | awk -F ' is ' '{gsub("^\\s+","") ; gsub("\047","\042",$1); printf ",\"{#SERVICE}\":"$1"}," }')"
	fi 
done
IFS=$OIFS
json=$(echo $json | sed 's/,$//')
json+=']}' #data closure
printf "$json"
