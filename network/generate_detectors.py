import string 

num_lanes = 3

detector_head = '<additional>\n'
detector_template = string.Template('\t<laneAreaDetector id="$id" lane="$lane" \
    pos="$pos" endPos="$end_pos" file="cross.out" freq="30"/>\n')


def create_left_lane_detector(edge_id):
    ''' Creates lane detectors on left turn lane of every edge.
    '''
    detector_xml = []
    # for i in range(num_lanes):
    detector_id = 'detector-{}'.format(edge_id)
    lane = '{}_{}'.format(edge_id, num_lanes-1)
    pos = -150
    end_pos = -1

    detector_xml = detector_template.substitute(id=detector_id, lane=lane, pos=pos, end_pos=end_pos)

    return detector_xml


def create_detector_xml(edges):
    xml_string = [detector_head]
    for edge in edges:
        detector_xml = create_left_lane_detector(edge)
        xml_string.append(detector_xml)
    xml_string.append('</additional>')

    xml_string = ''.join(xml_string)

    with open('data/grid.det.xml', 'w') as f:
        f.write(xml_string)


