import dspy
from typing import Union
from hybridagi.embeddings.embeddings import Embeddings
from hybridagi.core.graph_program import GraphProgram, GraphProgramList

class GraphProgramEmbedder(dspy.Module):
    """
    A class used to embed facts using a pre-trained embedding model.

    Attributes:
        embeddings (Embeddings): The pre-trained embedding model to be used for embedding facts.
    """    
    def __init__(
            self,
            embeddings: Embeddings
        ):
        """
        Initialize the FactEmbedder.

        Parameters:
            embeddings (Embeddings): The pre-trained embedding model to be used for embedding facts.
        """
        self.embeddings = embeddings
    
    def forward(self, prog_or_progs: Union[GraphProgram, GraphProgramList]) -> GraphProgramList:
        """
        Embed facts using the pre-trained embedding model.

        Parameters:
            prog_or_progs (Union[Fact, FactList]): A single program or a list of programs to be embedded.

        Returns:
            FactList: A list of facts with their corresponding embeddings.

        Raises:
            ValueError: If the input is not a Fact or FactList.
        """
        if not isinstance(prog_or_progs, GraphProgram) and not isinstance(prog_or_progs, GraphProgramList):
            raise ValueError(f"{type(self).__name__} input must be a Fact or FactList")
        if isinstance(prog_or_progs, GraphProgram):
            programs = GraphProgramList()
            programs.progs = [prog_or_progs]
        else:
            programs = prog_or_progs
        for prog in programs.progs:
            prog.vector = self.embeddings.embed_text(prog.description)
        return programs