import dspy
import hybridagi.core.graph_program as gp
from hybridagi.core.pipeline import Pipeline
from hybridagi.core.datatypes import Query, Fact, Entity, Relationship, FactList
from hybridagi.memory.integration.falkordb import FalkorDBFactMemory
from dspy.utils.dummies import DummyLM
from hybridagi.embeddings import SentenceTransformerEmbeddings
from hybridagi.modules.deduplicators import EntityDeduplicator
from hybridagi.modules.embedders import EntityEmbedder, FactEmbedder

from hybridagi.modules.retrievers.integration.falkordb import FalkorDBEntityRetriever

def test_falkordb_entity_retriever():
    input_data = \
    [
        {
            "Title": "The Shawshank Redemption",
            "Year Produced": 1994,
            "Actors": ["Tim Robbins", "Morgan Freeman"],
            "Directors": ["Frank Darabont"],
            "Genres": ["Drama", "Crime"],
            "Ratings": 9.3
        },
        {
            "Title": "The Godfather",
            "Year Produced": 1972,
            "Actors": ["Marlon Brando", "Al Pacino", "Diane Keaton"],
            "Directors": ["Francis Ford Coppola"],
            "Genres": ["Crime", "Drama"],
            "Ratings": 9.2
        },
        {
            "Title": "The Godfather: Part II",
            "Year Produced": 1974,
            "Actors": ["Al Pacino", "Robert De Niro", "Diane Keaton"],
            "Directors": ["Francis Ford Coppola"],
            "Genres": ["Crime", "Drama"],
            "Ratings": 9.0
        },
    ]
    
    input_facts = FactList()

    for data in input_data:
        movie = Entity(name=data["Title"], label="Movie")
        year = Entity(name=str(data["Year Produced"]), label="Year")
        input_facts.facts.append(Fact(subj=movie, rel=Relationship(name="PRODUCED_IN"), obj=year))
        for actor in data["Actors"]:
            actor_entity = Entity(name=actor, label="Actor")
            input_facts.facts.append(Fact(subj=actor_entity, rel=Relationship(name="PLAYED_IN"), obj=movie))
        for director in data["Directors"]:
            director_entity = Entity(name=actor, label="Director")
            input_facts.facts.append(Fact(subj=movie, rel=Relationship(name="DIRECTED_BY"), obj=director_entity))
        for genre in data["Genres"]:
            genre_entity = Entity(name=genre, label="Genre")
            input_facts.facts.append(Fact(subj=movie, rel=Relationship(name="HAS_GENRE"), obj=genre_entity))
        rating = Entity(name=str(data["Ratings"]), label="Ratings")
        input_facts.facts.append(Fact(subj=movie, rel=Relationship(name="HAS_RATING_OF"), obj=rating))
        
    pipeline = Pipeline()

    embeddings = SentenceTransformerEmbeddings(
        model_name_or_path = "all-MiniLM-L6-v2",
        dim = 384, # The dimention of the embeddings vector (also called dense vector)
        normalize_embeddings=True,
    )

    pipeline.add("deduplicate_entities", EntityDeduplicator(method="exact"))
    pipeline.add("embed_entities", EntityEmbedder(embeddings=embeddings))
    pipeline.add("embed_facts", FactEmbedder(embeddings=embeddings))

    output_facts = pipeline(input_facts)
    
    fact_memory = FalkorDBFactMemory(index_name="test_entity_retriever", wipe_on_start=True)
    
    fact_memory.update(output_facts)
    
    entity_retriever = FalkorDBEntityRetriever(
        fact_memory = fact_memory,
        embeddings = embeddings,
        max_distance = 1.0,
        distance = "cosine",
        k = 5,
    )
    result = entity_retriever(Query(query="godfather movie"))
    assert len(result.entities) > 0