from rdf2vec.walkers import Walker
import numpy as np
from hashlib import md5


class RandomWalker(Walker):
    def __init__(self, depth, walks_per_graph, sampler=None):
        super(RandomWalker, self).__init__(depth, walks_per_graph, sampler)

    def extract_random_walks_bfs(self, graph, root):
        """Breadth-first search to extract all possible walks."""
        walks = {(root,)}
        for i in range(self.depth):
            walks_copy = walks.copy()
            for walk in walks_copy:
                hops = graph.get_hops(walk[-1])
                if len(hops) > 0:
                    walks.remove(walk)
                for (pred, obj) in hops:
                    walks.add(walk + (pred, obj))
        return list(walks)

    def extract_random_walks_dfs(self, graph, root):
        """Depth-first search to extract a limited number of walks."""
        # TODO: Currently we are allowing duplicate walks in order
        # TODO: to avoid infinite loops. Can we do this better?

        self.sampler.initialize()

        walks = []
        while len(walks) < self.walks_per_graph:
            new = (root,)
            d = (len(new) - 1) // 2
            while d // 2 < self.depth:
                last = d == self.depth - 1
                hop = self.sampler.sample_neighbor(graph, new, last)
                if hop is None:
                    break
                new = new + (hop[0], hop[1])
            walks.append(new)
        return list(set(walks))

    def extract_random_walks(self, graph, root):
        if self.walks_per_graph is None:
            return self.extract_random_walks_bfs(graph, str(root))
        else:
            return self.extract_random_walks_dfs(graph, str(root))

    def extract(self, graph, instances):
        """Extracts the walks and processes them for the embedding model."""
        self.sampler.fit(graph)

        canonical_walks = set()
        for i, instance in enumerate(instances):
            walks = self.extract_random_walks(graph, instance)
            # if i == 0:
            #     for walk in walks:
            #         print('-->'.join([str(x).split('/')[-1] for x in walk]))
            for walk in walks:
                canonical_walk = []
                for i, hop in enumerate(walk):
                    if i == 0 or i % 2 == 1:
                        canonical_walk.append(str(hop))
                    else:
                        digest = md5(str(hop).encode()).digest()[:8]
                        canonical_walk.append(str(digest))

                canonical_walks.add(tuple(canonical_walk))

        return canonical_walks
