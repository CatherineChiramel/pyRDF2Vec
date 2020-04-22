from rdf2vec.walkers import Walker
from collections import defaultdict
from hashlib import md5
import networkx as nx
import numpy as np
import community
import itertools
import math

def check_random_state(seed):
    return np.random
community.community_louvain.check_random_state = check_random_state

def sample_from_iterable(x):
    perms = itertools.permutations(x)
    length = math.factorial(len(x))
    rand_ix = np.random.randint(min(length, 10000))
    for _ in range(rand_ix):
        _ = next(perms)
    return next(perms)
np.random.permutation = lambda x: next(itertools.permutations(x))#sample_from_iterable

class CommunityWalker(Walker):
    def __init__(self, depth, walks_per_graph, sampler=None, hop_prob=0.1, resolution=1):
        super(CommunityWalker, self).__init__(depth, walks_per_graph, sampler)
        self.hop_prob = hop_prob
        self.resolution = resolution

    def _community_detection(self, graph):
        # Convert our graph to a networkX graph
        nx_graph = nx.Graph()

        for v in graph._vertices:
            if not v.predicate:
                name = str(v)
                nx_graph.add_node(name, vertex=v)

        for v in graph._vertices:
            if not v.predicate:
                v_name = str(v)
                # Neighbors are predicates
                for pred in graph.get_neighbors(v):
                    pred_name = str(pred)
                    for obj in graph.get_neighbors(pred):
                        obj_name = str(obj)
                        nx_graph.add_edge(v_name, obj_name)

        # This will create a dictionary that maps the URI on a community
        partition = community.best_partition(nx_graph, 
                                             resolution=self.resolution)
        self.labels_per_community = defaultdict(list)

        self.communities = {}
        vertices = nx.get_node_attributes(nx_graph, 'vertex')
        for node in partition:
            if node in vertices:
                self.communities[vertices[node]] = partition[node]

        for node in self.communities:
            self.labels_per_community[self.communities[node]].append(node)

    def extract_random_community_walks_bfs(self, graph, root):
        """Extract random walks of depth - 1 hops rooted in root."""
        # Initialize one walk of length 1 (the root)

        walks = {(root,)}

        for i in range(self.depth):
            # In each iteration, iterate over the walks, grab the
            # last hop, get all its neighbors and extend the walks
            walks_copy = walks.copy()
            for walk in walks_copy:
                hops = graph.get_hops(walk[-1])
                if len(hops) > 0:
                    walks.remove(walk)
                for (pred, obj) in hops:
                    walks.add(walk + (pred, obj))
                    if neighbor in self.communities and np.random.random() < self.hop_prob:
                        community_nodes = self.labels_per_community[self.communities[neighbor]]
                        rand_jump = np.random.choice(community_nodes)
                        walks.add(walk + (rand_jump, ))

        # Return a numpy array of these walks
        return list(walks)

    def extract_random_community_walks_dfs(self, graph, root):
        """Extract random walks of depth - 1 hops rooted in root."""
        # Initialize one walk of length 1 (the root)
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
                if hop in self.communities and np.random.random() < self.hop_prob:
                    community_nodes = self.labels_per_community[self.communities[neighbor]]
                    rand_jump = np.random.choice(community_nodes)
                    new = new + (rand_jump, )
                else:
                    new = new + (hop[0], hop[1])
            walks.append(new)
        return list(set(walks))

    def extract_random_community_walks(self, graph, root):
        if self.walks_per_graph is None:
            return self.extract_random_community_walks_bfs(graph, str(root))
        else:
            return self.extract_random_community_walks_dfs(graph, str(root))

    def extract(self, graph, instances):
        self._community_detection(graph)
        canonical_walks = set()
        for instance in instances:
            walks = self.extract_random_community_walks(graph, str(instance))
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
