import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.validators.scatter.marker import SymbolValidator
import json
from os import listdir
import pandas as pd
import json
from CONSTANTS import *

from typing import TypedDict


class TestParameters(TypedDict):
    test_length: int
    error_rate: float


def plot_graph(directory):
    bandwidth_dict = {
        "tcp_algorithm": [],
        "link": [],
        "bandwidth": [],
        "link_2_latency": []
    }
    config: TestParameters = {}
    bandwidth_df = None

    with open(directory + '/config.json') as json_file:
        config: TestParameters = json.load(json_file)
    link_1_bandwidth = 0.0  # Link 1 bandwith at 100ms latency
    for tcp_scheduler in tcp_scheduling_algorithms:
        for link_2_latency in link_2_latency_list:
            for tcp_type in tcp_type_list:
                with open(f"{directory}/{tcp_scheduler}_{tcp_type}_{link_2_latency}_{config['error_rate']}.json") as iperf_json_file:
                    try:
                        iperf_result = json.load(iperf_json_file)
                        if tcp_type == "single_path":
                            link_2_bandwidth = iperf_result['end']['sum_sent']['bits_per_second']
                            bandwidth_dict["tcp_algorithm"].append(tcp_scheduler)
                            bandwidth_dict['bandwidth'].append(link_2_bandwidth)
                            bandwidth_dict["link"].append("link_2")
                            bandwidth_dict["link_2_latency"].append(link_2_latency)
                            if link_2_latency == link_1_latency:  # since they have same parameters, they're going to have the same bandwidth
                                link_1_bandwidth = iperf_result['end']['sum_sent']['bits_per_second']

                            #  append combined bandwidth for each result
                            bandwidth_dict["tcp_algorithm"].append(tcp_scheduler)
                            bandwidth_dict['bandwidth'].append(link_1_bandwidth + link_2_bandwidth)
                            bandwidth_dict["link"].append("combined")
                            bandwidth_dict["link_2_latency"].append(link_2_latency)

                            # append link 1 bandwdith for each result
                            bandwidth_dict["tcp_algorithm"].append(tcp_scheduler)
                            bandwidth_dict['bandwidth'].append(link_1_bandwidth)
                            bandwidth_dict["link"].append("link_1")
                            bandwidth_dict["link_2_latency"].append(link_2_latency)
                        else:
                            mptcp_bandwidth = iperf_result['end']['sum_sent']['bits_per_second']
                            bandwidth_dict["tcp_algorithm"].append(tcp_scheduler)
                            bandwidth_dict['bandwidth'].append(mptcp_bandwidth)
                            bandwidth_dict["link"].append("mptcp")
                            bandwidth_dict["link_2_latency"].append(link_2_latency)
                    except json.decoder.JSONDecodeError:
                        print(f"error with file {iperf_json_file.name}")
    bandwidth_df = pd.DataFrame.from_dict(bandwidth_dict)

    # each bar chart displays a single protocol compared with varying latencies
    fig = make_subplots(rows=1,
                        cols=len(tcp_scheduling_algorithms),
                        subplot_titles=tcp_scheduling_algorithms,
                        shared_yaxes=True)
    for i in range(len(tcp_scheduling_algorithms)):
        algorithm: str = tcp_scheduling_algorithms[i]
        single_protocol_df = bandwidth_df.query("tcp_algorithm == @algorithm")
        fig.add_trace(
            go.Bar(name='Link 1 throughput',
                   x=link_2_latency_list,
                   y=single_protocol_df.query("link =='link_1'")["bandwidth"].to_list()),
            col=i + 1,
            row=1
        )
        fig.add_trace(
            go.Bar(name='Link 2 throughput',
                   x=link_2_latency_list,
                   y=single_protocol_df.query("link =='link_2'")["bandwidth"].to_list()),
            col=i + 1,
            row=1
        )
        fig.add_trace(
            go.Bar(name='Total throughput', x=link_2_latency_list,
                   y=single_protocol_df.query("link =='combined'")["bandwidth"].to_list()),
            col=i + 1,
            row=1
        )
        fig.add_trace(
            go.Bar(name='Multipath TCP throughput',
                   x=link_2_latency_list,
                   y=single_protocol_df.query("link =='mptcp'")["bandwidth"].to_list()),
            col=i + 1,
            row=1
        )

        # Change the bar mode
    fig.update_layout(barmode='group',
                      title=f"Error rate: {config['error_rate']}%",
                      xaxis_title="Link 2 Latency",
                      yaxis_title="bandwidth",
                      legend_title="Links"
                      )
    fig.show()

    # each bar chart displays a single latency compared with varying protocols

    fig_2 = make_subplots(rows=1,
                          cols=len(link_2_latency_list),
                          subplot_titles=link_2_latency_list,
                          shared_yaxes=True)
    for i in range(len(link_2_latency_list)):
        latency: int = link_2_latency_list[i]
        single_protocol_df = bandwidth_df.query("link_2_latency == @latency")
        fig_2.add_trace(
            go.Bar(name='Link 1 throughput',
                   x=tcp_scheduling_algorithms,
                   y=single_protocol_df.query("link =='link_1'")["bandwidth"].to_list()),
            col=i + 1,
            row=1
        )
        fig_2.add_trace(
            go.Bar(name='Link 2 throughput',
                   x=tcp_scheduling_algorithms,
                   y=single_protocol_df.query("link =='link_2'")["bandwidth"].to_list()),
            col=i + 1,
            row=1
        )
        fig_2.add_trace(
            go.Bar(name='Total throughput', x=tcp_scheduling_algorithms,
                   y=single_protocol_df.query("link =='combined'")["bandwidth"].to_list()),
            col=i + 1,
            row=1
        )
        fig_2.add_trace(
            go.Bar(name='Multipath TCP throughput',
                   x=tcp_scheduling_algorithms,
                   y=single_protocol_df.query("link =='mptcp'")["bandwidth"].to_list()),
            col=i + 1,
            row=1
        )

        # Change the bar mode
    fig_2.update_layout(barmode='group',
                        title=f"Error rate: {config['error_rate']}%",
                        xaxis_title="Protocol",
                        yaxis_title="Bandwidth",
                        legend_title="Links")
    fig_2.show()

    # line graph comparing bandwidths and latencies
    multipath_bandwidth = bandwidth_df.query("link == 'mptcp'")
    fig_3 = px.line(multipath_bandwidth, x="link_2_latency", y="bandwidth", color="tcp_algorithm")
    fig_3.update_layout(
                        title=f"Error rate: {config['error_rate']}%",
                        xaxis_title="Latency",
                        yaxis_title="Bandwidth",
                        legend_title="Links")

    fig_3.show()


if __name__ == '__main__':


    test_directories = listdir('results/multi_protocol_multi_latency_single_speed/')
    for directory in test_directories:
        plot_graph('results/multi_protocol_multi_latency_single_speed/' + directory)
