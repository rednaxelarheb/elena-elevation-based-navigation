import igraph
import numpy as np
import typing
import heapq

class solver(object):
    ''' A solver object that finds a route for a starting location and desired grade/distance profile.

    Args:
        graph: an igraph object (see `path_finding.download_graph.download_graph`)
        latitude: the latitude of the starting location
        longitude: the longitude of the starting location
        altitude: the desired altitude change
        distance: the desired distance traveled

    Example:
    >>> solver(graph, 50,50,1,10).solve()
    '''
    def __init__(self, graph: igraph.Graph,
                 latitude: float, longitude: float,
                altitude: float, distance: float,
                cost_fn: typing.Union[None, typing.Callable[[float, float], float]]=None):
        self.graph = graph
        assert graph.vcount() > 0, 'Graph must contain at least 1 vertex'
        assert graph.ecount() > 0, 'Graph must contain at least 1 edge'
        self.start = self._find_nearest_vertex(latitude, longitude)
        self.altitude = altitude
        self.distance = distance
        self.cost_fn = cost_fn
        self.max_path_length = 50
        if cost_fn is None:
            self.cost_fn = lambda alt, dist: (
                (abs(self.altitude - alt) / max(1e-6, self.altitude))
                + (abs(self.distance - dist) / max(1e-6, self.distance)))
    
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

        def should_terminate(alt, dist):
            if alt > self.altitude: return True
            elif dist > self.distance: return True
            elif self.cost_fn(alt, dist) < 0.1: return True
            else: return False
        
        while not should_terminate(alt, dist):
            next_node = np.random.choice(self.graph.neighbors(path[-1]))
            edge = self.graph.es[self.graph.get_eid(path[-1], next_node)]
            dist += edge['length']
            alt += abs(edge['grade'])
            path.append(next_node)
        
        path += reversed(path)
        return path, alt, dist
    
    def solve(self, k_solutions = 10) -> typing.List[typing.Tuple[typing.List[int], float, float]]:
        ''' Finds a route for a starting location and desired grade/distance profile.
        
        Args:
            k_solutions: the number of solutions to return
        Returns:
            A list with `k_solutions` elements, where each element is a tuple (path, altitude, distance), where
                - `path` is a list of integers that index edges in the graph.
                - `altitude` is the total positive altitude change
                - `distance` is the distance traveled by the path
        '''
        # we negate the cost so that our heap is a max heap,
        # allowing us to efficiently maintain the k best (lowest cost) solutions
        def generate():
            p,a,d = self._random_path()
            return (-1*self.cost_fn(a,d), p, a, d)
        heap = [generate() for _ in range(k_solutions)]
        heapq.heapify(heap)
        for _ in range(1000):
            heapq.heappush(heap, generate())
            heapq.heappop(heap)
        return [t[1:] for t in sorted(heap, key=lambda t: -1*t[0])]

