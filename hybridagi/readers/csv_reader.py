import abc
from typing import Any
import pandas as pd
from hybridagi.readers import DocumentReader
from hybridagi.core.datatypes import Document, DocumentList

class CSVReader(DocumentReader):

    def read(self, filepath: str) -> DocumentList:
        result = DocumentList()
        df = pd.read_csv(filepath)
        for index, row in df.iterrows():
            text = "\n".join(str(row).split("\n")[:-1])
            row_doc = Document(text=text, metadata={"filepath": filepath, "row": index})
            result.docs.append(row_doc)
        return result