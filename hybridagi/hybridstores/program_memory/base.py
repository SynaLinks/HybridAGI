import numpy as np
from tqdm import tqdm
from typing import List
from hybridagikb import BaseHybridStore
from .prompt import PROGRAM_DESCRIPTION_PROMPT
from langchain.schema.embeddings import Embeddings
from langchain.chains.llm import LLMChain
from langchain.schema.language_model import BaseLanguageModel

class BaseProgramMemory(BaseHybridStore):

    def __init__(
            self,
            index_name: str,
            redis_url: str,
            embedding: Embeddings,
            embedding_dim: int,
            llm: BaseLanguageModel,
            verbose: bool = True):
        """The base program memory constructor"""
        super().__init__(
            index_name = index_name,
            redis_url = redis_url,
            embedding = embedding,
            embedding_dim = embedding_dim,
            graph_index = "program_memory",
            indexed_label = "Program",
            verbose = verbose)
        self.llm = llm
        self.embedding = embedding
        self.embedding_dim = embedding_dim
        self.playground = self.create_graph("testing_playground")

    def verify_programs(
            self,
            names: List[str],
            programs: List[str]):
        for idx, program in enumerate(programs):
            program_name = names[idx]
            try:
                self.playground.query(program)
            except Exception as err:
                raise RuntimeError(f"Error while loading '{program_name}': {err}"+\
                ". Please correct your program")
            result = self.playground.query(
                'MATCH (n:Control {name:"Start"}) RETURN n')
            if len(result.result_set) == 0:
                raise RuntimeError(f"Error while loading '{program_name}':"+\
                " No starting node detected, please "+\
                "make sure to start your program correctly")
            if len(result.result_set) > 1:
                raise RuntimeError(f"Error while loading '{program_name}':"+\
                    "Multiple entry point detected,"+
                    " please correct your programs.")

            result = self.playground.query(
                'MATCH (n:Control {name:"End"}) RETURN n')
            if len(result.result_set) == 0:
                raise RuntimeError(f"Error while loading '{program_name}':"+\
                " No ending node detected, please "+\
                "make sure to end your program correctly")
            if len(result.result_set) > 1:
                raise RuntimeError(f"Error while loading '{program_name}':"+\
                    "Multiple ending point detected,"+
                    " please correct your programs.")
                
            result = self.playground.query(
                'MATCH (p:Program) RETURN p'
            )
            if (result.result_set) > 0:
                for p in result.result_set[0]:
                    if not self.exists(program):
                        raise RuntimeError(
                            f"Error while loading '{program_name}': "+\
                            f"The sub-program '{p}' do not exist."+\
                            " Please correct your program")
            self.playground.delete()

    def add_programs(
            self,
            names: List[str],
            programs: List[str]):
        indexes = []
        dependencies = {}
        assert(len(programs) == len(names))
        if self.verbose:
            pbar = tqdm(total=len(programs))
        for idx, program in enumerate(programs):
            program_name = names[idx]
            graph_program = self.create_graph(program_name)
            try:
                graph_program.delete()
            except Exception:
                pass
            graph_program.query(program)
            chain = LLMChain(llm=self.llm, prompt=PROGRAM_DESCRIPTION_PROMPT)
            program_description = chain.predict(program=program)
            vector = np.array(
                self.embedding.embed_query(text=program_description),
                dtype=np.float32)
            self.set_content(program_name, program)
            params = {"program_name": program_name, "vector": list(vector)}
            self.query('MERGE (n:Program {name:"$program_name"'+
                       ', description:vector32f($vector)})',
                       params = params)
            result = graph_program.query('MATCH (n:Program) RETURN n')
            dependencies[program_name] = []
            if len(result.result_set) > 0:
                for node in result.result_set[0]:
                    dependencies[program_name].append(node.properties["program"])
            indexes.append(program_name)
            if self.verbose:
                pbar.update(1)
        if self.verbose:
            pbar.close()
        for name, dep in dependencies.items():
            for prog in dep:
                self.query(
                    'MERGE (:Program {name:"'+name+\
                    '"})-[:DEPENDS_ON]->(:Program {name:"'+prog+'"})')
        return indexes

