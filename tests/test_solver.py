import unittest
import json
import osmnx
import networkx
import igraph
import os
#from path_finding.solver import *

this_files_dir = os.path.dirname(os.path.realpath(__file__))

def test_1():
    #filename = os.path.join(this_files_dir, 'test_graphs', 'test_graph_1.gz')
    filename = os.path.join(this_files_dir, 'test_graphs', 'out.zip')

    #filename = ('test_graphs/simple.xml')
    #print(os.path)
    #if os.path.exists(filename):
    #graph = igraph.Graph.Read_GraphMLz(filename)
    graph = igraph.Graph.Read_GraphML(filename)
    
    #graph.WriteML()
    #igraph.Graph.write_graphml(graph, filename)
    return

if __name__ == '__main__':
    test_1()
