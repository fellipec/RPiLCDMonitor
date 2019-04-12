#!/usr/bin/python3

import psutil, socket, datetime, time

# you can convert that object to a dictionary 
dvm = dict(psutil.virtual_memory()._asdict())

def ipaddrs():
    af_map = {
        socket.AF_INET: 'IPv4',
        socket.AF_INET6: 'IPv6',
        psutil.AF_LINK: 'MAC',
    }
    adapters = dict()
    for nic, addrs in psutil.net_if_addrs().items():
        addresses = list()       
        for addr in addrs:
            if addr.family == socket.AF_INET:
                addresses.append(addr.address)
        if nic != 'lo':
            adapters[nic] = addresses
    return adapters


def cputemp():
    temps = psutil.sensors_temperatures()
    if not temps:
        sys.exit("can't read any temperature")
    for name, entries in temps.items():
        if name == 'cpu-thermal':
            for entry in entries:
               return entry.current


ipsaddrs = ipaddrs()
uptime = datetime.timedelta(seconds=time.time() - psutil.boot_time())
cpu = psutil.cpu_percent(interval=1, percpu=True)
ram = dvm['percent'] 

print(ipsaddrs['eth0'][0])
print(uptime)
print(cpu[0])
print(cpu[1])
print(cpu[2])
print(cpu[3])
print(ram)
print(cputemp())


