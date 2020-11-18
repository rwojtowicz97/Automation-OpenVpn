#!/usr/bin/python3
import os
import sys
import socket


hosts = []
ports = []
ip_tables = []
routes = []
one_port_entry = '$IPTABLES -A forward_vpn -s $VPNUSERNET -d ADRESIP -p tcp --dport PORTS -j ACCEPT ## HOSTNAME\n'
multi_port_entry = '$IPTABLES -A forward_vpn -s $VPNUSERNET -d ADRESIP -p tcp -m multiport --dports PORTS -j ACCEPT ## HOSTNAME\n'
route_entry = 'push "route ADRESIP 255.255.255.255" ## HOSTNAME\n'


argvInput = sys.argv[2:]
user = sys.argv[1]

if os.path.exists(f'/etc/openvpn/ccd/{user}') == False:
    sys.exit('ccd file doesn\'t exists')
    

firewall = open("/etc/rc.d/firewall", "r")
firewall_list = firewall.readlines()
firewall.close()


def split_hosts_and_ports(argvInput):
    for x in argvInput:
        data = x.split(':')
        hosts.append(data[0])
        ports.append(data[1])


def change_ip_to_hostname(hosts):
    for index, item in enumerate(hosts):
        if item[0].isdigit():
            hostname = socket.gethostbyaddr(item)
            hosts[index] = hostname[0]


def make_one_port_entry(ipv4, hostname, port):
    ip_table = one_port_entry.replace('ADRESIP', ipv4)
    ip_table = ip_table.replace('PORTS', port)
    ip_table = ip_table.replace('HOSTNAME', hostname)
    ip_tables.append(ip_table)
    route = route_entry.replace('ADRESIP', ipv4)
    route = route.replace('HOSTNAME', hostname)
    routes.append(route)


def make_multi_port_entry(ipv4, hostname, ports):
    ip_table = multi_port_entry.replace('ADRESIP', ipv4)
    ip_table = ip_table.replace('PORTS', ports)
    ip_table = ip_table.replace('HOSTNAME', hostname)
    ip_tables.append(ip_table)
    route = route_entry.replace('ADRESIP', ipv4)
    route = route.replace('HOSTNAME', hostname)
    routes.append(route)


def find_user_in_firewall():
    for i, v in enumerate(firewall_list):
        if v.find(user) != -1:
            for ip_table in ip_tables:
                firewall_list.insert(i+2, ip_table)
            break


def save_changes_in_firewall():
    firewall = open("/etc/rc.d/firewall", "w")
    new_file_contents = "".join(firewall_list)

    firewall.write(new_file_contents)
    firewall.close()


split_hosts_and_ports(argvInput)
change_ip_to_hostname(hosts)


for index in range((len(hosts))):
    ip_address = socket.gethostbyname(hosts[index])
    if ',' in ports[index]:
        make_multi_port_entry(ip_address, hosts[index], ports[index])
    else:
        make_one_port_entry(ip_address, hosts[index], ports[index]) 


find_user_in_firewall()
save_changes_in_firewall()


ccd = open(user,"a+")
for route in routes:
    ccd.write(route)
ccd.close()
