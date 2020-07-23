#!/bin/python3

from mininet.link import TCLink,TCIntf
from mininet.net import Mininet
from mininet.log import lg, info
from time import sleep
import json

from CONSTANTS import *


if __name__ == '__main__':

    iperf_test_time = 900
    net = Mininet()
    lg.setLogLevel('debug')
    net.addHost('h1')
    net.addHost('h2')
    h1 = net.get("h1")
    h2 = net.get("h2")
    link_2 = net.addLink(h1, h2, cls=TCLink, params1={'ip': '10.1.0.1/24'}, params2={'ip': '10.1.0.2/24'})
    net.start()
    h2.cmd("killall iperf3")
    h2.cmd("iperf3 -s -D")
    sleep(5)  # Wait for the server to start up.

    # write the test parameters to config.json
    config = {
        "test_length": iperf_test_time,
        "error_rate": error_rate
    }
    with open('results/multi_protocol_multi_latency_single_speed/config.json', 'w') as fp:
        json.dump(config, fp)


    #  single path testing
    print("Single path testing")
    for algorithm in tcp_scheduling_algorithms:
        for link_2_latency in link_2_latency_list:
            link_2.intf1.config(delay=str(link_2_latency) + "ms", loss=error_rate, bw=10, enable_red=True)
            link_2.intf2.config(delay=str(link_2_latency) + "ms", loss=error_rate, bw=10, enable_red=True)
            h1.cmdPrint(f"iperf3 --json -t {iperf_test_time} -c {h2.IP()} ",
                        f"-C {algorithm}",
                        "-i 0"
                        f" --logfile results/multi_protocol_multi_latency_single_speed/{algorithm}_single_path_{link_2_latency}_{error_rate}.json")
            sleep(5)  # Wait for the client to finish the test.

    #  multi path testing
    #  add another link
    link_1 = net.addLink(h1, h2, cls=TCLink, params1={'ip': '10.0.0.1/24'}, params2={'ip': '10.0.0.2/24'},
                         loss=error_rate, delay=str(link_1_latency) + "ms", bw=10, enable_red=True)

    print("Multipath testing")
    for algorithm in tcp_scheduling_algorithms:
        for link_2_latency in link_2_latency_list:
            link_2.intf1.config(delay=str(link_2_latency) + "ms", loss=error_rate, bw=10, enable_red=True)
            link_2.intf2.config(delay=str(link_2_latency) + "ms", loss=error_rate, bw=10, enable_red=True)
            h1.cmdPrint(f"iperf3 --json",
                        f"-t {iperf_test_time}",
                        f" -c {h2.IP()} -C {algorithm} ",
                        "-i 0",
                        f" --logfile results/multi_protocol_multi_latency_single_speed/{algorithm}_multi_path_{link_2_latency}_{error_rate}.json")
            sleep(5)  # Wait for the client to finish the test.
    net.stop()
