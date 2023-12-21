"""The archiver utility. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

import os
import zipfile
from time import gmtime, strftime
from ..hybridstores.filesystem.path import basename
from ..hybridstores.filesystem.filesystem import FileSystem

class ArchiverUtility():
    def __init__(
            self,
            filesystem: FileSystem,
            downloads_directory: str,
            verbose: bool = True
        ):
        self.filesystem = filesystem
        self.downloads_directory = downloads_directory
        self.verbose = verbose

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
        result_query = self.filesystem.query(
            'MATCH (f:Folder {name:"'+current_folder_path+'"})-[:CONTAINS]->(n:Folder)'+
            ' RETURN n'
        )
        for record in result_query:
            subfolder_path = record[0].properties["name"]
            self.zip_folders_and_files(
                target_folder_path,
                subfolder_path,
                zip_file
            )
        result_query = self.filesystem.query(
            'MATCH (f:Folder {name:"'+current_folder_path+
            '"})-[:CONTAINS]->(n:Document)'+
            ' RETURN n'
        )
        for record in result_query:
            document_path = record[0].properties["name"]
            file_content = self.filesystem.get_document(document_path)
            zip_file.writestr(
                document_path.replace(target_folder_path, ""),
                file_content
            )