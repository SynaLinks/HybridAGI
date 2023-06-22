"""The upload tool. Copyright (C) 2023 SynaLinks. License: GPLv3"""

import os
import zipfile
from colorama import Fore, Style
from datetime import datetime
from typing import Optional, Callable
from pydantic import BaseModel, Extra, Field, root_validator
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain.tools import BaseTool, StructuredTool, Tool, tool
from hybrid_agi.filesystem.filesystem import VirtualFileSystem, basename, join, dirname
from hybrid_agi.filesystem.text_editor import VirtualTextEditor
from hybrid_agi.parsers.path import PathOutputParser
from hybrid_agi.hybridstores.redisgraph import RedisGraphHybridStore

from inspect import signature
from langchain.tools.base import create_schema_from_function

class UploadTool(BaseTool):
    hybridstore: RedisGraphHybridStore
    filesystem: VirtualFileSystem
    text_editor: VirtualTextEditor
    downloads_directory:str
    path_parser = PathOutputParser()
    func: Callable

    class Config:
        """Configuration for this pydantic object."""
        extra = Extra.forbid
        arbitrary_types_allowed = True

    def __init__(
            self,
            hybridstore: RedisGraphHybridStore,
            filesystem: VirtualFileSystem,
            text_editor: VirtualTextEditor,
            downloads_directory: str,
            name:str = "Upload",
            description:str =\
    """
    Usefull to send a folder or file for testing and inspection.
    The Input should be the target path.
    """
        ):
        func = self.upload
        description = f"{name}{signature(func)} - {description.strip()}"
        super().__init__(
            name = name,
            description = description,
            hybridstore = hybridstore,
            filesystem = filesystem,
            text_editor = text_editor,
            downloads_directory = downloads_directory,
            func = func
        )

    def upload(self, path:str) -> str:
        try:
            path = self.path_parser.parse(query)
            path = self.filesystem.context.eval_path(path)
            filename = self.zip_and_download(path)
            print(f"{Fore.YELLOW}[*] Successfully archived into: {filename}{Style.RESET_ALL}")
            return "Successfully uploaded."
        except Exception as err:
            return str(err)

    def zip_and_download(self, path:str) -> str:
        """Method to zip a file or folder.

        The content is converted into .zip and downloaded into the user's downloads folder.

        Args:
            path (str): The target path to archive
        """
        if not self.text_editor.exists(path):
            raise ValueError("No such file or directory.")
        name = datetime.now().strftime("%d-%m-%Y_%H:%M:%S_"+basename(path))
        filename = os.path.join(self.downloads_directory, name)
        f = zipfile.ZipFile(filename+".zip", mode='a')
        if self.text_editor.is_file(path):
            file_content = self.text_editor.get_document(path)
            f.writestr(path, file_content)
        elif self.text_editor.is_folder(path):
            self.zip_folders_and_files(path, f)
        else:
            raise ValueError(f"Cannot upload {path}: Can only upload file or folder")
        f.close()
        return filename

    def zip_folders_and_files(self, folder_path:str, zip_file:zipfile.ZipFile):
        """Method to add folder and files"""
        result_query = self.hybridstore.metagraph.query('MATCH (f:Folder {name:"'+path+'"})-[:CONTAINS]->(n:Folder) RETURN n')
        for record in result_query.result_set:
            subfolder_name = record[0].properties["name"]
            subfolder_path = join(subfolder_path, basename(subfolder_name))
            zip_file.mkdir(subfolder_path, mode="666")
            self.add_folders_and_files(subfolder_path, zip_file)
            result_query = self.hybridstore.metagraph.query('MATCH (f:Folder {name:"'+path+'"})-[:CONTAINS]->(n:Document) RETURN n')
        for record in result_query.result_set:
            document_name = record[0].properties["name"]
            document_path = join(folder_path, basename(document_name))
            file_content = self.text_editor.get_document(document_path)
            zip_file.writestr(document_path, file_content)

    def _run(self, query:str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        return self.upload(query.strip())

    def _arun(self, query:str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        return self._run(query, run_manager)