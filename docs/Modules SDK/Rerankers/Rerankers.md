# Rerankers

Rerankers are an optional component to enhance the results of a RAG pipeline, when using an embedding vector to retrieve information from memory, the information retrieved might be noisy (meaning we retrieve things that are not needed to answer). To reduce the amount of non-desired information in the context, it is usually a good thing to add a reranker (or a sequence of rerankers).

In HybridAGI, to add a rerankers to your pipeline you can specify in the retriever tools the pipeline to use. A reranker always work with the Query associated with a datatype, like `QueryWithDocuments`, `QueryWithActions`, `QueryWithEntities`, `QueryWithFacts`, `QueryWithGraphPrograms`.

Here is the definition of each type of reranker supported at the moment.

## Document Reranker

```python
class DocumentReranker(dspy.Module):
    
    @abstractmethod
    def forward(self, query: QueryWithDocuments) -> QueryWithDocuments:
        raise NotImplementedError(
            f"DocumentReranker {type(self).__name__} is missing the required 'forward' method."
        )
```

## Action Reranker

```python
class ActionReranker(dspy.Module):
    
    @abstractmethod
    def forward(self, query: QueryWithSteps) -> QueryWithSteps:
        raise NotImplementedError(
            f"ActionReranker {type(self).__name__} is missing the required 'forward' method."
        )
```

## Fact Reranker

```python
class FactReranker(dspy.Module):
    
    @abstractmethod
    def forward(self, query: QueryWithFacts) -> QueryWithFacts:
        raise NotImplementedError(
            f"FactReranker {type(self).__name__} is missing the required 'forward' method."
        )
```

## Entity Reranker

```python
class EntityReranker(dspy.Module):
    
    @abstractmethod
    def forward(self, query: QueryWithEntities) -> QueryWithEntities:
        raise NotImplementedError(
            f"EntityReranker {type(self).__name__} is missing the required 'forward' method."
        )
```

## Graph Program Reranker

```python
class GraphProgramReranker(dspy.Module):
    
    @abstractmethod
    def forward(self, query: QueryWithGraphPrograms) -> QueryWithGraphPrograms:
        raise NotImplementedError(
            f"GraphProgramReranker {type(self).__name__} is missing the required 'forward' method."
        )
```