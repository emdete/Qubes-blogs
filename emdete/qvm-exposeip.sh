#!/bin/bash
#change dev to your exposed device name
#./qvm-exposeip.sh personal 80
dev=wlp0s1
appvm=$1
port=$2
fw=$3
net=$4
if [ -z ${net} ]; then
    net=sys-net
fi
if [ -z ${fw} ]; then
    fw=sys-firewall
fi
externip=`qvm-run -p ${net} -u root "ifconfig ${dev}" | grep broadcast |col -x | awk '{print $2}'`

fwip=`qvm-ls -n | grep \{${fw}\} | col -x | awk '{print $14}'`
vmip=`qvm-ls -n | grep ${appvm} | col -x | awk '{print $13}'`

exenet="iptables -t nat -A PREROUTING -i ${dev} -p tcp --dport ${port} -d ${externip} -j DNAT --to-destination ${fwip} && iptables -I FORWARD 2 -i ${dev} -d ${fwip} -p tcp --dport ${port} -m conntrack --ctstate NEW -j ACCEPT"
qvm-run -p -u root ${net} "${exenet}"
exefw="iptables -t nat -A PREROUTING -i eth0 -p tcp --dport $port -d ${fwip} -j DNAT --to-destination ${vmip} && iptables -I FORWARD 2 -i eth0 -d ${vmip} -p tcp --dport ${port} -m conntrack --ctstate NEW -j ACCEPT"
qvm-run -p -u root ${fw} "${exefw}"
exevm="iptables -I INPUT 5 -p tcp --dport ${port} -m conntrack --ctstate NEW -j ACCEPT"
qvm-run -p -u root ${appvm} "${exevm}"
