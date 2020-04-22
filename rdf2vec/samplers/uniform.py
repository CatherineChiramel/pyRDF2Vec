from rdf2vec.samplers import Sampler


class UniformSampler(Sampler):
    def __init__(self, inverse=False):
        super(UniformSampler, self).__init__(inverse)

    def fit(self, graph):
        pass

    def get_weight(self, hop):
        return 1