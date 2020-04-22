from rdf2vec.samplers import Sampler
from collections import defaultdict

class ObjFreqSampler(Sampler):
    def __init__(self, inverse=False, split=False):
        super(ObjFreqSampler, self).__init__(inverse, split)

    def fit(self, graph):
        super(ObjFreqSampler, self).fit(graph)
        self.counts = {}
        for v in graph._vertices:
            if not v.predicate:
                self.counts[str(v)] = len(graph.get_inv_neighbors(v))

    def get_weight(self, hop):
        return self.counts[str(hop[1])]


class PredFreqSampler(Sampler):
    def __init__(self, inverse=False, split=False):
        super(PredFreqSampler, self).__init__(inverse, split)

    def fit(self, graph):
        super(PredFreqSampler, self).fit(graph)
        self.counts = defaultdict(int)
        for v in graph._vertices:
            if v.predicate:
                self.counts[str(v)] += 1

    def get_weight(self, hop):
        return self.counts[str(hop[0])]


class ObjPredFreqSampler(Sampler):
    def __init__(self, inverse=False, split=False):
        super(ObjPredFreqSampler, self).__init__(inverse, split)

    def fit(self, graph):
        super(ObjPredFreqSampler, self).fit(graph)
        self.counts = defaultdict(int)
        for v in graph._vertices:
            if v.predicate:
            	# There will always only be 1 object associated with this pred
            	obj = list(graph.get_neighbors(v))[0]
            	self.counts[(str(v), str(obj))] += 1

    def get_weight(self, hop):
        return self.counts[(str(hop[0]), str(hop[1]))]