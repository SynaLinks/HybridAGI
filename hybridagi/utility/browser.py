"""The browser utility. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

import re
from typing import Tuple, Dict, Any, List
import requests
from ..hybridstores.filesystem.filesystem import FileSystem

class BrowserUtility():

    def __init__(
            self,
            filesystem: FileSystem,
            chunk_size: int = 1024,
            chunk_overlap: int = 0,
        ):
        self.filesystem = filesystem
        self.current_consulted_url = ""
        self.last_url_consulted = ""
        self.current_chunks = []
        self.current_chunk_index = 0
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def scrap_text(
            self,
            url: str,
        ) -> str:
        """Method to scrap the text from an url using jina.ai"""
        response = requests.get("https://r.jina.ai/"+url)
        return response.text

    def browse_website(
            self,
            url: str,
        ) -> str:
        """
        Method to browse a website url.
        This method display only one chunk at a time.
        Use it multiple times with the same target to scroll.
        """
        scrap = False
        if self.current_consulted_url != "":
            if self.current_consulted_url != url:
                scrap = True
        else:
            scrap = True
        if scrap:
            page_content = self.scrap_text(url)
            text_splitter = \
            SentenceTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )
            chunks = text_splitter.split_text(text)
            self.current_chunks = chunks
            self.current_chunk_index = 0
        else:
            self.current_chunk_index = (self.current_chunk_index + 1) % len(self.current_chunks)
        self.current_consulted_url = url

        content = self.current_chunks[self.current_chunk_index].page_content
        metadata = self.current_chunks[self.current_chunk_index].metadata

        result_string = content
        if self.current_chunk_index != len(self.current_chunks)-1:
            result_string + "\n\n[...]"
        else:
            result_string
        return result_string