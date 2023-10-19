import numpy as np
from tqdm import tqdm
from typing import List, Optional, Callable, Any
from hybridagikb import BaseHybridStore
from .prompt import PROGRAM_DESCRIPTION_PROMPT
from langchain.schema.embeddings import Embeddings
from langchain.chains.llm import LLMChain
from langchain.schema.language_model import BaseLanguageModel

def _default_norm(value):
    return value

class BaseProgramMemory(BaseHybridStore):

    def __init__(
            self,
            index_name: str,
            redis_url: str,
            embedding: Embeddings,
            embedding_dim: int,
            llm: BaseLanguageModel,
            normalize: Optional[Callable[[Any], Any]] = _default_norm,
            verbose: bool = True):
        """The base program memory constructor"""
        super().__init__(
            index_name = index_name,
            redis_url = redis_url,
            embedding = embedding,
            embedding_dim = embedding_dim,
            graph_index = "program_memory",
            indexed_label = "Program",
            normalize = normalize,
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
            programs: List[str],
            descriptions: List[str] = [],
            use_hardcoded_description = True):
        """Method to add programs"""
        indexes = []
        dependencies = {}
        assert(len(programs) == len(names))
        if descriptions:
            assert(len(programs) == len(descriptions))
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
            program_description = "" if not descriptions else descriptions[idx]
            if use_hardcoded_description:
                lines = program.split("\n")
                for ln in lines:
                    if ln.startswith("// @desc:"):
                        program_description += ln.replace("// @desc:", "").strip()
            if not program_description:
                chain = LLMChain(llm=self.llm, prompt=PROGRAM_DESCRIPTION_PROMPT)
                program_description = chain.predict(program=program)
            vector = np.array(
                self.embedding.embed_query(text=program_description),
                dtype=np.float32)
            params = {"program_name": program_name, "vector": list(vector)}
            self.query('MERGE (n:Program {name:"$program_name"'+
                    ', description:vector32f($vector)})', params = params)
            params = {"program_name": program_name}
            self.query('MATCH (n:Program {name:"$program_name"})'+
                '-[r:DEPENDS_ON]->(m) DELETE r')
            self.set_content(program_name, program)
            result = graph_program.query('MATCH (n:Program) RETURN n.name AS name')
            dependencies[program_name] = []
            for record in result.result_set:
                dependencies[program_name].append(record[0])
            indexes.append(program_name)
            if self.verbose:
                pbar.update(1)
        if self.verbose:
            pbar.close()
        for name, dep in dependencies.items():
            for prog_dep in dep:
                self.query(
                    'MATCH (n:Program {name:"'+name+'"}), '+
                    '(m:Program {name:"'+prog_dep+'"}) '+
                    'MERGE (n)-[:DEPENDS_ON]->(m)')
        return indexes

