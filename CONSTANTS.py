link_1_latency = 100  # [1000, 1500, 2000, 2500]  # https://en.wikipedia.org/wiki/Satellite_Internet_access#Geostationary_orbits:~:text=Geostationary%20orbits,-%5B
link_2_latency_list = [100, 200, 500, 750, 1000]
error_rate = 0.0001  # [0.1, 0.01, 0.001, 0.0001, 0.00001]  # error_rate in %, count 5
#tcp_scheduling_algorithms = ['wvegas', 'olia', 'balia', 'bbr']
tcp_scheduling_algorithms = ['hybla', 'cubic', 'reno', 'bbr', 'wvegas', 'olia', 'balia']
tcp_type_list = ["single_path", "multi_path"]
