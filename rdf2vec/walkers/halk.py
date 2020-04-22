from collections import defaultdict
from rdf2vec.walkers import RandomWalker
import numpy as np
from hashlib import md5

class HalkWalker(RandomWalker):
    def __init__(self, depth, walks_per_graph, sampler=None, 
                 freq_thresholds=[0.001]):
        super(HalkWalker, self).__init__(depth, walks_per_graph, sampler)
        self.freq_thresholds = freq_thresholds
        # self.lb_freq_threshold = lb_freq_threshold

    def extract(self, graph, instances):
        canonical_walks = set()
        all_walks=[]
        for instance in instances:
            walks = self.extract_random_walks(graph, str(instance))
            all_walks.extend(walks)

        freq = defaultdict(set)
        for i in range(len(all_walks)):
            for hop in all_walks[i]:
                freq[str(hop)].add(i)

        for freq_threshold in self.freq_thresholds:
            uniformative_hops = set()
            for hop in freq:
                if len(freq[hop])/len(all_walks) < freq_threshold:
                    uniformative_hops.add(hop)

            for walk in all_walks:
                canonical_walk = []
                for i, hop in enumerate(walk):
                    if i == 0:
                        canonical_walk.append(str(hop))
                    else:
                        if str(hop) not in uniformative_hops:
                            digest = md5(str(hop).encode()).digest()[:8]
                            canonical_walk.append(str(digest))
                canonical_walks.add(tuple(canonical_walk))
                
        return canonical_walks
