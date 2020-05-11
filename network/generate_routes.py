import os 
import random
from string import Template

import numpy as np 

random.seed(4)
np.random.seed(4)

# number of roads horizontally and vertically
num_roads = 3

xml_version = '<?xml version="1.0" encoding="UTF-8"?>\n'

route_header = '<routes>\n'
vehicle_template = Template('\t<vType id="$id" vClass="$vClass" maxSpeed="$maxSpeed" \
speedFactor="$speedFactor" speedDev="$speedDev" sigma="$sigma"/>\n')
flow_template = Template('\t<flow id="$id" type="$type" beg="0" end="5000" number="$number" \
from="$from_edge" to="$to_edge"/>\n')


def get_terminal_edges():
    start_edges = []
    end_edges = []
    for i in range(num_roads):
        start_1 = 'starth{}-{}_{}'.format(i, i, 0)
        end_1 = '{}_{}-starth{}'.format(i, num_roads-1, i)
        start_2 = 'endh{}-{}_{}'.format(i, i, num_roads-1)
        end_2 = '{}_{}-endh{}'.format(i, num_roads-1, i)
        start_edges += [start_1, start_2]
        end_edges += [end_1, end_2]

    for j in range(num_roads):
        start_1 = 'startv{}-{}_{}'.format(j, 0, j)
        end_1 = '{}_{}-startv{}'.format(0, j, j)
        start_2 = 'endv{}-{}_{}'.format(j, num_roads-1, j)
        end_2 = '{}_{}-endv{}'.format(num_roads-1, j, j)
        start_edges += [start_1, start_2]
        end_edges += [end_1, end_2]

    return start_edges, end_edges
            

def create_flow(xml_string, edge_1, edge_2, vehicles, vehicle_nums):
    for vehicle, number in zip(vehicles, vehicle_nums):
        flow_id = '{}-({})-({})'.format(vehicle, edge_1, edge_2)
        xml_string += flow_template.substitute(
            id=flow_id,
            type=vehicle,
            number=number,
            from_edge=edge_1,
            to_edge=edge_2
        )
    return xml_string


def create_route_xml(start_edges, end_edges):
    xml_string = ''
    xml_string += xml_version
    xml_string += route_header

    vehicles = ["normal", "sporty", "trailer", "coach"]
    v_classes = ["passenger", "passenger", "trailer", "coach"]
    max_speeds = [40, 60, 30, 30]
    speed_factors = [0.9, 1.3, 1.1, 1.]
    speed_devs = [0.2, 0.1, 0.1, 0.1]
    sigmas = [0.5, 0.1, 0.5, 0.5]
    vehicle_nums = [50, 3, 3, 7]

    car_attributes = zip(vehicles, v_classes, max_speeds, speed_factors, speed_devs, sigmas)

    for vehicle, v_class, max_s, speed_f, speed_d, sigma in car_attributes:
        xml_string += vehicle_template.substitute(
            id=vehicle,
            vClass=v_class,
            maxSpeed=max_s,
            speedFactor=speed_f,
            speedDev=speed_d,
            sigma=sigma
        )

    # start_edges, end_edges = get_terminal_edges()
    # import pdb;  pdb.set_trace()
    for edge_1 in start_edges:
        for edge_2 in end_edges:
            if edge_1 == edge_2:
                continue
            xml_string = create_flow(xml_string, edge_1, edge_2, vehicles, vehicle_nums)

    xml_string += '</routes>'

    with open('data/grid.rou.xml', 'w') as f:
        f.write(xml_string)
