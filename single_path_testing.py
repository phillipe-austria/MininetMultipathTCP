#!/bin/python3

from mininet.topo import Topo
from mininet.link import TCLink
from mininet.net import Mininet
from statistics import mean, median
from mininet.log import lg, info
from math import ceil
from time import sleep


def min_seconds_to_transmit(bandwidth, tcp_mss=1480, packet_count=100000):
    return ceil(packet_count * tcp_mss / bandwidth)


class TwoHostTopo(Topo):
    def build(self, bandwidth, latency, error_rate=0):
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        self.addLink(h1, h2, cls=TCLink, delay=latency, bw=bandwidth, loss=error_rate)


    def test(self):
        self.pingAll()


if __name__ == '__main__':
    bandwidth_list = [10]  # bandwidth in Mbps, count 2
    latency_list = [1000, 1500, 2000, 2500]  # latency in ms. count 6
    error_rate_list = [0.1, 0.01, 0.001, 0.0001, 0.00001]  # error_rate in %, count 5
    lg.setLogLevel('debug')

    for bandwidth in bandwidth_list:
        for latency in latency_list:
            for error_rate in error_rate_list:
                net = Mininet(controller=None, topo=TwoHostTopo(bandwidth, str(latency) + "ms", error_rate))
                net.start()
                client, server = net.get("h1", "h2")
                info(f"*** Iperf with {bandwidth}Mbps, {latency}ms and {error_rate}%\n")
                server.cmd('killall -9 iperf3')
                server.sendCmd("iperf3 -s -P 1")
                sleep(5)
                print(f"Server IP is {server.IP()}")
                h1_cmd = f"iperf3 --json -i -t 100 1 -c {server.IP()} --logfile test_{str(bandwidth)}_{str(latency)}_{str(error_rate)}.json"
                client.cmdPrint(h1_cmd)
                sleep(5)
                net.stop()
