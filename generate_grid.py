from network.generate_net import create_nodes, create_link_xml, create_edges, create_net
from network.generate_routes import create_route_xml
from network.generate_detectors import create_detector_xml



if __name__ == '__main__':
    create_nodes()
    print('Created node xml')

    create_link_xml()
    print('Created link type xml')

    all_edges, start_edges, end_edges = create_edges()
    print('Created edges xml')

    create_net()
    print('Successfuly converted nodes and edges to network')

    create_route_xml(start_edges, end_edges)
    print('Created route xml')
    
    create_detector_xml(all_edges)
    print('Created lane area detector xml')