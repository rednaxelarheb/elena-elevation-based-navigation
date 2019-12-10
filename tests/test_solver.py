import unittest
import json
import osmnx
import networkx
import igraph
import os
from path_finding import *
#from path_finding.solver import *
#from path_finding.download_graph import *
#from path_finding.path_objects import *

'''
this_files_dir = os.path.dirname(os.path.realpath(__file__))

def test_1():
    #filename = os.path.join(this_files_dir, 'test_graphs', 'test_graph_1.gz')
    filename = os.path.join(this_files_dir, 'test_graphs', 'test_graph_1')

    #filename = ('test_graphs/simple.xml')
    #print(os.path)
    #if os.path.exists(filename):
    #graph = igraph.Graph.Read_GraphMLz(filename)
    graph = igraph.Graph.Read_GraphML(filename)
    
    #graph.WriteML()
    #igraph.Graph.write_graphml(graph, filename)
    return
'''

def test_profile_init():
    #test the empty constructor
    profile = path_profile()
    assert(profile) #profile not null
    profile = None

    #test the "from_total_uphill_and_dist" constructor
    profile = path_profile().from_total_uphill_and_dist(15.0, 100.0)
    assert(profile) #profile from_total_uphill_and_dist not null
    assert(profile.total_uphil == 15.0) #profile from_total_uphill_and_dist correct total_uphil 
    assert(profile.total_distance == 100.0) #profile from_total_uphill_and_dist correct total_distance 
    return

def test_path_init():
    #test constructor
    in_graph = igraph.Graph()
    in_eids = [10,20]
    in_profile = path_profile()
    path = path_object(in_graph,in_eids,in_profile)
    assert(path) #path not null
    return

def test_path_get_edge_ids():
    filename = os.path.join(this_files_dir, 'test_graphs', 'test_graph_0')
    in_graph = igraph.Graph().Read_GraphML(filename)
    in_profile = path_profile().from_total_uphill_and_dist(0.0, 10.0)
    in_eids = [0,1]
    path = path_object(in_graph,in_eids,in_profile)

    e_ids = path.get_edge_ids()
    assert(e_ids[0] == 0)
    assert(e_ids[1] == 1)
    return

def test_path_get_vertex_ids():
    filename = os.path.join(this_files_dir, 'test_graphs', 'test_graph_0')
    in_graph = igraph.Graph().Read_GraphML(filename)
    in_profile = path_profile().from_total_uphill_and_dist(0.0, 10.0)
    in_eids = [0,1]
    path = path_object(in_graph,in_eids,in_profile)

    v_ids = path.get_vertex_ids()
    assert(v_ids[0] == 'n0')
    assert(v_ids[1] == 'n1')
    return

def test_path_get_text_instructions():
    filename = os.path.join(this_files_dir, 'test_graphs', 'test_graph_4')
    in_graph = igraph.Graph().Read_GraphML(filename)
    in_profile = path_profile().from_total_uphill_and_dist(0.0, 18.0)
    in_eids = [0,1,2]
    path = path_object(in_graph,in_eids,in_profile)
    str_instructions = path.get_text_directions()
    list_instructions = str_instructions.split('\n')
    assert(len(list_instructions) == 3)
    assert(list_instructions[0] == "Continue straight onto A-east for 5.0 meters")
    assert(list_instructions[1] == "Turn left onto B-north, continue for 5.0 meters")
    assert(list_instructions[2] == "Turn left onto C-west, continue for 8.0 meters")
    return

def test_path_get_vertex_locations():
    filename = os.path.join(this_files_dir, 'test_graphs', 'test_graph_4')
    in_graph = igraph.Graph().Read_GraphML(filename)
    in_profile = path_profile().from_total_uphill_and_dist(0.0, 18.0)
    in_eids = [0,1,2]
    path = path_object(in_graph,in_eids,in_profile)
    vertex_dict = path.get_vertex_locations()
    assert(len(vertex_dict) == 3)
    assert(vertex_dict[0].'latitude' == 0)
    assert(vertex_dict[0].'longitude' == 0)
    assert(vertex_dict[1].'latitude' == 5)
    assert(vertex_dict[1].'longitude' == 0)
    assert(vertex_dict[2].'latitude' == 5)
    assert(vertex_dict[2].'longitude' == 5)
    return

def test_solver_init():
    testgraph = igraph.Graph()
    testprofile = path_profile().from_total_uphill_and_dist(100, 500)
    sol = solver()
    sol = solver(igraph.Graph,15.0,15.0)

if __name__ == '__main__':
    test_profile_init()
    test_path_init()
    test_solver_init()
    test_path_get_edge_ids()
    test_path_get_vertex_ids()
    test_path_get_text_instructions()
    test_path_get_vertex_locations()

