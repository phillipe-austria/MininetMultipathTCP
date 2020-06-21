#!/bin/python3

from mininet.topo import Topo
from mininet.link import TCLink,TCIntf
from mininet.net import Mininet
from mininet.log import setLogLevel
from mininet.log import lg, info


class TwoHostTwoLinkTopo(Topo):
    def build(self, latency_1, latency_2, error_rate=0):
        client = self.addHost("client")
        server = self.addHost("server")
        self.addLink(client, server, delay=latency_1, bw=10, loss=error_rate, params1={ 'ip' : '10.0.0.1/24' }, params2={ 'ip' : '10.0.0.2/24' })
        self.addLink(client, server, delay=latency_2, bw=10, loss=error_rate, params1={ 'ip' : '10.0.1.1/24' }, params2={ 'ip' : '10.0.1.2/24' })

if __name__ == '__main__':
    latency_list = [10, 100]  # latency in ms. count 6
    error_rate_list = [0.1, 0.01, 0.001, 0.0001, 0.00001]  # error_rate in %, count 5
    setLogLevel(levelname='info')
    with open("results_multipath.csv", 'w') as result_file:
        result_file.write("latency,error_rate,bandwidth\n")
        for latency_1 in latency_list:
            for latency_2 in latency_list:
                for error_rate in error_rate_list:
                    net = Mininet(link=TCLink, topo=TwoHostTwoLinkTopo(str(latency_1) + "ms", str(latency_2) + "ms", error_rate))
                    net.start()
                    info(f"*** Iperf with {latency}ms and {error_rate}%\n")
                    server_bw_with_unit, _ = net.iperf(fmt='m', seconds=100)  # get the iperf server bandwidth results in Mbps. Ignore the client reported bandwidth since its inaccurate.
                    # server_bw_with_unit   is a string in the format of 'X Mbps'. We split the string just to get the X alone and convert the string to a float
                    server_bw = float(server_bw_with_unit.split(' ')[0])
                    result_file.write(f"{latency},{error_rate},{server_bw}\n")
                    net.stop()
