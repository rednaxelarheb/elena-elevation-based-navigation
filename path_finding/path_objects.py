import igraph
import numpy as np
import typing

'''
TODO the `path_profile` and `path_object` objects need to be tested and documented
'''

class path_profile(object):
    def __init__(self):
        self.altitudes = [0]
        self.distances = [0]
        self.total_uphill = 0
        self.total_distance = 0
    
    def get_slopes(self) -> typing.List[float]:
        ''' Returns the slopes of each edge in the path. '''
        slopes = []
        for i in range(1, len(self.altitudes)):
            slopes.append((self.altitudes[i] - self.altitudes[i-1]) / self.distances[i])
        return slopes

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




class path_object(object):
    def __init__(self, graph: igraph.Graph,
        eids: typing.List[int],
        profile: typing.Union[path_profile, None]=None):
        self.graph = graph
        self.eids = eids
        self.profile = profile
    
    def get_profile(self) -> path_profile:
        if self.profile is None:
            self.profile = path_profile().from_path(self.graph, self.eids)
        return self.profile
    
    def get_edge_ids(self) -> typing.List[int]:
        return self.eids
    
    def get_vertex_ids(self) -> typing.List[int]:
        vids = [self.graph.es[self.eids[0]].source]
        for eid in self.eids:
            vids.append(self.graph.es[eid].target)
        return vids
    
    def get_vertex_locations(self) -> typing.List[typing.Dict[str, float]]:
        ''' Returns a list of (latitude, longitude) pairs, as a dict '''
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
