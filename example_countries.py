import random
import os
import numpy as np
import rdflib
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix, accuracy_score
from sklearn.manifold import TSNE

from rdf2vec.graphs import KnowledgeGraph, RemoteKnowledgeGraph
from rdf2vec.walkers import RandomWalker
from rdf2vec import RDF2VecTransformer

import warnings
warnings.filterwarnings('ignore')

np.random.seed(42)
random.seed(42)

#########################################################################
#                              DATA LOADING                             #
#########################################################################

# Load our train & test instances and labels
data = pd.read_csv('sample/CountriesCities/entities.tsv', sep='\t')

all_entities = [rdflib.URIRef(x) for x in data['location']]
all_labels = data['label']

# Define the label predicates, all triples with these predicates
# will be excluded from the graph
label_predicates = [
    'www.w3.org/1999/02/22-rdf-syntax-ns#type'
]

# Convert the rdflib to our KnowledgeGraph object
# kg = KnowledgeGraph('sample/CountriesCities/countries.ttl', 
#                     label_predicates=label_predicates,
#                     format='turtle')
kg = RemoteKnowledgeGraph('https://dbpedia.org/sparql')

#########################################################################
#                          CREATING EMBEDDINGS                          #
#########################################################################

# We'll all possible walks of depth 6 (3 hops)
random_walker = RandomWalker(3, 250)

# Create embeddings with random walks
transformer = RDF2VecTransformer(walkers=[random_walker], sg=1)
walk_embeddings = transformer.fit_transform(kg, all_entities)

#########################################################################
#                                 T-SNE PLOT                            #
#########################################################################

# Create t-SNE embeddings from RDF2Vec embeddings (dimensionality reduction)
walk_tsne = TSNE(random_state=42)
X_walk_tsne = walk_tsne.fit_transform(walk_embeddings)

# Define a color map
colors = ['r', 'g']
color_map = {}
for i, label in enumerate(set(all_labels)):
    color_map[label] = colors[i]

# Plot the train embeddings
plt.figure(figsize=(10, 4))
plt.scatter(
    X_walk_tsne[:, 0],
    X_walk_tsne[:, 1],
    edgecolors=[color_map[i] for i in all_labels],
    facecolors=[color_map[i] for i in all_labels],
)

for x, y, t in zip(X_walk_tsne[:, 0], X_walk_tsne[:, 1], all_entities):
    plt.annotate(t.split('/')[-1], (x, y))


# Show & save the figure
plt.title('pyRDF2Vec', fontsize=32)
plt.axis('off')
plt.show()
