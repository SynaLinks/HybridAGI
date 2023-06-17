from typing import Optional, Type, List, Tuple
from pydantic import BaseModel, Extra, Field, root_validator
from langchain.base_language import BaseLanguageModel
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain.tools import BaseTool, StructuredTool, Tool, tool
from langchain.schema import Document
from hybrid_agi.filesystem.filesystem import VirtualFileSystem
from hybrid_agi.filesystem.text_editor import VirtualTextEditor
from hybrid_agi.parsers.path import PathOutputParser
from langchain.chains.llm import LLMChain
from inspect import signature
from langchain.tools.base import create_schema_from_function

class WriteFileTool(StructuredTool):
    filesystem: VirtualFileSystem
    text_editor: VirtualTextEditor
    path_parser = PathOutputParser()

    def __init__(
            self,
            filesystem: VirtualFileSystem,
            text_editor: VirtualTextEditor,
            name = "WriteFile",
            description = \
    """
    Usefull when you want to write into a new file.
    The Input should be the target path followed by the data to write.
    """
        ):
        func = self.write_file
        description = f"{name}{signature(func)} - {description.strip()}"
        super().__init__(
            name = name,
            description = description,
            filesystem = filesystem,
            text_editor = text_editor,
            func = func,
            args_schema = create_schema_from_function(f"{name}Schema", func)
        )

    class Config:
        """Configuration for this pydantic object."""
        extra = Extra.forbid
        arbitrary_types_allowed = True

    def write_file(self, path: str, text: str) -> str:
        """Use the tool."""
        try:
            path = self.path_parser.parse(path)
            path = self.filesystem.context.eval_path(path)
            return self.text_editor.write_document(path, data)
        except Exception as err:
            return str(err)

    def _run(self, query:str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            super()._run(query, run_manager)
        except Exception as err:
            return str(err)

class UpdateFileTool(StructuredTool):
    filesystem: VirtualFileSystem
    text_editor: VirtualTextEditor
    path_parser = PathOutputParser()

    class Config:
        """Configuration for this pydantic object."""
        extra = Extra.forbid
        arbitrary_types_allowed = True

    def __init__(
            self,
            filesystem: VirtualFileSystem,
            text_editor: VirtualTextEditor,
            name = "UpdateFile",
            description = \
    """
    Usefull when you want to modify an existing file using your own LLM.
    The Input should be the target path followed by the modifications to make.
    Make sure to include you goal/instruction and every necessary modification to make.
    """
        ):
        func = self.update_file
        super().__init__(
            name = name,
            description = description,
            filesystem = filesystem,
            text_editor = text_editor,
            func = func,
            args_schema = create_schema_from_function(f"{name}Schema", func)
        )

    def update_file(self, path:str, modifications:str) -> str:
        try:
            path = self.path_parser.parse(path)
            path = self.filesystem.context.eval_path(path)
            return self.text_editor.update_document(path, data)
        except Exception as err:
            return str(err)

    def _run(self, query:str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            super()._run(query, run_manager)
        except Exception as err:
            return str(err)

class ReadFileTool(StructuredTool):
    filesystem: VirtualFileSystem
    text_editor: VirtualTextEditor
    
    path_parser = PathOutputParser()

    class Config:
        """Configuration for this pydantic object."""
        extra = Extra.forbid
        arbitrary_types_allowed = True

    def __init__(
            self,
            filesystem: VirtualFileSystem,
            text_editor: VirtualTextEditor,
            name = "ReadFile",
            description =\
    """
    Usefull when you want to read a existing file.
    The Input should be the target path.
    Display one chunk at a time, use multiple times with the same target to scroll.
    """
        ):
        func = self.read_file
        super().__init__(
            name = name,
            description = description,
            filesystem = filesystem,
            text_editor = text_editor,
            func = func,
            args_schema = create_schema_from_function(f"{name}Schema", func)
        )

    def read_file(self, path: str) -> str:
        try:
            path = self.path_parser.parse(path)
            path = self.filesystem.context.eval_path(path)
            return self.text_editor.read_document(path)
        except Exception as err:
            return str(err)

    def _run(self, query:str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            super()._run(query, run_manager)
        except Exception as err:
            return str(err)