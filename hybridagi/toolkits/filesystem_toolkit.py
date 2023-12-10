from .base import BaseToolKit
from hybridagikb import FileSystem
from hybridagikb.tools import (
    ShellTool,
    WriteFilesTool,
    AppendFilesTool,
    ReadFileTool,
    UploadTool,
    ContentSearchTool,
)

class FileSystemToolKit(BaseToolKit):
    filesystem: FileSystem
    downloads_directory: str

    def __init__(
        self,
        filesystem: FileSystem,
        downloads_directory: str):

        shell_tool = ShellTool(
            filesystem = filesystem)
        
        write_files_tool = WriteFilesTool(
            filesystem = filesystem)

        append_files_tool = AppendFilesTool(
            filesystem = filesystem)

        read_file_tool = ReadFileTool(
            filesystem = filesystem)

        upload_tool = UploadTool(
            filesystem = filesystem,
            downloads_directory = downloads_directory)

        content_search_tool = ContentSearchTool(
            filesystem = filesystem)

        tools = [
            shell_tool,
            write_files_tool,
            append_files_tool,
            read_file_tool,
            upload_tool,
            content_search_tool,
        ]

        super().__init__(
            filesystem = filesystem,
            downloads_directory = downloads_directory,
            tools = tools,
        )