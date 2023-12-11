from langchain.schema.embeddings import Embeddings
from typing import List

class FakeListEmbeddings(Embeddings):
    responses: List[List[float]]
    i:int = 0

    def __init__(self, responses):
        super().__init__()
        self.responses = responses
        self.i = 0

    def embed_query(self, query):
        result = self.responses[self.i]
        self.i += 1
        return result

    def embed_documents(self, query: List[str]):
        return [self.embed_query(i) for i in query]