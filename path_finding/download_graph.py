import osmnx
import networkx
import igraph

google_maps_api_key = 'ask_julian'

def get_graph(latitude: float, longitude: float, radius: float) -> igraph.Graph:
    '''Constructs a graph from street networks within a specified location.
    
    Args:
        latitude (float): the latitude of the center of the location
        longitude (float): the longitude of the center of the location
        radius (float): half the sidelength of the location covered
    Returns:
        An igraph containing the street network within the specified location.
        Nodes have 'x' (latitude), 'y' (longitude), and 'osmid' (id) attributes.
        Edges have 'length' (distance), 'grade' (change in elevation), and 'name' attributes.
    '''
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
    for attr in ('length', 'grade', 'name'):
        graph_ig.es[attr] = list(networkx.get_edge_attributes(graph, attr).values())
    graph_ig.es[attr] = list(networkx.get_edge_attributes(graph, attr).values())
    # return igraph
    return graph_ig
