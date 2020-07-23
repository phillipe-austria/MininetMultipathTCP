#!/bin/python3

from mininet.topo import Topo
from mininet.link import TCLink
from mininet.net import Mininet
from statistics import mean, median
from mininet.log import lg, info, debug
from math import ceil
from time import sleep
import mininet.util as util

if __name__ == '__main__':
    bandwidth_list = [10]  # bandwidth in Mbps, count 2
    latency_list = [550] #[1000, 1500, 2000, 2500]  # https://en.wikipedia.org/wiki/Satellite_Internet_access#Geostationary_orbits:~:text=Geostationary%20orbits,-%5B
    error_rate_list = [0.1] #[0.1, 0.01, 0.001, 0.0001, 0.00001]  # error_rate in %, count 5
    tcp_scheduling_algorithms = ['reno', 'cubic', 'vegas', 'hybla']
    net = Mininet()
    lg.setLogLevel('debug')
    net.addHost('h1')
    net.addHost('h2')
    h1 = net.get("h1")
    h2 = net.get("h2")
    link = net.addLink(h1, h2, cls=TCLink, params1={'ip': '10.0.0.1/24'}, params2={'ip': '10.0.0.2/24'})
    net.start()
    h2.cmd("killall iperf3")
    h2.cmd("iperf3 -s -D")
    sleep(5)  # Wait for the server to start up.
    for latency in latency_list:
        for error_rate in error_rate_list:
            for tcp_algorithm in tcp_scheduling_algorithms:
                link.intf1.config(bw=10, loss=error_rate, delay=str(latency) + "ms", use_tbf=True, peakrate="10mbps")
                link.intf2.config(bw=10, loss=error_rate, delay=str(latency) + "ms", use_tbf=True, peakrate="10mbps")
                info(f"*** Iperf with 10 Mbps, {latency}ms and {error_rate}%\n")
                h1.cmdPrint(f"iperf3 --json -t 1800 -c {h2.IP()} -C {tcp_algorithm} --logfile results_multiple_tcp/{tcp_algorithm}.json")
                sleep(5)  # Wait for the client to finish the test.
    net.stop()
