import numpy as np


class Sampler():
    def __init__(self, inverse=False, split=False):
        self.inverse = inverse
        self.split = split

    def fit(self, graph):
        if self.split:
	        self.degrees = {}
	        for v in graph._vertices:
	            if not v.predicate:
	                self.degrees[str(v)] = len(graph.get_inv_neighbors(v))

    def initialize(self):
        """We will tag vertices that appear at the max_depth
        or of which all their children are tagged"""
        self.visited = set()

    def sample_neighbor(self, graph, walk, last):
        # Get the neighbors that are not yet tagged.
        neighbors = [x for x in graph.get_hops(walk[-1]) 
                     if (x, len(walk)) not in self.visited]

        # If there are no untagged neighbors, then tag
        # this vertex and return None
        if len(neighbors) == 0:
            if len(walk) > 2:
                self.visited.add(((walk[-2], walk[-1]), len(walk) - 2))
            return None

        # Calculate weights of untagged neighbors
        weights = [self.get_weight(hop) for hop in neighbors]
        if self.inverse:
            weights = [max(weights) - (x - min(weights)) for x in weights]
        if self.split:
        	weights = [w / self.degrees[v[1]] 
        	           for w, v in zip(weights, neighbors)]
        weights = [x / sum(weights) for x in weights]

        # Sample a random neighbor and add them to visited if needed.
        rand_ix = np.random.choice(range(len(neighbors)), p=weights)
        if last:
            self.visited.add((neighbors[rand_ix], len(walk)))
        return neighbors[rand_ix]

    def get_weight(self, hop):
        raise NotImplementedError('This has to be implemented')