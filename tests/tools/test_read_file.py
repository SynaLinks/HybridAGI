import dspy
from hybridagi.tools import ReadFileTool
from dspy.utils.dummies import DummyLM
from hybridagi.hybridstores.filesystem.filesystem import FileSystem
from hybridagi.embeddings.fake import FakeEmbeddings
from hybridagi import AgentState

def test_read_file_tool():
    # Set up the test environment
    embeddings = FakeEmbeddings(dim=250)
    
    # Create test files
    test_files = {
        "/home/user/test1.txt": "This is the content of test1.txt",
        "/home/user/test2.txt": "This is the content of test2.txt",
    }
    
    filesystem = FileSystem(
        index_name="test",
        embeddings=embeddings,
        wipe_on_start=True,
    )
    
    # Add test files to the filesystem
    for filename, content in test_files.items():
        filesystem.add_texts(
            texts=[content],
            ids=[filename],
        )
    
    agent_state = AgentState()
    
    dspy.settings.configure(lm=DummyLM(answers=["/home/user/test1.txt", "/home/user/test2.txt"]))
    
    # Create the ReadFileTool
    tool = ReadFileTool(
        filesystem=filesystem,
        agent_state=agent_state,
    )
    
    # Test reading existing files
    for filename, expected_content in test_files.items():
        expected_content = f"{expected_content}\n\n{{'filename': '{filename}'}}"
        prediction = tool(
            objective="Read file content",
            context="Testing ReadFileTool",
            purpose="Verify file reading",
            prompt=f"Read the file {filename}",
            disable_inference=False,
        )

        assert prediction.filename == filename, f"Filename mismatch for {filename}"
        assert prediction.content == expected_content, f"Content mismatch for {filename}"
