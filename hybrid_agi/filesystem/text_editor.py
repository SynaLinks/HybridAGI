from typing import Optional, List, Dict, Any
from langchain.schema import Document
from hybrid_agi.filesystem.filesystem import FileSystemUtility, dirname
from langchain.base_language import BaseLanguageModel
from langchain.text_splitter import RecursiveCharacterTextSplitter

from hybrid_agi.hybridstores.redisgraph import RedisGraphHybridStore
from hybrid_agi.extractors.graph.graph_extractor import GraphExtractor
from hybrid_agi.extractors.summary.summary_extractor import SummaryExtractor

class VirtualTextEditor(FileSystemUtility):
    """Virtual text editor for the filesystem."""
    llm: BaseLanguageModel

    graph_extractor: GraphExtractor
    summary_extractor: SummaryExtractor
    
    chunk_size: int = 1000
    chunk_overlap: int = 0
    current_consulted_document: str = ""
    last_content_consulted: str = ""
    verbose: bool = True
    
    def __init__(self,
            hybridstore: RedisGraphHybridStore,
            llm: BaseLanguageModel,
            chunk_size: int,
            chunk_overlap: int,
            verbose: bool = True
        ):
        graph_extractor = GraphExtractor(
            hybridstore = hybridstore,
            llm = llm,
            verbose = verbose
        )
        summary_extractor = SummaryExtractor(
            hybridstore = hybridstore,
            llm = llm,
            verbose = verbose
        )
        super().__init__(
            hybridstore = hybridstore,
            llm = llm,
            chunk_size = chunk_size,
            chunk_overlap = chunk_overlap,
            graph_extractor = graph_extractor,
            summary_extractor = summary_extractor,
            verbose = verbose
        )

    def is_beginning_of_file(self, content_key:str) -> bool:
        """Returns True if the content is the beginning of the file"""
        result = self.hybridstore.metagraph.query('MATCH (n:Content {name:"'+content_key+'"})<-[:BOF]-() RETURN n')
        if len(result.result_set) > 0:
            return True
        return False

    def is_end_of_file(self, content_key:str) -> bool:
        """Returns True if the content is the end of the file"""
        result = self.hybridstore.metagraph.query('MATCH (n:Content {name:"'+content_key+'"})<-[:EOF]-() RETURN n')
        if len(result.result_set) > 0:
            return True
        return False
    
    def get_beginning_of_file(self, path: str) -> str:
        result = self.hybridstore.metagraph.query('MATCH (:Document {name:"'+path+'"})-[:BOF]->(n:Content) RETURN n')
        return result.result_set[0][0].properties["name"]

    def get_end_of_file(self, path: str) -> str:
        result = self.hybridstore.metagraph.query('MATCH (:Document {name:"'+path+'"})-[:EOF]->(n:Content) RETURN n')
        return result.result_set[0][0].properties["name"]

    def get_next(self, content_key: str) -> str:
        result = self.hybridstore.metagraph.query('MATCH (:Content {name:"'+content_key+'"})-[:NEXT]->(n:Content) RETURN n')
        if len(result.result_set) > 0:
            return result.result_set[0][0].properties["name"]
        return ""

    def write_document(self, path: str, text: str, metadata: Dict[Any, Any]={}) -> str:
        """Method to write a document."""
        if self.exists(path):
            return "Already exist, cannot override."
        texts = []
        folder = dirname(path)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
        sub_docs = text_splitter.split_documents([Document(page_content=text, metadata=metadata)])
        texts = [d.page_content for d in sub_docs]
        metadatas = [d.metadata for d in sub_docs]
        self.create_document(path)
        keys = self.hybridstore.add_texts(texts, metadatas=metadatas)
        for idx, key in enumerate(keys):
            self.hybridstore.metagraph.query('MERGE (n:Content {name:"'+key+'"})')
            self.hybridstore.metagraph.query('MATCH (n:Document {name:"'+path+'"}), (m:Content {name:"'+key+'"}) MERGE (n)-[:CONTAINS]->(m)')
            if idx > 0:
                self.hybridstore.metagraph.query('MATCH (n:Content {name:"'+keys[idx-1]+'"}), (m:Content {name:"'+key+'"}) MERGE (n)-[:NEXT]->(m)')
        if len(keys) > 0:
            self.hybridstore.metagraph.query('MATCH (n:Document {name:"'+path+'"}), (m:Content {name:"'+keys[0]+'"}) MERGE (n)-[:BOF]->(m)')
            self.hybridstore.metagraph.query('MATCH (n:Document {name:"'+path+'"}), (m:Content {name:"'+keys[len(keys)-1]+'"}) MERGE (n)-[:EOF]->(m)')
        return "Successfuly created file"

    def update_document(self, path:str, modifications:str) -> str:
        """Method to update a document."""
        if self.llm is None:
            raise ValueError("LLM should not be None.")
        if not self.exists(path):
            return "No such file or directory."
        else:
            if self.is_folder(path):
                return "Not a file."
        bof = self.get_beginning_of_file(path)
        eof = self.get_end_of_file(path)
        if bof == eof:
            self._update_content(path, bof, modifications)
        else:
            result = self.hybridstore.metagraph.query('MATCH path=(:Content {name:"'+bof+'"})-[:NEXT*]->(:Content {name:"'+eof+'"}) RETURN nodes(path)')
            for record in result.result_set:
                content_key = record[0].properties["name"]
                self._update_content(path, content_key, modifications)
        return "Successfuly updated file."

    def _update_content(self, path:str, content_key:str, modifications:str) -> List[str]:
        """Method to update a content."""
        if self.llm is None:
            raise ValueError("LLM should not be None.")
        content_to_update = self.hybridstore.get_content(content_key)
        content_metadata = self.hybridstore.get_content_metadata(content_key)
        chain = LLMChain(llm=self.llm, prompt=UPDATE_FILE_PROMPT, verbose=self.verbose)
        updated_content = chain.predict(text=content_to_update, modifications=modifications)
        if len(updated_content) > 1.5 * self.chunk_size:
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
            sub_docs = text_splitter.split_documents([Document(page_content=updated_content, metadata=json.load(content_metadata))])
            texts = [d.page_content for d in sub_docs]
            metadatas = [d.metadata for d in sub_docs]
            keys = self.hybridstore.add_texts(texts, metadatas=metadatas)
            for idx, key in enumerate(keys):
                self.hybridstore.metagraph.query('MERGE (n:Content {name:"'+key+'"})')
                if idx > 0:
                    self.hybridstore.metagraph.query('MATCH (n:Content {name:"'+keys[idx-1]+'"}), (m:Content {name:"'+key+'"}) MERGE (n)-[:NEXT]->(m)')
            if self.is_beginning_of_file(content_key):
                self.hybridstore.metagraph.query('MATCH (n:Document {name:"'+path+'"}), (m:Content {name:"'+keys[0]+'"}) MERGE (n)-[:BOF]->(m)')
            if self.is_end_of_file(content_key):
                self.hybridstore.metagraph.query('MATCH (n:Document {name:"'+path+'"}), (m:Content {name:"'+keys[len(keys)-1]+'"}) MERGE (n)-[:EOF]->(m)')
            self.hybridstore.metagraph.query('MATCH (n:Content {name:"'+content_key+'"}) DETACH DELETE n')
            self.hybridstore.delete_content(content_key)
            return keys
        else:
            self.hybridstore.set_content(content_key, updated_content)
            self.hybridstore.set_content_vector(content_key, updated_content)
            return [content_key]

    def read_document(self, path:str) -> str:
        """
        Method to read a document.
        This method display only one content at a time.
        Use it multiple times with the same target to scroll.
        """
        if self.exists(path):
            if self.is_folder(path):
                return "Cannot read directory."
        else:
            return "No such file or directory."
        if self.current_consulted_document != "":
            if self.current_consulted_document == path:
                content_key = self.get_next(self.last_content_consulted)
                if content_key != "":
                    self.last_content_consulted = content_key
                    return self.hybridstore.get_content(content_key)
                else:
                    self.current_consulted_document = ""
                    self.last_content_consulted = ""
                    return "End Of File"
        content_key = self.get_beginning_of_file(path)
        self.current_consulted_document = path
        self.last_content_consulted = content_key
        return self.hybridstore.get_content(content_key)

    def get_document(self, path:str) -> str:
        """
        Method to get the full document.
        Do not use it for the LLM tools as it can exceed the max token.
        """
        if self.exists(path):
            if self.is_folder(path):
                return "Cannot read directory."
        else:
            return "No such file or directory."
        text = ""
        bof = self.get_beginning_of_file(path)
        eof = self.get_end_of_file(path)
        result = self.hybridstore.metagraph.query('MATCH path=(:Content {name:"'+bof+'"})-[:NEXT*]->(:Content {name:"'+eof+'"}) RETURN nodes(path)')
        for record in result.result_set:
            content_key = record[0].properties["name"]
            content = self.hybridstore.get_content(content_key)
            text += content
        return text




