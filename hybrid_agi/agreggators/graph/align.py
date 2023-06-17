## The alignement based aggregator.
## Copyright (C) 2023 SynaLinks.
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program. If not, see <https://www.gnu.org/licenses/>.

import numpy as np
from scipy.linalg import orthogonal_procrustes
from hybrid_agi.agreggators.graph.base import BaseGraphAgreggator
from redisgraph import Graph

class AlignmentAgreggator(BaseGraphAgreggator):
    """Class to agreggate graphs using embedding based entity alignment"""

    def agreggate(data:List[Graph]) -> Graph:
        raise NotImplementedError("Not yet implemented.")

    def entity_alignment(embedding_matrix_list:List[np.array]):
        """
        Align the entities from multiple knowledge graphs

        Args:
            entity_embeddings (List[np.array]): The list of entity embedding matrices (nb_entity, embed_dim)
        """
        # Determine the maximum embedding dimensionality across all knowledge graphs
        max_dim = max(e.shape[1] for e in embedding_matrix_list)

        # Pad all embeddings with zeros up to the maximum dimensionality
        for i in range(len(embedding_matrix_list)):
            embedding_matrix_list[i] = np.pad(embedding_matrix_list[i], ((0, 0), (0, max_dim - embedding_matrix_list[i].shape[1])), mode='constant')

        # Pick an arbitrary knowledge graph to use as the reference
        ref_kg_idx = 0

        # Align the embeddings of all other knowledge graphs to the reference
        for i in range(len(embedding_matrix_list)):
            if i != ref_kg_idx:
                mtx1, mtx2, disparity = orthogonal_procrustes(embedding_matrix_list[ref_kg_idx], embedding_matrix_list[i])
                embedding_matrix_list[i] = np.dot(embedding_matrix_list[i], mtx2.T)

        # Compute the pairwise cosine similarities between the aligned embeddings of all entities from all knowledge graphs
        similarity_matrix = None
        for i in range(len(embedding_matrix_list)):
            for j in range(i+1, len(embedding_matrix_list)):
                cos_sim = np.dot(embedding_matrix_list[i], embedding_matrix_list[j].T) / (np.linalg.norm(embedding_matrix_list[i], axis=1)[:, np.newaxis] * np.linalg.norm(embedding_matrix_list[j], axis=1))
                if similarity_matrix is None:
                    similarity_matrix = cos_sim
                else:
                    similarity_matrix = np.maximum(similarity_matrix, cos_sim)

        # Find the highest similarity score for each entity in each knowledge graph
        aligned_entities = []
        for kg_idx, kg_emb in enumerate(embedding_matrix_list):
            kg_to_ref = similarity_matrix.argmax(axis=1)
            ref_to_kg = similarity_matrix.argmax(axis=0)
            for i in range(kg_emb.shape[0]):
                j = kg_to_ref[i]
                if similarity_matrix[i, j] >= self.similarity_threshold and ref_to_kg[j] == i:
                    aligned_entities.append((kg_idx, i, ref_kg_idx, j))

        return aligned_entities