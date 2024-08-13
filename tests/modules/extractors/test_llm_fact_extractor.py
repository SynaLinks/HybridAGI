import dspy
from hybridagi.modules.extractors.llm_fact_extractor import LLMFactExtractor
from hybridagi.core.datatypes import Document, DocumentList, FactList

from dspy.utils.dummies import DummyLM

def test_llm_fact_extractor_with_document():
    answers = ['(:Person {name:"Bob"})-[:KNOWS]->(:Person {name:"Alice"})']
    dspy.settings.configure(lm=DummyLM(answers=answers))

    extractor = LLMFactExtractor()

    doc = Document(text="Bob knows Alice.")
    result = extractor.forward(doc)

    assert isinstance(result, FactList)
    assert len(result.facts) == 1
    assert result.facts[0].subj.label == "Person"
    assert result.facts[0].subj.name == "Bob"
    assert result.facts[0].rel.name == "KNOWS"
    assert result.facts[0].obj.label == "Person"
    assert result.facts[0].obj.name == "Alice"

def test_llm_fact_extractor_with_document_list():
    answers = [
        '(:Person {name:"John"})-[:LIKES]->(:Fruit {name:"apples"})',
        '(:Person {name:"Mary"})-[:HATES]->(:Fruit {name:"bananas"})'
    ]
    dspy.settings.configure(lm=DummyLM(answers=answers))
    
    extractor = LLMFactExtractor()
    
    docs = DocumentList(docs=[
        Document(text="John likes apples."),
        Document(text="Mary hates bananas.")
    ])
    result = extractor.forward(docs)
    
    assert isinstance(result, FactList)
    assert len(result.facts) == 2
    assert result.facts[0].subj.name == "John"
    assert result.facts[0].rel.name == "LIKES"
    assert result.facts[0].obj.name == "apples"
    assert result.facts[1].subj.name == "Mary"
    assert result.facts[1].rel.name == "HATES"
    assert result.facts[1].obj.name == "bananas"

def test_llm_fact_extractor_with_invalid_input():
    extractor = LLMFactExtractor()
    
    try:
        extractor.forward("Invalid input")
    except ValueError as e:
        assert str(e) == "LLMFactExtractor input must be a Document or DocumentList"
    else:
        assert False, "ValueError was not raised"
