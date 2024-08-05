import dspy
from tqdm import tqdm
from typing import Union
from hybridagi.embeddings.embeddings import Embeddings
from hybridagi.core.graph_program import GraphProgram
from hybridagi.core.datatypes import GraphProgramList

class GraphProgramEmbedder(dspy.Module):
    """
    A class used to embed graph programs using a pre-trained embedding model.

    Attributes:
        embeddings (Embeddings): The pre-trained embedding model to be used for embedding graph programs.
    """    
    def __init__(
            self,
            embeddings: Embeddings
        ):
        """
        Initialize the GraphProgramEmbedder.

        Parameters:
            embeddings (Embeddings): The pre-trained embedding model to be used for embedding graph programs.
        """
        self.embeddings = embeddings
    
    def forward(self, prog_or_progs: Union[GraphProgram, GraphProgramList]) -> GraphProgramList:
        """
        Embed graph programs using the pre-trained embedding model.

        Parameters:
            prog_or_progs (Union[Fact, FactList]): A single program or a list of programs to be embedded.

        Returns:
            GraphProgramList: A list of facts with their corresponding embeddings.

        Raises:
            ValueError: If the input is not a Fact or FactList.
        """
        if not isinstance(prog_or_progs, GraphProgram) and not isinstance(prog_or_progs, GraphProgramList):
            raise ValueError(f"{type(self).__name__} input must be a GraphProgram or GraphProgramList")
        if isinstance(prog_or_progs, GraphProgram):
            programs = GraphProgramList()
            programs.progs = [prog_or_progs]
        else:
            programs = prog_or_progs
        for prog in tqdm(programs.progs):
            prog.vector = self.embeddings.embed_text(prog.description)
        return programs