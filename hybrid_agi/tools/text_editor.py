"""The tools related to the virtual text editor. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

import re
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

def _parse_output(output:str):
    output = output.strip()
    if not output.endswith("\n```"):
        output = output + "\n```"
    output = output.replace("\n\n```", "\n```")
    pattern = r"^(?P<filename>[a-zA-Z0-9_.-]+)\n```(?P<lang>[a-zA-Z]+)\n(?P<content>.*?)\n```$"
    match = re.match(pattern, output, re.DOTALL)
    if match:
        filename = match.group('filename')
        lang = match.group('lang')
        content = match.group('content')
        return filename, content
    else:
        raise ValueError("Invalid format. Could not parse the LLM output.")

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
    The Input should follow the following format:
    FILENAME
    ```LANG
    CONTENT
    ```
    Where the following tokens must be replaced such that:
    FILENAME is the lowercase file name including the file extension.
    LANG is the markup code block language for the code's language if any.
    CONTENT its content.
    """
        ):
        super().__init__(
            name = name,
            description = description,
            filesystem = filesystem,
            text_editor = text_editor
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
    Usefull when you want to write into a new file.
    The Input should follow the following format:
    FILENAME
    ```LANG
    MODIFICATIONS
    ```
    Where the following tokens must be replaced such that:
    FILENAME is the lowercase file name including the file extension.
    LANG is the markup code block language for the code's language if any.
    MODIFICATIONS are the instructions to modify the file.
    """
        ):
        super().__init__(
            name = name,
            description = description,
            filesystem = filesystem,
            text_editor = text_editor
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


class AppendFileTool(BaseTool):
    filesystem: VirtualFileSystem
    text_editor: VirtualTextEditor
    path_parser = PathOutputParser()


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
            description = \
    """
    Usefull when you want to read or check an existing file.
    The input should be a string containing the target path.
    Display one chunk at a time, use multiple times with the same target to scroll.
    """
        ):
        super().__init__(
            name = name,
            description = description,
            filesystem = filesystem,
            text_editor = text_editor
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