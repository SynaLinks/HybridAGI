"""The tools related to the virtual text editor. Copyright (C) 2023 SynaLinks. License: GPLv3"""

import shlex
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


class PathWithDataInputSchema(BaseModel):
    path: str
    data: str

class PathInputSchema(BaseModel):
    path: str

def _parse_output(output:str):
    try:
        args = shlex.split(output)
    except Exception as err: 
        if "No closing quotation" in str(err):
            try:
                args = shlex.split('"'+output+'"')
            except Exception as err:
                raise err
        else:
            raise err
    path = args[0]
    path = path.replace(",", "")
    data = args[1]
    return path, data

class WriteFileTool(BaseTool):
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
    Both parameters needs to be double quoted.
    """
        ):
        super().__init__(
            name = name,
            description = description,
            filesystem = filesystem,
            text_editor = text_editor,
            # args_schema = PathWithDataInputSchema
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
            return self.text_editor.write_document(path, text)
        except Exception as err:
            return str(err)

    def _run(self, query:str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        path, data = _parse_output(query)
        return self.write_file(path, data)

    def _arun(self, query:str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        return self._run(query, run_manager)

class UpdateFileTool(BaseTool):
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
    Both parameters needs to be double quoted.
    """
        ):
        super().__init__(
            name = name,
            description = description,
            filesystem = filesystem,
            text_editor = text_editor,
            # args_schema = PathWithDataInputSchema
        )

    def update_file(self, path:str, modifications:str) -> str:
        try:
            path = self.path_parser.parse(path)
            path = self.filesystem.context.eval_path(path)
            return self.text_editor.update_document(path, modifications)
        except Exception as err:
            return str(err)

    def _run(self, query:str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        path, data = _parse_output(query)
        return self.update_file(path, data)

    def _arun(self, query:str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        return self._run(query, run_manager)

class ReadFileTool(BaseTool):
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
    Usefull when you want to read or check an existing file.
    The input should be the target path.
    Display one chunk at a time, use multiple times with the same target to scroll.
    """
        ):
        super().__init__(
            name = name,
            description = description,
            filesystem = filesystem,
            text_editor = text_editor,
            args_schema = PathInputSchema
        )

    def read_file(self, path: str) -> str:
        try:
            path = self.path_parser.parse(path)
            path = self.filesystem.context.eval_path(path)
            return self.text_editor.read_document(path)
        except Exception as err:
            return str(err)

    def _run(self, query:str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        return self.read_file(query.strip())

    def _arun(self, query:str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        return self._run(query, run_manager)