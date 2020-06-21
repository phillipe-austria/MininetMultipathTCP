#!/bin/python3

from mininet.topo import Topo
from mininet.link import TCLink
from mininet.net import Mininet
from statistics import mean, median
from mininet.log import lg, info
from math import ceil


def min_seconds_to_transmit(bandwidth, tcp_mss=1480, packet_count=100000):
    return ceil(packet_count * tcp_mss / bandwidth)


class TwoHostTopo(Topo):
    def build(self, bandwidth, latency, error_rate=0):
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        self.addLink(h1, h2, cls=TCLink, delay=latency, bw=bandwidth, loss=error_rate)


if __name__ == '__main__':
    bandwidth_list = [1, 10]  # bandwidth in Mbps, count 2
    latency_list = [10, 100]  # latency in ms. count 6
    error_rate_list = [0.1, 0.01, 0.001, 0.0001, 0.00001]  # error_rate in %, count 5
    lg.setLogLevel('info')
    with open("results.csv", 'w') as result_file:
        for bandwidth in bandwidth_list:
            for latency in latency_list:
                for error_rate in error_rate_list:
                    net = Mininet(controller=None, topo=TwoHostTopo(bandwidth, str(latency) + "ms", error_rate))
                    net.start()
                    info(f"*** Iperf with {bandwidth}Mbps, {latency}ms and {error_rate}%\n")
                    server_bw_with_unit, _ = net.iperf(fmt='m', seconds=100)  # get the iperf server bandwidth results in Mbps. Ignore the client reported bandwidth since its inaccurate.
                    # server_bw_with_unit   is a string in the format of 'X Mbps'. We split the string just to get the X alone and convert the string to a float
                    server_bw = float(server_bw_with_unit.split(' ')[0])
                    result_file.write(f"{bandwidth},{latency},{error_rate},{server_bw}\n")
                    net.stop()