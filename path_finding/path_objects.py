import igraph
import numpy as np
import typing


class path_profile(object):
    '''A path profile object represents the altitude / distance profile of a path.

    Attributes:
        altitudes: a list of altitudes, in meters, representing the altitude (relative to the starting point) of
            each vertex. The `ith` entry represents the altitude change after traversing the first `i` edges in the path,
            or equivalently, the first `i+1` vertices. The first element will always be 0. Note that if there are `|E|` edges 
            in the path, there will be `|E|+1` vertices, so this list will contain `|E|+1` altitudes.
            If the path is a loop, the last element should be close to 0, by conservation.
        distances: a list of distances, in meters, representing the distances traversed at each vertex.
            The `ith` entry represents the distance traveled after traversing the first `i` edges in the path,
            or equivalently, the first `i+1` vertices. The first element will always be 0, and the elements will be monotonically increasing.
            Note that if there are `|E|` edges in the path, there will be `|E|+1` vertices, so this list will contain `|E|+1` distances.
        total_uphill: the total uphill altitude travelled, in meters.
        total_distance: the total distance travelled, in meters.

    
    Example:
            >>> from path_finding import *
            >>> graph = download_graph(50, 50, 1)
            >>> profile = path_profile().from_path(graph, [0,2,1,3])
            >>> profile.altitudes
            [0, -1.3103053999999998, -4.1448941999999995, 0.31178560000000033, 1.6220910000000002]
            >>> profile.distances
            [0, 29.578, 64.922, 102.12299999999999, 131.701]
            >>> profile.get_slopes()
            [-0.04429999999999999, -0.04366145220418348, 0.0436403141309989, 0.009949092262017751]
            >>> profile.total_uphill
            5.7669852
            >>> profile.total_distance
            131.701

    '''
    def __init__(self):
        self.altitudes: typing.List[float] = [0]
        self.distances: typing.List[float] = [0]
        self.total_uphill: float = 0
        self.total_distance: float = 0
    
    def get_slopes(self) -> typing.List[float]:
        '''Returns the slopes of each edge in the path. If there are `|E|` edges in the path, this list
        will contain `|E|` elements, where the `ith` element gives the slope of the `ith` edge. '''
        slopes = []
        for i in range(1, len(self.altitudes)):
            slopes.append((self.altitudes[i] - self.altitudes[i-1]) / self.distances[i])
        return slopes

    def from_path(self, graph: igraph.Graph, path: typing.List[int]):
        '''Constructs the path profile from a graph and a path (list of edge ids).

        Example:
            >>> from path_finding import *
            >>> graph = download_graph(50, 50, 1)
            >>> profile = path_profile().from_path(graph, [0,2,1,3])
        '''
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
        '''Constructs the path profile from a graph and a path (list of edge ids).

        Args:
            uphill: the total uphill altitude in the path, in meters
            distance: the total distance travelled in the path, in meters

        Example:
            >>> from path_finding import *
            >>> graph = download_graph(50, 50, 1)
            >>> path_profile().from_total_uphill_and_dist(100, 500)
        '''
        self.altitudes = [0, uphill]
        self.distances = [0, distance]
        self.total_distance = distance
        self.total_uphill = uphill
        return self




class path_object(object):
    '''A path object encapsulates a path in a graph, providing useful information and convenience functions.

    Args:
        graph: the graph that the path is part of.
        eids: a list of edge id's in the path.
        profile: (optional) a path profile of the path. If not provided, will be generated.

    '''
    def __init__(self, graph: igraph.Graph,
        eids: typing.List[int],
        profile: typing.Union[path_profile, None]=None):
        self.graph = graph
        self.eids = eids
        self.profile = profile
    
    def get_profile(self) -> path_profile:
        ''' Returns the path's profile. This method is memoized. '''
        if self.profile is None:
            self.profile = path_profile().from_path(self.graph, self.eids)
        return self.profile
    
    def get_edge_ids(self) -> typing.List[int]:
        ''' Returns the edge ids in the path. '''
        return self.eids
    
    def get_vertex_ids(self) -> typing.List[int]:
        ''' Returns the vertex ids in the path. Note that if there are `|E|` edges in the path, there will be `|E|+1` vertices. '''
        vids = [self.graph.es[self.eids[0]].source]
        for eid in self.eids:
            vids.append(self.graph.es[eid].target)
        return vids
    
    def get_vertex_locations(self) -> typing.List[typing.Dict[str, float]]:
        ''' Returns a list of `(latitude, longitude)` pairs, as a dict. Note that if there are `|E|` edges in the path, there will be `|E|+1` vertices. '''
        locs = []
        for vid in self.get_vertex_ids():
            v = self.graph.vs[vid]
            locs.append({'latitude': v['y'], 'longitude': v['x']})
        return locs
    
    def get_text_directions(self) -> str:
        ''' Returns directions for the path, in plain english. 
        TODO: make sure that the left/right/straight navigation is correct. Test with negative lat/longs.
        '''
        g = self.graph
        to_angle = lambda v1, v2: np.degrees(np.math.atan2(np.linalg.det([v1,v2]), np.dot(v1,v2))) % 360
        names = [g.es[e]['streetname'] for e in self.eids]
        lengths = [g.es[e]['length'] for e in self.eids]
        vectors = np.array([
            [
                g.vs[g.es[eid].target]['x'] - g.vs[g.es[eid].source]['x'],
                g.vs[g.es[eid].target]['y'] - g.vs[g.es[eid].source]['y']
            ]
            for eid in self.eids
        ])
        text = 'Go to {}. Continue for {:1f} meters.'.format(names[0], lengths[0])
        for i in range(1, len(self.eids)):
            angle = to_angle(vectors[i-1], vectors[i])
            if angle < 20 or angle > 340:
                text += '\nContinue straight onto {} for {:1f} meters'.format(names[i], lengths[i])
            elif angle > 180:
                text += '\nTurn right onto {}, continue for {:1f} meters'.format(names[i], lengths[i])
            else:
                text += '\nTurn left onto {}, continue for {:1f} meters'.format(names[i], lengths[i])
        return text



__all__ = ['path_profile', 'path_object']
