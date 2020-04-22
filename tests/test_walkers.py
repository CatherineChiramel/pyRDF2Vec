import random
import os
import numpy as np
import rdflib
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix, accuracy_score
from sklearn.manifold import TSNE

from rdf2vec.graphs import KnowledgeGraph
from rdf2vec.walkers import (RandomWalker, CommunityWalker, AnonymousWalker,
							 HalkWalker, NGramWalker, WalkletWalker,
							 WeisfeilerLehmanWalker)
from rdf2vec.samplers import UniformSampler
from rdf2vec import RDF2VecTransformer

import warnings
warnings.filterwarnings('ignore')

np.random.seed(42)
random.seed(42)

#########################################################################
#                              DATA LOADING                             #
#########################################################################

# Load our train & test instances and labels
test_data = pd.read_csv('sample/MUTAG/MUTAG_test.tsv', sep='\t')
train_data = pd.read_csv('sample/MUTAG/MUTAG_train.tsv', sep='\t')

train_entities = [rdflib.URIRef(x) for x in train_data['bond']]
train_labels = train_data['label_mutagenic']

test_entities = [rdflib.URIRef(x) for x in test_data['bond']]
test_labels = test_data['label_mutagenic']

all_entities = train_entities + test_entities
all_labels = list(train_labels) + list(test_labels)

# Define the label predicates, all triples with these predicates
# will be excluded from the graph
label_predicates = [
    'http://dl-learner.org/carcinogenesis#isMutagenic'
]

# Convert the rdflib to our KnowledgeGraph object
kg = KnowledgeGraph('sample/MUTAG/mutag.owl', label_predicates=label_predicates)

walkers = [
	('Random', RandomWalker(2, 5, UniformSampler())),
	('Anonymous', AnonymousWalker(2, 5, UniformSampler())),
	('HALK', HalkWalker(2, 5, UniformSampler())),
	('Walklet', NGramWalker(2, 5, UniformSampler())),
	('NGram', WalkletWalker(2, 5, UniformSampler())),
	('Weisfeiler-Lehman', WeisfeilerLehmanWalker(2, 5, UniformSampler())),
	('Community', CommunityWalker(2, 5, UniformSampler())),
]

for name, walker in walkers:
	print('Testing {}...'.format(name))
	transformer = RDF2VecTransformer(walkers=[walker], sg=1)
	walk_embeddings = transformer.fit_transform(kg, all_entities)