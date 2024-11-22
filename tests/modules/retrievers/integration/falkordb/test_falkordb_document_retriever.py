import dspy
import hybridagi.core.graph_program as gp
from hybridagi.core.pipeline import Pipeline
from hybridagi.core.datatypes import Query, Document, DocumentList
from hybridagi.memory.integration.falkordb import FalkorDBDocumentMemory
from dspy.utils.dummies import DummyLM
from hybridagi.embeddings import SentenceTransformerEmbeddings
from hybridagi.modules.deduplicators import EntityDeduplicator
from hybridagi.modules.splitters import DocumentSentenceSplitter
from hybridagi.modules.embedders import DocumentEmbedder

from hybridagi.modules.retrievers.integration.falkordb import FalkorDBDocumentRetriever

def test_document_retriever():
    input_data = [
        "In a small town nestled between rolling hills, there lived a young girl named Lily. She was known for her vivid imagination and her dream to become a writer. One day, she found an old typewriter in her grandmother's attic. With each clack of the keys, Lily's stories came to life, filling the pages with adventures and dreams. Her first book, a tale of a brave little mouse, became a local sensation, inspiring others to chase their dreams.",
        "The Great Wall of China is one of the most impressive architectural feats in history. Stretching over 13,000 miles, it was built over several centuries to protect the Chinese states and empires from raids and invasions. The wall includes watchtowers, troop barracks, garrison stations, and signaling capabilities through the means of smoke or fire.",
        "Photosynthesis is the process by which green plants, algae, and some bacteria convert light energy, typically from the sun, into chemical energy stored in glucose. This process occurs in the chloroplasts of plant cells and involves the absorption of carbon dioxide and water, releasing oxygen as a byproduct. Photosynthesis is crucial for life on Earth as it provides the primary source of energy for nearly all organisms.",
    ]
    input_docs = DocumentList()
    for data in input_data:
        input_docs.docs.append(Document(text=data))
    
    pipeline = Pipeline()

    embeddings = SentenceTransformerEmbeddings(
        model_name_or_path = "all-MiniLM-L6-v2",
        dim = 384, # The dimention of the embeddings vector (also called dense vector)
        normalize_embeddings=True,
    )
    
    pipeline = Pipeline()

    pipeline.add("chunk_documents", DocumentSentenceSplitter(
        method = "word",
        chunk_size = 100,
        chunk_overlap = 0,
    ))
    
    pipeline.add("embed_chunks", DocumentEmbedder(embeddings=embeddings))
    
    output_docs = pipeline(input_docs)
    
    document_memory = FalkorDBDocumentMemory(
        index_name="test_document_retriever",
        wipe_on_start=True,
    )
    
    document_memory.update(output_docs)
    
    document_retriever = FalkorDBDocumentRetriever(
        document_memory = document_memory,
        embeddings = embeddings,
        max_distance = 1.0,
        distance = "cosine",
        k = 5,
    )
    
    result = document_retriever(Query(query="What is photosynthesis"))
    assert len(result.docs) > 0