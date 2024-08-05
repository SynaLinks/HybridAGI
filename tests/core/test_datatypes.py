import hybridagi.core.datatypes as dt

def test_document():
    doc = dt.Document(text="This is a test text")
    assert doc.text == "This is a test text"
    assert doc.id != ""
    assert doc.metadata == {}
    assert doc.vector == None

def test_document_with_id():
    doc = dt.Document(text="This is a test text", id="Test id")
    assert doc.id == "Test id"

def test_document_with_different_id():
    doc_1 = dt.Document(text="Doc 1")
    doc_2 = dt.Document(text="Doc 2")
    assert doc_1.id != doc_2.id

def test_document_with_metadata():
    doc = dt.Document(text="This is test doc", metadata={"metadata": "This is some metadata"})
    assert doc.metadata["metadata"] == "This is some metadata"

def test_document_with_parent_id():
    parent_doc = dt.Document(text="This is the parent doc")
    child_doc = dt.Document(text="This is the child doc", parent_id=parent_doc.id)
    assert parent_doc.id == child_doc.parent_id
    assert parent_doc.id != child_doc.id

def test_document_with_vector():
    vec = [0.0, 0.1, 0.2, 0.3]
    doc = dt.Document(text="This is a test text", vector=vec)
    assert doc.vector == vec

def test_document_list():
    docs_list = dt.DocumentList()
    docs_list.docs.append(dt.Document(text="This is a test text"))
    assert docs_list.docs[0].text == "This is a test text"

def test_entity():
    entity = dt.Entity(label="Person", name="John Doe")
    assert entity.id != ""
    assert entity.metadata == {}
    assert entity.vector == None

def test_entity_with_metadata():
    entity = dt.Entity(label="Person", name="John Doe", metadata={"birth_year": 1991})
    assert entity.metadata["birth_year"] == 1991

def test_entity_with_vector():
    vec = [0.0, 0.1, 0.2, 0.3]
    entity = dt.Entity(label="Person", name="John Doe", vector=vec)
    assert entity.vector == vec

def test_entity_list():
    entity_list = dt.EntityList()
    entity_list.entities.append(dt.Entity(label="Person", name="John Doe"))
    assert entity_list.entities[0].name == "John Doe"

def test_fact():
    bob = dt.Entity(label="Person", name="Bob")
    alice = dt.Entity(label="Person", name="Alice")
    relation = dt.Relationship(name="Knows")
    fact = dt.Fact(subj=bob, rel=relation, obj=alice)
    assert fact.subj.id == bob.id
    assert fact.obj.id == alice.id
    assert fact.rel.name == "Knows"

def test_fact_with_metadata():
    bob = dt.Entity(label="Person", name="Bob")
    alice = dt.Entity(label="Person", name="Alice")
    relation = dt.Relationship(name="Knows")
    fact = dt.Fact(subj=bob, rel=relation, obj=alice, metadata={"from": "college"})
    assert fact.metadata["from"] == "college"

def test_fact_with_vector():
    vec = [0.0, 0.1, 0.2, 0.3]
    bob = dt.Entity(label="Person", name="Bob")
    alice = dt.Entity(label="Person", name="Alice")
    relation = dt.Relationship(name="Knows")
    fact = dt.Fact(subj=bob, rel=relation, obj=alice, vector=vec)
    assert fact.vector == vec

def test_user_profile():
    user = dt.UserProfile(name="Alice", profile="A famous prompt engineer")

def test_user_profile_empty():
    user = dt.UserProfile()
    assert user.name == "Unknow"
    assert user.profile == "An average user"

def test_user_profile_with_metadata():
    user = dt.UserProfile(metadata={"from": "LinkedIn"})
    assert user.metadata["from"] == "LinkedIn"

def test_user_profile_with_vector():
    vec = [0.0, 0.1, 0.2, 0.3]
    user = dt.UserProfile(vector=vec)
    assert user.vector == vec

def test_message():
    msg = dt.Message(role=dt.Role.AI, content="Hello world")
    assert msg.role == "AI"
    assert msg.content == "Hello world"

def test_chat_history():
    chat = dt.ChatHistory()
    chat.msgs.append(dt.Message(role=dt.Role.AI, content="Hello world"))
    assert chat.msgs[0].content == "Hello world"

def test_interaction_session_empty():
    session = dt.InteractionSession()
    assert session.user.name == "Unknow"
    assert session.user.profile == "An average user"
    assert session.chat.msgs == []

def test_interaction_session_with_user():
    session = dt.InteractionSession(user=dt.UserProfile(name="Alice", profile="A famous prompt engineer"))
    assert session.user.name == "Alice"
    assert session.user.profile == "A famous prompt engineer"

def test_interaction_session_with_chat():
    session = dt.InteractionSession()
    session.chat.msgs.append(dt.Message(role=dt.Role.AI, content="Hello, I'm an AI assistant what can I do to help you?"))
    session.chat.msgs.append(dt.Message(role=dt.Role.User, content="Can you tell me what is the capital of France?"))
    assert session.chat.msgs[0].content == "Hello, I'm an AI assistant what can I do to help you?"
    assert session.chat.msgs[1].content == "Can you tell me what is the capital of France?"
