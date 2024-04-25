"""The archiver utility. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

import os
import zipfile
from time import gmtime, strftime
from ..hybridstores.filesystem.path import basename
from ..hybridstores.filesystem.filesystem import FileSystem

class ArchiverUtility():
    """The archiver utility"""

    def __init__(
            self,
            filesystem: FileSystem,
            downloads_directory: str,
        ):
        self.filesystem = filesystem
        self.downloads_directory = downloads_directory

    def zip_and_download(self, path:str) -> str:
        """Method to convert into .zip and download to downloads folder"""
        if not self.filesystem.exists(path):
            raise ValueError("No such file or directory.")
        name = strftime("%Y-%m-%d_%H:%M:%S_", gmtime())+basename(path)
        filename = os.path.join(self.downloads_directory, name)
        f = zipfile.ZipFile(filename+".zip", mode='a')
        if self.filesystem.is_file(path):
            file_content = self.filesystem.get_document(path)
            f.writestr(basename(path), file_content)
        elif self.filesystem.is_folder(path):
            self.zip_folders_and_files(path, path, f)
        else:
            raise ValueError(f"Cannot upload {path}: Can only upload file or folder")
        f.close()
        return filename+".zip"

    def zip_folders_and_files(
            self,
            target_folder_path:str,
            current_folder_path:str,
            zip_file:zipfile.ZipFile
        ):
        """Method to recursively add folder and files"""
        params = {"folder_path": current_folder_path}
        result_query = self.filesystem.hybridstore.query(
            "MATCH (f:Folder {name:$folder_path})-[:CONTAINS]->(n:Folder) RETURN n",
            params = params,
        )
        for record in result_query.result_set:
            subfolder_path = record[0].properties["name"]
            self.zip_folders_and_files(
                target_folder_path,
                subfolder_path,
                zip_file
            )
        params = {"folder_path": current_folder_path}
        result_query = self.filesystem.hybridstore.query(
            "MATCH (f:Folder {name:$folder_path})-[:CONTAINS]->(n:Document) RETURN n",
            params = params,
        )
        for record in result_query.result_set:
            document_path = record[0].properties["name"]
            file_content = self.filesystem.get_document(document_path)
            zip_file.writestr(
                document_path.replace(target_folder_path, ""),
                file_content,
            )