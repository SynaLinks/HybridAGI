from hybridagi import HybridStore
from hybridagi import FakeEmbeddings

def test_add_texts():
    emb = FakeEmbeddings(dim=250)
    rm = HybridStore(
        index_name="test",
        graph_index="store",
        embeddings=emb,
        wipe_on_start=True,
    )
    text = "This the a test text"
    text_name = "test_text"

    rm.add_texts(
        texts = [text],
        ids = [text_name]
    )
    assert rm.get_content("test_text") == text

def test_add_two_texts():
    emb = FakeEmbeddings(dim=250)
    rm = HybridStore(
        index_name="test",
        graph_index="store",
        embeddings=emb,
        wipe_on_start=True,
    )
    text1 = "This the a test text 1"
    text_name1 = "test_text_1"
    text2 = "This the a test text 2"
    text_name2 = "test_text_2"

    rm.add_texts(
        texts = [text1, text2],
        ids = [text_name1, text_name2]
    )
    assert rm.get_content(text_name1) == text1
    assert rm.get_content(text_name2) == text2

def test_add_texts_non_ascii():
    emb = FakeEmbeddings(dim=250)
    rm = HybridStore(
        index_name="test",
        graph_index="store",
        embeddings=emb,
        wipe_on_start=True,
    )
    text = "This the a tes°t text"
    text_name = "test_text"

    rm.add_texts(
        texts = [text],
        ids = [text_name]
    )
    assert rm.get_content("test_text") == text

def test_remove_texts():
    emb = FakeEmbeddings(dim=250)
    rm = HybridStore(
        index_name="test",
        graph_index="store",
        embeddings=emb,
        wipe_on_start=True,
    )
    text = "This the a test text"
    text_name = "test_text"

    rm.add_texts(
        texts = [text],
        ids = [text_name]
    )
    assert rm.exists(text_name)
    rm.remove_texts([text_name])
    assert not rm.exists(text_name)

def test_get_graph():
    emb = FakeEmbeddings(dim=250)
    rm = HybridStore(
        index_name="test",
        graph_index="store",
        embeddings=emb,
        wipe_on_start=True,
    )
    g = rm.get_graph("test_graph")
    assert g.name == "test:graph:test_graph"

def test_graph_query():
    emb = FakeEmbeddings(dim=250)
    rm = HybridStore(
        index_name="test",
        graph_index="store",
        embeddings=emb,
        wipe_on_start=True,
    )
    g = rm.get_graph("test_graph")
    g.query("RETURN 1")

def test_set_content():
    emb = FakeEmbeddings(dim=250)
    rm = HybridStore(
        index_name="test",
        graph_index="store",
        embeddings=emb,
        wipe_on_start=True,
    )
    assert rm.set_content("test_index", "This is a test text")

def test_set_and_retreive_content():
    emb = FakeEmbeddings(dim=250)
    rm = HybridStore(
        index_name="test",
        graph_index="store",
        embeddings=emb,
        wipe_on_start=True,
    )
    assert rm.set_content("test_index", "This is a test text")
    assert rm.get_content("test_index") == "This is a test text"

def test_set_content_description():
    emb = FakeEmbeddings(dim=250)
    rm = HybridStore(
        index_name="test",
        graph_index="store",
        embeddings=emb,
        wipe_on_start=True,
    )
    assert not rm.set_content_description("test_index", "This is a description")
    assert rm.set_content("test_index", "This is a test text")
    assert rm.set_content_description("test_index", "This is a description")

def test_set_and_retreive_content_description():
    emb = FakeEmbeddings(dim=250)
    rm = HybridStore(
        index_name="test",
        graph_index="store",
        embeddings=emb,
        wipe_on_start=True,
    )
    assert not rm.set_content_description("test_index", "This is a description")
    assert rm.set_content("test_index", "This is a test text")
    assert rm.set_content_description("test_index", "This is a description")

def test_set_content_metadata():
    emb = FakeEmbeddings(dim=250)
    rm = HybridStore(
        index_name="test",
        graph_index="store",
        embeddings=emb,
        wipe_on_start=True,
    )
    metadata = {"metadata": "this is a content metadata"}
    assert not rm.set_content_metadata("test_index", metadata) 
    assert rm.set_content("test_index", "This is a test text")
    assert rm.set_content_metadata("test_index", metadata)

def test_set_and_retreive_content_metadata():
    emb = FakeEmbeddings(dim=250)
    rm = HybridStore(
        index_name="test",
        graph_index="store",
        embeddings=emb,
        wipe_on_start=True,
    )
    metadata = {"metadata": "this is a content metadata"}
    assert rm.set_content("test_index", "This is a test text")
    assert rm.set_content_metadata("test_index", metadata)
    assert rm.get_content_metadata("test_index") == metadata

def test_delete_content():
    emb = FakeEmbeddings(dim=250)
    rm = HybridStore(
        index_name="test",
        graph_index="store",
        embeddings=emb,
        wipe_on_start=True,
    )
    assert not rm.delete_content("test_index")
    assert rm.set_content("test_index", "This is a test text")
    assert rm.delete_content("test_index")
    assert not rm.exists("test_index")