from rdf2vec.walkers import RandomWalker
from rdf2vec.graph import Vertex
import numpy as np
from hashlib import md5

class AnonymousWalker(RandomWalker):
    def __init__(self, depth, walks_per_graph, sampler):
        super(AnonymousWalker, self).__init__(depth, walks_per_graph, sampler)

    def extract(self, graph, instances):
        canonical_walks = set()
        for instance in instances:
            walks = self.extract_random_walks(graph, instance)
            for walk in walks:
                canonical_walk = []
                str_walk = [str(x) for x in walk]
                for i, hop in enumerate(walk):
                    if i == 0:
                        canonical_walk.append(str(hop))
                    else:
                        canonical_walk.append(str(str_walk.index(str(hop))))
                canonical_walks.add(tuple(canonical_walk))

        return canonical_walks
