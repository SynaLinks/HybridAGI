import os
from typing import List
from ..hybridstores.filesystem.context import FileSystemContext
from ..hybridstores.fact_memory.fact_memory import FactMemory
from ..hybridstores.filesystem.filesystem import FileSystem
from ..knowledge_parsers.base import BaseKnowledgeParser

class KnowledgeLoader():

    def __init__(
            self,
            filesystem: FileSystem,
            fact_memory: FactMemory,
            parsers: List[BaseKnowledgeParser] = []
        ):
        self.filesystem = filesystem
        self.fact_memory = fact_memory
        self.valid_extensions = []
        self.parsers = {}
        for parser in parsers:
            self.valid_extensions.extend(parser.valid_extensions)
            for extension in parser.valid_extensions:
                self.parsers[extension] = parser

    def from_folders(
            self,
            folders: List[str],
        ):
        for i, folder in enumerate(folders):
            folder_name = os.path.basename(folder)
            ctxt = FileSystemContext()
            folder_name = ctxt.eval_path(folder_name)
            self.filesystem.create_folder(folder_name)
            for dirpath, dirnames, filenames in os.walk(folder):
                if "venv" in dirpath or dirpath.startswith("__") > 0 or dirpath.startswith(".") > 0:
                    continue
                for filename in filenames:
                    if not filename.startswith("."):
                        _, extension = os.path.splitext(filename)
                        if extension in self.valid_extensions:
                            parser = self.parsers[extension]
                            source_path = os.path.join(dirpath, filename)
                            target_path = os.path.join(dirpath.replace(folder, folder_name), filename)
                            if extension in self.valid_extensions:
                                try:
                                    file_content = parser.read(source_path)
                                    parser.parse(target_path, file_content)
                                except Exception:
                                    continue