from ..hybridstores.filesystem.filesystem import FileSystem

class ReaderUtility():
    """The reader utility"""
    def __init__(
            self,
            filesystem: FileSystem,
            verbose: bool = True):
        """The reader constructor"""
        self.filesystem = filesystem
        self.current_consulted_document = ""
        self.last_content_consulted = ""
        self.verbose = verbose

    def read_document(self, path:str) -> str:
        """
        Method to read a document.
        This method display only one content at a time.
        Use it multiple times with the same target to scroll.
        """
        if self.filesystem.exists(path):
            if self.filesystem.is_folder(path):
                return f"Cannot read {path}: Is a directory."
        else:
            return f"Cannot read {path}: No such file or directory"
        if self.current_consulted_document != "":
            if self.current_consulted_document == path:
                content_key = self.filesystem.get_next(self.last_content_consulted)
                next_key = self.filesystem.get_next(content_key)
            else:
                content_key = self.filesystem.get_beginning_of_file(path)
                next_key = self.filesystem.get_next(content_key)
        else:
            content_key = self.filesystem.get_beginning_of_file(path)
            next_key = self.filesystem.get_next(content_key)
        
        if next_key != "":
            self.current_consulted_document = path
        else:
            self.current_consulted_document = ""
        content = str(self.filesystem.get_content(content_key))
        self.last_content_consulted = content_key
        if next_key != "":
            return content + "\n\n[...]"
        else:
            return content