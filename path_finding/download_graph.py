import osmnx
import networkx
import igraph
import os
import json

this_files_dir = os.path.dirname(os.path.realpath(__file__))

def download_graph(latitude: float, longitude: float, radius: float) -> igraph.Graph:
    print("we got called")
    '''Constructs a graph from street networks within a specified location.
    
    Args:
        latitude (float): the latitude of the center of the location
        longitude (float): the longitude of the center of the location
        radius (float): half the sidelength of the location covered
    Returns:
        An igraph containing the street network within the specified location.
        Nodes have 'x' (latitude), 'y' (longitude), and 'osmid' (id) attributes.
        Edges have 'length' (distance), 'grade' (change in elevation), and 'streetname' attributes.
    '''
    latitude, longitude, radius = [float(x) for x in (latitude, longitude, radius)]
    filename = json.dumps([latitude, longitude, radius]) + '.zip'
    filename = os.path.join(this_files_dir, 'saved_graphs', filename)

    res = os.listdir(os.path.join(this_files_dir, 'saved_graphs/'))
    for file in res:
        params = file[1:-5]
        variables = params.split(', ')
        if float(variables[0].strip()) == latitude and float(variables[1].strip()) == latitude and float(variables[2]) >= radius: #check if previously computed graph centered on same lat/long of equal or smaller radius was cached
            filename = os.path.join(this_files_dir, 'saved_graphs', file)
            break

    if os.path.exists(filename):
        graph = igraph.Graph.Read_GraphML(filename)
    else:
        should_download = input('Are you sure you want to download data? (y/n): ')
        assert should_download.lower() == 'y'
        with open(os.path.join(this_files_dir, 'google_maps_api_key.txt'), 'r') as f:
            google_maps_api_key = f.readline()
        graph = _get_graph_not_memoized(latitude, longitude, radius, google_maps_api_key)
        # convert streetname to an integer (for serialization)
        #for e in graph.es:  e['streetname'] = int(''.join(format(ord(i), 'b') for i in e['streetname']), 2)
        graph.write_graphml(filename)
    return graph
    


def _get_graph_not_memoized(latitude: float, longitude: float, radius: float,
    google_maps_api_key: str) -> igraph.Graph:
    # calculate extent of the graph
    radius_latlong = radius / 60
    north_lat = latitude + radius_latlong
    south_lat = latitude - radius_latlong
    east_long = longitude + radius_latlong
    west_long = longitude - radius_latlong
    # download graph
    graph = osmnx.graph_from_bbox(37.79, 37.78, -122.41, -122.43, network_type='walk')
    graph = osmnx.add_node_elevations(graph, api_key=google_maps_api_key)
    graph = osmnx.add_edge_grades(graph) 
    # convert node labels
    graph = networkx.relabel.convert_node_labels_to_integers(graph)
    # populate igraph
    graph_ig = igraph.Graph(directed=True)
    graph_ig.add_vertices(list(graph.nodes()))
    graph_ig.add_edges(list(graph.edges()))
    for attr in ('osmid', 'x', 'y'):
        graph_ig.vs[attr] = list(networkx.get_node_attributes(graph, attr).values())
    for attr in ('length', 'grade'):
        graph_ig.es[attr] = list(networkx.get_edge_attributes(graph, attr).values())
    graph_ig.es['streetname'] = [str(s) for s in networkx.get_edge_attributes(graph, 'name').values()]
    return graph_ig

__all__ = ['download_graph']
