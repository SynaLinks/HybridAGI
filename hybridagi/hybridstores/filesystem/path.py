from typing import List

def join(paths: List[str]) -> str:
    return '/'.join(paths)

def dirname(path:str) -> str:
    if path == "/":
        return path
    else:
        tokens = path.split('/')
        dirname = '/'.join(tokens[:-1])
        if dirname == "":
            return "/"
        return dirname

def basename(path:str) -> str:
    tokens = path.split('/')
    return tokens[-1]