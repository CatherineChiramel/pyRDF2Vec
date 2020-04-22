from rdf2vec.walkers import RandomWalker
import numpy as np
from hashlib import md5


class WalkletWalker(RandomWalker):
    def __init__(self, depth, walks_per_graph, sampler=None):
        super(WalkletWalker, self).__init__(depth, walks_per_graph, sampler)

    def extract(self, graph, instances):
        canonical_walks = set()
        for instance in instances:
            walks = self.extract_random_walks(graph, str(instance))
            for walk in walks:
                for n in range(1, len(walk)):
                    canonical_walks.add((str(walk[0]), str(walk[n])))
        return canonical_walks
