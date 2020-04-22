from rdf2vec.samplers import Sampler
import networkx as nx


class PageRankSampler(Sampler):
    def __init__(self, inverse=False, split=False, alpha=0.85):
        super(PageRankSampler, self).__init__(inverse, split)
        self.alpha = alpha

    def fit(self, graph):
        super(PageRankSampler, self).fit(graph)
        nx_graph = nx.DiGraph()

        for v in graph._vertices:
            if not v.predicate:
                name = v.name
                nx_graph.add_node(name, vertex=v)

        for v in graph._vertices:
            if not v.predicate:
                v_name = v.name
                # Neighbors are predicates
                for pred in graph.get_neighbors(v):
                    pred_name = pred.name
                    for obj in graph.get_neighbors(pred):
                        obj_name = obj.name
                        nx_graph.add_edge(v_name, obj_name)

        self.pageranks = nx.pagerank(nx_graph, alpha=self.alpha)

    def get_weight(self, hop):
        return self.pageranks[str(hop[1])]