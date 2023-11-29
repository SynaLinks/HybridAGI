
from typing import List, Optional, Callable, Any
from hybridagikb import BaseHybridStore
from langchain.schema.embeddings import Embeddings

def _default_norm(value):
    return value

class BaseProgramMemory(BaseHybridStore):
    def __init__(
            self,
            index_name: str,
            redis_url: str,
            embedding: Embeddings,
            embedding_dim: int,
            normalize: Optional[Callable[[Any], Any]] = _default_norm,
            verbose: bool = True):
        """The base program memory constructor"""
        super().__init__(
            index_name = index_name,
            redis_url = redis_url,
            embedding = embedding,
            embedding_dim = embedding_dim,
            graph_index = "program_memory",
            indexed_label = "Content",
            normalize = normalize,
            verbose = verbose)
        self.embedding = embedding
        self.embedding_dim = embedding_dim
        self.playground = self.create_graph("testing_playground")

    def verify_programs(
            self,
            names: List[str],
            programs: List[str]):
        for idx, program in enumerate(programs):
            program_name = names[idx]
            if self.depends_on("main", program_name):
                raise RuntimeError(
                    f"Error while loading '{program_name}': "+\
                    "Trying to modify a protected program")
            try:
                self.playground.query(program)
            except Exception as err:
                raise RuntimeError(
                    f"Error while loading '{program_name}': {err}. "+\
                    "Please correct your program")
            result = self.playground.query(
                'MATCH (n:Control {name:"Start"}) RETURN n')
            if len(result) == 0:
                raise RuntimeError(
                    f"Error while loading '{program_name}': "+\
                    "No starting node detected, please "+\
                    "make sure to start your program correctly")
            if len(result) > 1:
                raise RuntimeError(
                    f"Error while loading '{program_name}': "+\
                    "Multiple entry point detected, "+
                    "please correct your programs.")

            result = self.playground.query(
                'MATCH (n:Control {name:"End"}) RETURN n')
            if len(result) == 0:
                raise RuntimeError(
                    f"Error while loading '{program_name}': "+\
                    "No ending node detected, please "+\
                    "make sure to end your program correctly")
            if len(result) > 1:
                raise RuntimeError(
                    f"Error while loading '{program_name}': "+\
                    "Multiple ending point detected, "+
                    "please correct your programs.")
                
            result = self.playground.query(
                'MATCH (p:Program) RETURN p.program AS program')
            for record in result:
                subprogram = record[0]
                if self.depends_on("main", subprogram):
                    raise RuntimeError(
                        f"Error while loading '{program_name}': "+\
                        "Trying to call a protected program")
                if not self.exists(subprogram):
                    raise RuntimeError(
                        f"Error while loading '{program_name}': "+\
                        f"The sub-program '{subprogram}' do not exist. "+\
                        "Please correct your program")
            self.playground.delete()

    def add_programs(
            self,
            names: List[str],
            programs: List[str]):
        """Method to add programs"""
        indexes = []
        dependencies = {}
        descriptions = []
        assert(len(programs) == len(names))
        for idx, program in enumerate(programs):
            program_name = names[idx]
            graph_program = self.create_graph(program_name)
            description = ""
            for line in program.split():
                if line.startswith("// @desc:"):
                    description += line.replace("// @desc:", "")
                elif line.startswith("//"):
                    pass
                else:
                    break
            if description:
                descriptions.append(description)
            else:
                descriptions.append(program)
            
            try:
                graph_program.delete()
            except Exception:
                pass
            try:
                graph_program.query(program)
            except Exception as e:
                raise RuntimeError(f"{program_name}: {e}")
            self.query('MERGE (n:Program {name:"'+program_name+'"})')
            result = graph_program.query('MATCH (n:Program) RETURN n.program AS program')
            if len(result) > 0:
                dependencies[program_name] = []
                for record in result:
                    dependencies[program_name].append(record[0])
        for name, dep in dependencies.items():
            for prog_dep in dep:
                self.query(
                    'MATCH (p:Program {name:"'+name+'"}), '+
                    '(d:Program {name:"'+prog_dep+'"}) '+
                    'MERGE (p)-[:DEPENDS_ON]->(d)')

        indexes = self.add_texts(
            programs,
            ids = names,
            descriptions = descriptions)
        for idx in indexes:
            self.query('MATCH (p:Program {name:"'+idx+'"}), '+
                '(c:Content {name:"'+idx+'"}) '+
                'MERGE (p)-[:CONTAINS]->(c)')
        return indexes

    def depends_on(self, source: str, target: str):
        """Method to check if a program depend on another"""
        result = self.query('MATCH (n:Program {name:"'+source+
            '"})-[r:DEPENDS_ON*]->(m:Program {name:"'+target+
            '"}) RETURN r')
        if len(result) > 0:
            return True
        return False
