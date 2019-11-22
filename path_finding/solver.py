import igraph
import numpy as np
import typing
import heapq
from path_finding.path_profile import path_profile

class solver(object):
    ''' A solver object that finds a route for a starting location and desired grade/distance profile.

    Args:
        graph: an igraph object (see `path_finding.download_graph.download_graph`)
        latitude: the latitude of the starting location
        longitude: the longitude of the starting location
        altitude: the desired altitude change
        distance: the desired distance traveled

    Example:
    >>> solver(graph, 50,50,100,500).solve()
    '''
    def __init__(self, graph: igraph.Graph,
                 latitude: float, longitude: float,
                altitude: float, distance: float,
                cost_fn: typing.Union[None, typing.Callable[[path_profile], float]]=None):
        self.graph = graph
        assert graph.vcount() > 0, 'Graph must contain at least 1 vertex'
        assert graph.ecount() > 0, 'Graph must contain at least 1 edge'
        self.start = self._find_nearest_vertex(latitude, longitude)
        self.altitude = altitude
        self.distance = distance
        self.max_path_length = 50
        if cost_fn is None:
            def default_cost_fn(profile):
                err_alt = abs(self.altitude - profile.total_uphill) / max(1e-6, self.altitude)
                err_dist = abs(self.distance - profile.total_distance) / max(1e-6, self.distance)
                return err_alt + err_dist
            self.cost_fn = default_cost_fn
        else:
            self.cost_fn = cost_fn
    
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
        last_node = self.start
        edge_path = []

        def should_terminate(alt, dist):
            if alt > self.altitude: return True
            elif dist > self.distance: return True
            else: return False
        
        while not should_terminate(alt, dist):
            next_node = np.random.choice(self.graph.neighbors(last_node))
            edge_id = self.graph.get_eid(last_node, next_node)
            edge = self.graph.es[edge_id]
            dist += edge['length']
            alt += abs(edge['length'] * edge['grade'])
            edge_path.append(edge_id)
            last_node = next_node
        
        edge_path += reversed(edge_path)
        return edge_path


    def _reconnect_path(self, path: typing.List[int], max_expansions: int=500) -> typing.Union[None, typing.List[int]]:
        # pick a random vertex in the path that is not the source
        search_source_idx = np.random.randint(0, len(path)-1)
        search_source = self.graph.es[search_source_idx].target
        vids_in_path = set([self.graph.es[e].target for e in path[search_source_idx+1:]])
        # run BFS from `search_source`, search for a node in `vids_in_path`
        layer = [search_source]
        next_layer = []
        expansions = 0
        parents = dict()
        while True:
            for node in layer:
                # check if we've exceeded our expansion budget
                if expansions >= max_expansions:
                    return None
                expansions += 1
                # check if we found a node on the original path
                if node in vids_in_path:
                    search_end = node
                    break
                # add children
                for child in self.graph.neighbors(node):
                    if child in parents:
                        continue
                    else:
                        parents[child] = node
                        next_layer.append(child)
            layer = next_layer
            next_layer = []
        # reconstruct path, from source -> search_source -> search_end -> source
        # connect source -> search_source
        beginning = []
        for eid in path:
            beginning.append(eid)
            if self.graph.es[eid].target == search_source: break
        # connect search_source -> search_end
        new_connection = []
        last_vertex = search_end
        while last_vertex != search_source:
            prev = parents[last_vertex]
            new_connection.append(self.graph.get_eid(prev, last_vertex))
            last_vertex = prev
        new_connection = reversed(new_connection)
        # connect search_end -> path_end
        ending = []
        for eid in reversed(path):
            ending.append(eid)
            if self.graph.es[eid].source == search_end: break
        ending = reversed(ending)
        # chain together the 3 paths
        reconnected = beginning + new_connection + ending
        return reconnected


    def solve(self, k_solutions = 100) -> typing.List[typing.Tuple[typing.List[int], float, float]]:
        ''' Finds a route for a starting location and desired grade/distance profile.
        
        Args:
            k_solutions: the number of solutions to return
        Returns:
            A list with `k_solutions` elements, where each element is a dictionary with keys (path, profile), where
                - `path` is a list of integers that index edges in the graph.
                - `profile` is a `path_profile` object
        '''
        # we negate the cost so that our heap is a max heap,
        # allowing us to efficiently maintain the k best (lowest cost) solutions
        counter = [0] # use this for breaking ties in the heap
        
        def generate():
            path = self._random_path()
            profile = path_profile().from_path(self.graph, path)
            counter[0] -= 1
            return (-1*self.cost_fn(profile), counter[0], path, profile)
        
        def perturb(heap_item):
            _, _, old_path, _ = heap_item
            new_path = self._reconnect_path(old_path)
            if new_path is None:
                return None
            else:
                profile = path_profile().from_path(self.graph, new_path)
                counter[0] -= 1
                return (-1*self.cost_fn(profile), counter[0], new_path, profile)

        heap = [generate() for _ in range(k_solutions)]
        heapq.heapify(heap)

        for _ in range(1000):
            heapq.heappush(heap, generate())
            heapq.heappop(heap)
        
        for _ in range(1000):
            response = perturb(heap[np.random.randint(0, len(heap))])
            if response is not None:
                heapq.heappush(heap, response)
                heapq.heappop(heap)

        return [{'path': t[2], 'profile': t[3]} for t in sorted(heap, key=lambda t: -1*t[0])]

