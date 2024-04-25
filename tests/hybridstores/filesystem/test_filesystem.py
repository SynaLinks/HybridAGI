from hybridagi import FakeEmbeddings
from hybridagi import FileSystem

def test_create_folder():
    emb = FakeEmbeddings(dim=250)
    memory = FileSystem(
        index_name = "test",
        embeddings = emb,
        wipe_on_start = True,
    )

    memory.create_folder("/test")
    assert memory.is_folder("/test")

def test_create_document():
    emb = FakeEmbeddings(dim=250)
    memory = FileSystem(
        index_name = "test",
        embeddings = emb,
        wipe_on_start = True,
    )

    memory.create_document("/test.txt")
    assert memory.is_file("/test.txt")

def test_add_one_text():
    emb = FakeEmbeddings(dim=250)
    memory = FileSystem(
        index_name = "test",
        embeddings = emb,
        wipe_on_start = True,
    )

    text = \
"""Lorem ipsum dolor sit amet, consectetur adipiscing elit.
Integer molestie pellentesque velit, nec lobortis elit. 
Curabitur rhoncus vehicula euismod. Donec suscipit justo 
quis ante congue, sed dictum lorem hendrerit. Curabitur 
ultricies erat felis, vitae rutrum arcu placerat vel.
Nulla dapibus dictum arcu, nec varius lacus tempor non.
Maecenas aliquet porta dui quis aliquam. Proin dictum orci
auctor orci vulputate, commodo tristique neque posuere.
Aliquam in eros eu arcu fermentum dignissim nec vehicula diam."""

    filename = "/lorem_ipsum.txt"

    memory.add_texts(
        [text],
        [filename],
    )
    assert memory.is_file(filename)
    assert memory.get_document(filename) == text

def test_add_one_text_with_metadata():
    emb = FakeEmbeddings(dim=250)
    memory = FileSystem(
        index_name = "test",
        embeddings = emb,
        wipe_on_start = True,
    )

    text = \
"""Lorem ipsum dolor sit amet, consectetur adipiscing elit.
Integer molestie pellentesque velit, nec lobortis elit. 
Curabitur rhoncus vehicula euismod. Donec suscipit justo 
quis ante congue, sed dictum lorem hendrerit. Curabitur 
ultricies erat felis, vitae rutrum arcu placerat vel.
Nulla dapibus dictum arcu, nec varius lacus tempor non.
Maecenas aliquet porta dui quis aliquam. Proin dictum orci
auctor orci vulputate, commodo tristique neque posuere.
Aliquam in eros eu arcu fermentum dignissim nec vehicula diam."""

    filename = "/lorem_ipsum.txt"

    metadata = {"filename": filename}

    memory.add_texts(
        texts = [text],
        ids = [filename],
        metadatas = [metadata],
    )
    assert memory.is_file(filename)
    assert memory.get_document(filename) == text

def test_add_two_texts():
    emb = FakeEmbeddings(dim=250)
    memory = FileSystem(
        index_name = "test",
        embeddings = emb,
        wipe_on_start = True,
    )

    text1 = \
"""Lorem ipsum dolor sit amet, consectetur adipiscing elit.
Integer molestie pellentesque velit, nec lobortis elit. 
Curabitur rhoncus vehicula euismod. Donec suscipit justo 
quis ante congue, sed dictum lorem hendrerit. Curabitur 
ultricies erat felis, vitae rutrum arcu placerat vel.
Nulla dapibus dictum arcu, nec varius lacus tempor non.
Maecenas aliquet porta dui quis aliquam. Proin dictum orci
auctor orci vulputate, commodo tristique neque posuere.
Aliquam in eros eu arcu fermentum dignissim nec vehicula diam."""

    text2 = \
"""Cras suscipit quis lacus eu vulputate. Donec commodo volutpat tellus, 
sed finibus enim aliquam in. Suspendisse id felis dignissim, 
pharetra turpis in, convallis velit. Morbi magna felis, porttitor 
vel volutpat eget, condimentum vitae est. Cras lacus nunc, sagittis
vel nisi quis, tincidunt aliquam elit. Vivamus sagittis suscipit sem,
eget pretium nibh. Pellentesque rhoncus velit ut nisi egestas, nec 
iaculis elit fermentum. Etiam tempus ante lacinia, ornare ante id,
bibendum arcu. Mauris purus dui, placerat blandit scelerisque in, 
varius vitae enim. Nullam eu leo a urna tincidunt interdum vitae sed felis. 
In id nibh in quam sollicitudin egestas non sed est.

Sed interdum, nulla ut tempor lacinia, magna sem accumsan turpis,
sit amet hendrerit purus odio pretium turpis.
Curabitur convallis tempor consequat.
Proin dictum imperdiet eros nec vehicula."""

    filename1 = "/lorem_ipsum.txt"
    filename2 = "/lorem_ipsum2.txt"

    memory.add_texts(
        [text1, text2],
        [filename1, filename2],
    )

    assert memory.is_file(filename1)
    assert memory.get_document(filename1) == text1
    assert memory.is_file(filename2)
    assert memory.get_document(filename2) == text2

def test_append_one_text():
    emb = FakeEmbeddings(dim=250)
    memory = FileSystem(
        index_name = "test",
        embeddings = emb,
        wipe_on_start = True,
    )

    text1 = \
"""Lorem ipsum dolor sit amet, consectetur adipiscing elit.
Integer molestie pellentesque velit, nec lobortis elit. 
Curabitur rhoncus vehicula euismod. Donec suscipit justo 
quis ante congue, sed dictum lorem hendrerit. Curabitur 
ultricies erat felis, vitae rutrum arcu placerat vel.
Nulla dapibus dictum arcu, nec varius lacus tempor non.
Maecenas aliquet porta dui quis aliquam. Proin dictum orci
auctor orci vulputate, commodo tristique neque posuere.
Aliquam in eros eu arcu fermentum dignissim nec vehicula diam."""

    text2 = \
"""Cras suscipit quis lacus eu vulputate. Donec commodo volutpat tellus, 
sed finibus enim aliquam in. Suspendisse id felis dignissim, 
pharetra turpis in, convallis velit. Morbi magna felis, porttitor 
vel volutpat eget, condimentum vitae est. Cras lacus nunc, sagittis
vel nisi quis, tincidunt aliquam elit. Vivamus sagittis suscipit sem,
eget pretium nibh. Pellentesque rhoncus velit ut nisi egestas, nec 
iaculis elit fermentum. Etiam tempus ante lacinia, ornare ante id,
bibendum arcu. Mauris purus dui, placerat blandit scelerisque in, 
varius vitae enim. Nullam eu leo a urna tincidunt interdum vitae sed felis. 
In id nibh in quam sollicitudin egestas non sed est.

Sed interdum, nulla ut tempor lacinia, magna sem accumsan turpis,
sit amet hendrerit purus odio pretium turpis.
Curabitur convallis tempor consequat.
Proin dictum imperdiet eros nec vehicula."""

    filename = "/lorem_ipsum.txt"

    memory.add_texts(
        texts = [text1],
        ids = [filename],
    )

    assert memory.get_document(filename) == text1

    memory.append_texts(
        texts = [text2],
        ids = [filename],
    )

    assert memory.get_document(filename) == "\n".join([text1, text2])

def test_load_folders():
    emb = FakeEmbeddings(dim=250)
    memory = FileSystem(
        index_name = "test",
        embeddings = emb,
        wipe_on_start = True,
    )

    memory.add_folders(
        ["tests/hybridstores/filesystem/test_folder"],
    )

    assert memory.is_folder("/home/user/test_folder")
    assert memory.is_file("/home/user/test_folder/plaintext_test.txt")
    assert memory.is_file("/home/user/test_folder/markdown_test.md")