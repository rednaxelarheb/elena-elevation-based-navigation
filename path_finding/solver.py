import numpy as np
import typing
import heapq

class solver(object):
    '''
    TODO: document me!
    
    Example:
    >>> solver(graph, 50,50,1,10).solve()
    '''
    def __init__(self, graph: igraph.Graph,
                 latitude: float, longitude: float,
                altitude: float, distance: float,
                tradeoff: typing.Union[None, typing.Callable[[float, float], float]]=None):
        self.graph = graph
        assert graph.vcount() > 0, 'Graph must contain at least 1 vertex'
        assert graph.ecount() > 0, 'Graph must contain at least 1 edge'
        self.start = self._find_nearest_vertex(latitude, longitude)
        self.altitude = altitude
        self.distance = distance
        self.tradeoff = tradeoff
        self.max_path_length = 50
        if tradeoff is None:
            self.tradeoff = lambda alt, dist: (
                (abs(self.altitude - alt) / self.altitude)
                + (abs(self.distance - dist) / self.distance))
    
    def _find_nearest_vertex(self, lat: float, long: float) -> int:
        ''' Returns the name of the nearest vertex '''
        best = np.inf
        best_idx = -1
        for idx, node in enumerate(self.graph.vs):
            dist = np.linalg.norm(np.subtract([lat, long], [node['x'], node['y']]))
            if dist <= best:
                best = dist
                best_idx = idx
        return best_idx
    
    def _random_path(self):
        ''' Returns a random path, starting from the `start` vertex,
            who's altitude and distance meets a certain criteria (see the while loop condition)
        '''
        dist = 0
        alt = 0
        path = [self.start]
        while not ((dist > self.distance and alt > self.altitude)
               or len(path) >= self.max_path_length
               or self.tradeoff(alt, dist) < 0.1):
            next_node = np.random.choice(self.graph.neighbors(path[-1]))
            edge = self.graph.es[self.graph.get_eid(path[-1], next_node)]
            dist += edge['length']
            alt += abs(edge['grade'])
            path.append(next_node)
        return path, alt, dist
    
    def solve(self):
        ''' TODO: document + comment '''
        def generate():
            p,a,d = self._random_path()
            return (-1*self.tradeoff(a,d), p, a, d)
        heap = [generate() for _ in range(10)]
        heapq.heapify(heap)
        for _ in range(1000):
            heapq.heappush(heap, generate())
            heapq.heappop(heap)
        return [t[1:] for t in sorted(heap, key=lambda t: -1*t[0])]

