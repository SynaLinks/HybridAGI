from hybridagi import FactMemory
from hybridagi import FakeEmbeddings
from hybridagi.utility.knowledge_parsers.text import TextKnowledgeParser

def test_text_knowledge_parser():
    emb = FakeEmbeddings(dim=250)
    
    memory = FactMemory(
        index_name = "test",
        embeddings = emb,
        wipe_on_start = True,
    )

    parser = TextKnowledgeParser(memory)

    # Using test phrase from https://medium.com/@erkajalkumari/knowledge-graphs-the-game-changer-in-ai-and-data-science-d56580b15aaa 
    text = "London is the capital of England. Westminster is located in London."

    parser.parse(filename="example.txt", content=text)
    assert len(memory.get_triplets("London")) == 1
    
    rel_map = memory.get_rel_map(["Westminster"])
    expected_result = {
        'Westminster': [
            ['LOCATED_IN', 'London'],
            ['LOCATED_IN', 'London', 'IS', 'England']
        ]
    }

    # Sort the inner lists before comparing
    assert sorted((k, sorted(v)) for k, v in rel_map.items()) == sorted((k, sorted(v)) for k, v in expected_result.items())

