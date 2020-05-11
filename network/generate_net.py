import os 
import random
import string
import subprocess

import numpy as np 

random.seed(4)
np.random.seed(4)

# number of roads horizontally and vertically
num_roads = 3

# distance between roads/intersections
block_size = 500

one_way_probabilty = 0.2
valid_road_directions = False 
while not valid_road_directions:
    # Dimensions are road_orientation x num_roads x directions
    road_directions = np.random.rand(2, num_roads, 2) > one_way_probabilty
    if road_directions.any(axis=-1).all():
        valid_road_directions = True


xml_version = '<?xml version="1.0" encoding="UTF-8"?>\n'

node_header = '<nodes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\
     xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/nodes_file.xsd">\n'
node_template = string.Template('\t<node id="$id" x="$x" y="$y" type="$type"/>\n')

type_header = '<types>\n'
type_template = string.Template('\t<type id="$id" priority="$priority" numLanes="$numLanes" speed="$speed"/>\n')

edge_header = '<edges xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\
     xsi:noNamespaceSchemaLocation="http://sumo.sf.net/xsd/edges_file.xsd">\n'
edge_template = string.Template('\t<edge id="$id" from="$from_node" to="$to_node" type="$type"/>\n')


def create_nodes():
    ''' Creates node xml for network.

    Nodes take on a particular naming format.
    Node IDs for all internal grid intersections are of the form "(i_j)", following matrix row/column convention.
    Terminal nodes are of the form "{terminal}{direction}{road}", e.g. "startv0" or "endh1",
        terminal in {start, end}
        direction in {v, h} (vertical or horizontal)
        road in {0, ..., num_roads}

    The location of nodes is slightly counter intuitive, the origin is x=0, y=0 for node (0, 0).
    The subsequent nodes are laid out in matrix form, with greater i coord indicating a "lower" row.
    Therefore, greater i indicates a lower y coord, whereas greater j indicates a greater x coord.
    '''

    x_coords = np.arange(0, (num_roads)*block_size, block_size)
    y_coords = x_coords * -1
    xml_string = [xml_version, node_header]

    for i in range(num_roads):
        for j in range(num_roads):
            x = x_coords[j]
            y = y_coords[i] 
            node_id = '({}_{})'.format(i, j)
            xml_node = node_template.substitute(id=node_id, x=x, y=y, type='traffic_light')
            xml_string.append(xml_node)

    # Make start and end nodes for each horizontal road
    for i in range(num_roads):
         # Start Node
        x = x_coords[0] - block_size
        y = y_coords[i] 
        node_id = 'starth{}'.format(i)
        xml_node = node_template.substitute(id=node_id, x=x, y=y, type='priority')
        xml_string.append(xml_node)

        # End Node
        x = x_coords[-1] + block_size
        y = y_coords[i]
        node_id = 'endh{}'.format(i)
        xml_node = node_template.substitute(id=node_id, x=x, y=y, type='priority')
        xml_string.append(xml_node)

    # Make start and end nodes for each vertical road
    for j in range(num_roads):
        # Start Node
        x = x_coords[j]
        y = y_coords[0] + block_size
        node_id = 'startv{}'.format(j)
        xml_node = node_template.substitute(id=node_id, x=x, y=y, type='priority')
        xml_string.append(xml_node)

        # End Node
        x = x_coords[j]
        y = y_coords[-1] - block_size
        node_id = 'endv{}'.format(j)
        xml_node =  node_template.substitute(id=node_id, x=x, y=y, type='priority')
        xml_string.append(xml_node)
    
    xml_string.append('</nodes>')

    xml_string = ''.join(xml_string)

    with open('data/grid.nod.xml', 'w') as f:
        f.write(xml_string)


def create_link_xml():
    ''' Creates xml for 3 different road types (only 2 are used for now).
    '''
    priorities = [3, 2, 2]
    numLanes = [3, 3, 2]
    speeds = [16.667, 16.667, 13.889]
    
    xml_string = [xml_version, type_header]

    for i in range(3):
        priority = priorities[i]
        numLane = numLanes[i]
        speed = speeds[i]
        
        xml_type = type_template.substitute(
            id='type{}'.format(i),
            priority=priority, 
            numLanes=numLane,
            speed=speed
        )
        xml_string.append(xml_type)
    
    xml_string.append('</types>')
    xml_string = ''.join(xml_string)
    with open('data/grid.typ.xml', 'w') as f:
        f.write(xml_string)        


def create_road_edges(road_id, road_nodes, road_orientation, edge_type):
    ''' Creates road edges for a given road and its nodes.

    Accounts for one way roads by checking the value of road_directions for the road.
    '''
    xml_edges = []
    edges = []
    start_edges = []
    end_edges = []

    # Checks the forward direction of road (East to West, or North to South)
    if road_directions[road_orientation, road_id, 0]:
        for index in range(len(road_nodes)-1):
            from_node = road_nodes[index]
            to_node = road_nodes[index+1]
            edge_id = '{}-{}'.format(from_node, to_node)
            edges.append(edge_id)
            if index == 0:
                start_edges.append(edge_id)
            elif index == len(road_nodes) - 2:
                end_edges.append(edge_id)
            xml_edge = edge_template.substitute(id=edge_id, from_node=from_node, to_node=to_node, type=edge_type)
            xml_edges.append(xml_edge)

    # Checks the reverse direction of road (West to East, or South to North)
    if road_directions[road_orientation, road_id, 1]:
        for index in range(-1, -len(road_nodes), -1):
            from_node = road_nodes[index]
            to_node = road_nodes[index-1]
            edge_id = '{}-{}'.format(from_node, to_node)
            edges.append(edge_id)
            if index == -1:
                start_edges.append(edge_id)
            elif index == -len(road_nodes)+1:
                end_edges.append(edge_id)
            xml_edge = edge_template.substitute(id=edge_id, from_node=from_node, to_node=to_node, type=edge_type)
            xml_edges.append(xml_edge)   
                    
    return xml_edges, edges, start_edges, end_edges


def create_edges():
    ''' Creates edges xml for network.

    Edges follow a particular naming convention.
    Edge names are derived from their from_node and to_node:
        edge_id = "from_node-to_node"
        e.g. "starth0-(0_0)", "(1_1)-(1_2)"
    '''
    xml_string = [xml_version, edge_header]
    all_edges = []
    all_start_edges = []
    all_end_edges = []

    # Horizontal Roads
    road_orientation = 0
    edge_type = 'type0'
    for i in range(num_roads):
        road_nodes = ['starth{}'.format(i)]
        road_nodes += ['({}_{})'.format(i, j) for j in range(num_roads)]
        road_nodes += ['endh{}'.format(i)]
        xml_edges, edges, start_edges, end_edges = create_road_edges(i, road_nodes, road_orientation, edge_type)
        
        xml_string += xml_edges
        all_edges += edges
        all_start_edges += start_edges
        all_end_edges += end_edges

    # Vertical Roads
    edge_type = 'type1'
    road_orientation = 1
    for j in range(num_roads):
        road_nodes = ['startv{}'.format(j)]
        road_nodes += ['({}_{})'.format(i, j) for i in range(num_roads)]
        road_nodes += ['endv{}'.format(j)]
        xml_edges, edges, start_edges, end_edges = create_road_edges(j, road_nodes, road_orientation, edge_type)

        xml_string += xml_edges
        all_edges += edges
        all_start_edges += start_edges
        all_end_edges += end_edges

    xml_string.append('</edges>')

    xml_string = ''.join(xml_string)

    with open('data/grid.edg.xml', 'w') as f:
        f.write(xml_string)      

    return all_edges, all_start_edges, all_end_edges  


def create_net():
    ''' Runs the netconvert program to automatically generate a net.xml
    '''
    command = ['netconvert', '-c', 'grid.netcfg']
    # command = ["ls", "-l"]
    subprocess.call(command)

