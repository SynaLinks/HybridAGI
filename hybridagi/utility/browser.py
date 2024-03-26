"""The browser utility. Copyright (C) 2023 SynaLinks. License: GPL-3.0"""

import re
from typing import Tuple, Dict, Any, List
import requests
from bs4 import BeautifulSoup
from langchain.schema import Document
from ..hybridstores.filesystem.filesystem import FileSystem
from langchain.text_splitter import RecursiveCharacterTextSplitter

class BrowserUtility():
    filesystem: FileSystem
    user_agent: str
    current_consulted_url: str = ""
    last_url_consulted: str = ""
    current_documents: List[Document] = []
    current_document_index:int = 0

    def scrap_text(
            self,
            url: str,
        ) -> Tuple[str, Dict[str, Any]]:
        """Method to scrap the text from an url, modified from BabyAGI"""
        headers = {"User-Agent": self.user_agent}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")
        result = soup.get_text()
        metadata = {"url":url,"href":[]}
        for link in soup.findAll('a', attrs={'href': re.compile("^https://")}):
            metadata["href"].append(link.get('href'))
        return result, metadata

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
            page_content, metadata = self.scrap_text(url)
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size = self.filesystem.chunk_size,
                chunk_overlap = self.filesystem.chunk_overlap,
            )
            sub_docs = text_splitter.split_documents(
                [Document(page_content = page_content, metadata = metadata)]
            )
            self.current_documents = sub_docs
            self.current_document_index = 0
        else:
            self.current_document_index = (self.current_document_index + 1) % len(self.current_documents)
        self.current_consulted_url = url

        content = self.current_documents[self.current_document_index].page_content
        metadata = self.current_documents[self.current_document_index].metadata

        result_string = content
        if self.current_document_index != len(self.current_documents)-1:
            result_string + "\n\n[...]" + f"\n\n{metadata}"
        else:
            result_string
        return result_string + f"\n\n{metadata}"