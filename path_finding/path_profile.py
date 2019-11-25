import igraph
import numpy as np
import typing

class path_profile(object):
    def __init__(self):
        self.altitudes = [0]
        self.distances = [0]
        self.total_uphill = 0
        self.total_distance = 0

    def from_path(self, graph: igraph.Graph, path: typing.List[int]):
        self.altitudes = [0]
        self.distances = [0]
        self.total_uphill = 0

        for edge_id in path:
            edge = graph.es[edge_id]
            grade = edge['grade']
            length = edge['length']
            self.total_uphill += max(0, length * grade)
            self.distances.append(self.distances[-1] + length)
            self.altitudes.append(self.altitudes[-1] + (length * grade))
        
        self.total_distance = self.distances[-1]

        return self
    
    def from_total_uphill_and_dist(self, uphill: float, distance: float):
        self.altitudes = [0, uphill]
        self.distances = [0, distance]
        self.total_distance = distance
        self.total_uphill = uphill
        return self


__all__ = ['path_profile']
