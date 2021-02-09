There are 3 files of concern.  
[mptcp_testing.py](mptcp_testing.py) is the main program that runs iperf and generates the JSON of iperf. This is run in mininet  
[graph_results.py](graph_results.py) ingests the json and spits out pretty graphs from the JSON. This is run in the directory containing the json test results.  
[CONSTANTS.py](CONSTANTS.py) contains the constants required for the test. Change values in the array to change the test parameters
