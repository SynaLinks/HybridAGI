import pytest
from unittest.mock import Mock, patch
from uuid import UUID

from hybridagi.core.datatypes import Document, DocumentList
from docling_core.types.doc.document import DoclingDocument

# Import the classes we're testing
from hybridagi.modules.splitters.docling_splitter import DoclingHierarchicalChunker
from hybridagi.readers.docling_reader import DoclingReader

# Fixtures for common test data
@pytest.fixture
def sample_text_items():
    """Creates sample text items for testing."""
    # Create basic mocks with just the text attribute
    item1 = Mock()
    item1.text = "Sample text 1"
    item2 = Mock()
    item2.text = "Sample text 2"
    return [(item1, 1), (item2, 1)]  # Return tuples of (item, level)

@pytest.fixture
def sample_docling_document(sample_text_items):
    """Creates a mock DoclingDocument for testing with iterate_items support."""
    mock_doc = Mock(spec=DoclingDocument)
    mock_doc.export_to_text.return_value = "Sample text content"
    mock_doc.export_to_markdown.return_value = "# Sample markdown content"
    mock_doc.export_to_dict.return_value = {"content": "Sample content"}
    
    # Configure the iterate_items method to return our sample items
    mock_doc.iterate_items.return_value = sample_text_items
    return mock_doc

@pytest.fixture
def sample_converter_result(sample_docling_document):
    """Creates a mock converter result containing a DoclingDocument."""
    mock_result = Mock()
    mock_result.document = sample_docling_document
    return mock_result

# Tests for DoclingReader
class TestDoclingReader:
    def test_init(self):
        """Test that DoclingReader can be instantiated."""
        reader = DoclingReader()
        assert isinstance(reader, DoclingReader)
    
    @pytest.mark.parametrize("format,expected_content", [
        ("text", "Sample text content"),
        ("markdown", "# Sample markdown content"),
        ("json", '{"content": "Sample content"}')
    ])
    def test_read_different_formats(self, format, expected_content, sample_converter_result):
        """Test reading documents in different formats."""
        with patch('docling.document_converter.DocumentConverter.convert') as mock_convert:
            mock_convert.return_value = sample_converter_result
            
            reader = DoclingReader()
            doc_list, docling_doc = reader.read("dummy/path.txt", format=format)
            
            # Verify the returned values
            assert isinstance(doc_list, DocumentList)
            assert isinstance(docling_doc, DoclingDocument)
            assert len(doc_list.docs) == 1 # type: ignore
            assert doc_list.docs[0].text == expected_content # type: ignore
            assert doc_list.docs[0].metadata["format"] == format # type: ignore
            assert doc_list.docs[0].metadata["filepath"] == "dummy/path.txt" # type: ignore
            assert doc_list.docs[0].metadata["converter"] == "docling" # type: ignore

    def test_read_invalid_filepath_with_raise_mode(self):
        """Test that reading an invalid filepath raises ValueError when raise_mode is True."""
        with patch('docling.document_converter.DocumentConverter.convert') as mock_convert:
            mock_convert.side_effect = FileNotFoundError
            
            reader = DoclingReader()
            with pytest.raises(ValueError) as exc_info:
                reader.read("nonexistent/file.txt", raise_mode=True)
            assert "Conversion failed" in str(exc_info.value)

    def test_read_invalid_filepath_without_raise_mode(self):
        """Test that reading an invalid filepath returns None values when raise_mode is False."""
        with patch('docling.document_converter.DocumentConverter.convert') as mock_convert:
            mock_convert.side_effect = FileNotFoundError
            
            reader = DoclingReader()
            doc_list, docling_doc = reader.read("nonexistent/file.txt", raise_mode=False)
            
            assert doc_list is None
            assert docling_doc is None

# Tests for DoclingHierarchicalChunker
class TestDoclingHierarchicalChunker:
    @pytest.fixture
    def sample_chunks(self):
        """Creates sample chunks for testing."""
        chunk1 = Mock()
        chunk1.text = "Chunk 1 content"
        chunk2 = Mock()
        chunk2.text = "Chunk 2 content"
        return [chunk1, chunk2]
    
    def test_init(self, sample_docling_document):
        """Test chunker initialization."""
        chunker = DoclingHierarchicalChunker(sample_docling_document)
        assert chunker.doclingdoc == sample_docling_document

    def test_forward_single_document(self, sample_docling_document, sample_chunks):
        """Test processing a single document."""
        with patch('docling_core.transforms.chunker.hierarchical_chunker.HierarchicalChunker.chunk') as mock_chunk:
            mock_chunk.return_value = sample_chunks
            
            chunker = DoclingHierarchicalChunker(sample_docling_document)
            input_doc = Document(
                text="Original text",
                metadata={"source": "test"},
                id=UUID("6d8235a2-9404-4290-8b34-72525dff7272")
            )
            
            result = chunker.forward(input_doc)
            
            assert isinstance(result, DocumentList)
            assert len(result.docs) == 2  # Two chunks # type: ignore
            for doc in result.docs: # type: ignore
                assert doc.metadata == {"source": "test"}
                assert isinstance(doc.parent_id, UUID)  # Check that parent_id is a UUID
                assert doc.parent_id == input_doc.id    # Direct UUID comparison

    def test_forward_document_list(self, sample_docling_document, sample_chunks):
        """Test processing multiple documents."""
        with patch('docling_core.transforms.chunker.hierarchical_chunker.HierarchicalChunker.chunk') as mock_chunk:
            mock_chunk.return_value = sample_chunks
            
            chunker = DoclingHierarchicalChunker(sample_docling_document)
            doc_list = DocumentList()
            doc1_id = UUID("6d8235a2-9404-4290-8b34-72525dff7272")
            doc2_id = UUID("7d8235a2-9404-4290-8b34-72525dff7272")
            doc_list.docs = [
                Document(text="Doc 1", metadata={"source": "test1"}, id=doc1_id),
                Document(text="Doc 2", metadata={"source": "test2"}, id=doc2_id)
            ]
            
            result = chunker.forward(doc_list)
            
            assert isinstance(result, DocumentList)
            assert len(result.docs) == 4  # Two documents * two chunks each # type: ignore
            # Check that metadata and parent_ids are preserved correctly
            assert len([doc for doc in result.docs if doc.parent_id == doc1_id]) == 2 # type: ignore
            assert len([doc for doc in result.docs if doc.parent_id == doc2_id]) == 2 # type: ignore

    @pytest.mark.parametrize("input_docs,expected_chunks", [
        (Document(text="", metadata={}, id=UUID("6d8235a2-9404-4290-8b34-72525dff7272")), 2),
        (DocumentList(), 0),
    ])
    def test_forward_edge_cases(self, sample_docling_document, input_docs, expected_chunks, sample_chunks):
        """Test edge cases with empty documents or document lists."""
        with patch('docling_core.transforms.chunker.hierarchical_chunker.HierarchicalChunker.chunk') as mock_chunk:
            mock_chunk.return_value = sample_chunks
            
            chunker = DoclingHierarchicalChunker(sample_docling_document)
            result = chunker.forward(input_docs)
            assert isinstance(result, DocumentList)
            assert len(result.docs) == expected_chunks # type: ignore

    def test_forward_invalid_input(self, sample_docling_document):
        """Test that invalid input raises ValueError."""
        chunker = DoclingHierarchicalChunker(sample_docling_document)
        with pytest.raises(ValueError):
            chunker.forward("invalid input") # type: ignore