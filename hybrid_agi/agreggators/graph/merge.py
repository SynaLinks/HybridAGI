"""The merge graph aggregator. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

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