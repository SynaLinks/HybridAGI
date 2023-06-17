## The merge aggregator.
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

from typing import List, Optional
from redisgraph import Graph
from hybrid_agi.agreggators.graph.base import BaseGraphAgreggator

class MergeAgreggator(BaseGraphAgreggator):
    """Class to agreggate graphs using RedisGraph MERGE"""
    def agreggate(self, data:List[Graph], metadata:Optional[List[dict]]=None) -> Graph:
        resulting_graph = Graph(
            self.hybridstore.redis_key(
                self.hybridstore.graph_key),
            self.hybridstore.client
        )
        self.hybridstore.metagraph.query('MERGE (:Graph {name:"'+resulting_graph.name+'"})')
        for graph in data:
            self.hybridstore.metagraph.query('MATCH (n:Graph {name:"'+resulting_graph.name+'"}), (m:Graph {name:"'+graph.name+'"}) MERGE (n)-[:CONTAINS]-(m)')
            result = graph.query('MATCH (n) RETURN labels(n),n')
            for record in result.result_set:
                if "name" in record[1].properties:
                    label = record[0][0]
                    name = record[1].properties["name"]
                    resulting_graph.query('MERGE (n:'+label+' {name:"'+name+'"})')
            result = graph.query('MATCH (n)-[r]->(m) RETURN labels(n),n,type(r),labels(m),m')
            for record in result.result_set:
                if "name" in record[1].properties and "name" in record[4].properties:
                    source_label = record[0][0]
                    source_name = record[1].properties["name"]
                    relation_type = record[2]
                    target_label = record[3][0]
                    target_name = record[4].properties["name"]
                    resulting_graph.query(
                        'MATCH (s:'+source_label+
                        ' {name:"'+source_name+
                        '"}), (t:'+target_label+
                        ' {name:"'+target_name+
                        '"}) MERGE (s)-[:'+relation_type+
                        ']->(t)'
                    )
        return resulting_graph