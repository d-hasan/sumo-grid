import os
import sys
import pdb


if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")


import sumolib
import traci 


net_path = 'data/grid.net.xml'
net = sumolib.net.readNet(net_path)


def get_edge_coords(edge):
    ''' Converts edge node IDs to grid coordinates

    The format for node ID is "(i_j)". Except for terminal nodes which have format:
         "start{direction}{road}", direction in {'h', 'v'}, road in {0, ..., roadnum}
         "end{direction}{road}"
    '''
    to_node = edge.getToNode().getID()
    coords = to_node.split('_')
    to_coord = [int(coords[0].replace('(', '')), int(coords[1].replace(')', ''))]

    from_node = edge.getFromNode().getID()
    if 'start' in from_node:
        if 'h' in from_node:
            from_coord = [to_coord[0], -1]
        elif 'v' in from_node:
            from_coord = [-1, to_coord[1]]
    elif 'end' in from_node:
        if 'h' in from_node:
            from_coord = [to_coord[0], -1]
        elif 'v' in from_node:
            from_coord = [-1, to_coord[1]]
    else:
        coords = from_node.split('_')
        from_coord = [int(coords[0].replace('(', '')), int(coords[1].replace(')', ''))]

    return from_coord, to_coord

def get_lane_detectors(traffic_lights):    
    ''' Returns a dictionary of lane detectors per road direction per traffic light.
    '''
    lane_detectors = {traffic_light.getID(): {'NS':[], 'EW':[]} for traffic_light in traffic_lights}

    for traffic_light in traffic_lights:
        edges = traffic_light.getEdges()
        for edge in edges:
            from_coord, to_coord = get_edge_coords(edge)
            if from_coord[0] == to_coord[0]:
                # i coordinate is consistent, meaning road is east-west
                direction = 'EW'
            elif from_coord[1] == to_coord[1]:
                # j coordinate is consistent, meaning road is north-south
                direction = 'NS'
            
            detector_id = 'detector-{}'.format(edge.getID())
            lane_detectors[traffic_light.getID()][direction].append(detector_id)

    return lane_detectors


def run():
    step = 0
    traffic_lights = net.getTrafficLights()
    lane_detectors = get_lane_detectors(traffic_lights)

    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()

        # Check all traffic lights for left turn delays
        for traffic_light in traffic_lights:
            current_phase = traci.trafficlight.getPhase(traffic_light.getID())
            current_ryg = traci.trafficlight.getRedYellowGreenState(traffic_light.getID())

            lane_detectors_ns = lane_detectors[traffic_light.getID()]['NS']
            lane_detectors_ew = lane_detectors[traffic_light.getID()]['EW']

            # Total number of cars waiting to turn left from north-south road
            total_vehicle_num_ns = 0
            for lane_detector in lane_detectors_ns:
                total_vehicle_num_ns += traci.lanearea.getLastStepVehicleNumber(lane_detector)

            # Total number of cars waiting to turn left from east-west road
            total_vehicle_num_ew = 0
            for lane_detector in lane_detectors_ew:
                total_vehicle_num_ew += traci.lanearea.getLastStepVehicleNumber(lane_detector)
            
            # Give priority to changing east-west roads when there are more than 10 cars waiting for a left
            if total_vehicle_num_ew > 10 and current_phase == 2:
                traci.trafficlight.setPhase(traffic_light.getID(), 3)
            elif total_vehicle_num_ns > 10 and current_phase == 0:
                traci.trafficlight.setPhase(traffic_light.getID(), 1)
        
        step += 1
    traci.close()
    sys.stdout.flush()

    


if __name__ == "__main__":
    sumoBinary = sumolib.checkBinary('sumo-gui')

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    traci.start([sumoBinary, "-c", "grid.sumocfg",
                             "--tripinfo-output", "tripinfo.xml"])
    run()