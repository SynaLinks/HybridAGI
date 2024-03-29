import dspy
from hybridagi import FakeEmbeddings
from hybridagi import FileSystem
from hybridagi.tools import DocumentSearchTool
from dspy.utils.dummies import DummyLM

def test_document_search():
    emb = FakeEmbeddings(dim=250)

    memory = FileSystem(
        index_name = "test",
        embeddings = emb,
        wipe_on_start = True,
    )

    text = "This is a test text"
    text_name = "test_text"

    memory.add_texts(
        texts = [text],
        ids = [text_name]
    )

    answers = ["test prediction"]

    dspy.settings.configure(lm=DummyLM(answers=answers))

    tool = DocumentSearchTool(
        index_name = "test",
        embeddings = emb,
    )

    prediction = tool(
        trace = "Nothing done yet",
        objective = "test objective",
        purpose = "test purpose",
        prompt = "test prompt",
        disable_inference = False,
        stop = None,
    )

    assert prediction.query == "test prediction"
    assert len(prediction.passages) == 1

def test_document_search_without_inference():
    emb = FakeEmbeddings(dim=250)

    memory = FileSystem(
        index_name = "test",
        embeddings = emb,
        wipe_on_start = True,
    )

    text = "This is a test text"
    text_name = "test_text"

    memory.add_texts(
        texts = [text],
        ids = [text_name]
    )

    answers = ["test prediction"]
    
    dspy.settings.configure(lm=DummyLM(answers=answers))

    tool = DocumentSearchTool(
        index_name = "test",
        embeddings = emb,
    )

    prediction = tool(
        trace = "Nothing done yet",
        objective = "test objective",
        purpose = "test purpose",
        prompt = "test prompt",
        disable_inference = True,
        stop = None,
    )

    assert prediction.query == "test prompt"
    assert len(prediction.passages) == 1