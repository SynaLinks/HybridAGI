"""The virtual filesystem index. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

import os
from colorama import Fore, Style
from typing import List, Optional
from langchain.schema import Document
from hybrid_agi.filesystem.filesystem import (
    join,
    FileSystemUtility,
    VirtualFileSystem,
)
from hybrid_agi.filesystem.text_editor import VirtualTextEditor

class VirtualFileSystemIndexWrapper(FileSystemUtility):
    filesystem: VirtualFileSystem
    text_editor: VirtualTextEditor
    verbose: bool = True

    def add_documents(self, names: List[str], documents: list[Document]):
        assert len(names) == len(documents)
        for i, doc in enumerate(documents):
            if self.verbose:
                print(f"{Fore.GREEN}[*] Adding document '{Fore.YELLOW}{names[i]}{Fore.GREEN}'...{Style.RESET_ALL}")
            path = self.filesystem.context.eval_path(names[i])
            self.text_editor.write_document(path, doc.page_content, metadata=doc.metadata)

    def add_folders(self, folders: List[str], folder_names: Optional[List[str]] = None):
        names = []
        docs = []
        for i, folder in enumerate(folders):
            folder_name = os.path.basename(folder) if folder_names is None else folder_names[i]
            if self.verbose:
                print(f"{Fore.GREEN}[*] Adding folder '{Fore.YELLOW}{folder_name}{Fore.GREEN}'...{Style.RESET_ALL}")
            self.create_folder(folder_name)
            for dirpath, dirnames, filenames in os.walk(folder):
                if dirpath.find("__") > 0 or dirpath.find(".git") > 0:
                    continue
                for dirname in dirnames:
                    if not dirname.startswith("__") and not dirname.startswith(".git"):
                        path = join([dirpath.replace(folder, folder_name), dirname])
                        if self.verbose:
                            print(f"{Fore.GREEN}[*] Adding folder '{Fore.YELLOW}{path}{Fore.GREEN}'...{Style.RESET_ALL}")
                        self.create_folder(path)
                for filename in filenames:
                    if not filename.startswith(".") and not filename.endswith(".zip"):
                        source = os.path.join(dirpath, filename)
                        try:
                            f = open(source, "r")
                            file_content = f.read()
                            doc = Document(page_content=str(file_content))
                            path = join([dirpath.replace(folder, folder_name), filename])
                            docs.append(doc)
                            names.append(path)
                        except Exception as err:
                            print(f"{Fore.RED}[!] Error occured with {source}: {str(err)}{Style.RESET_ALL}")
        self.add_documents(names, docs)
    