"""The OWL graph loader. Copyright (C) 2023 SynaLinks. License: GPLv3"""

class OWLGraphLoader(BaseGraphLoader):
    """Class to load .owl ontologies"""
    client: redis.Redis
    filepath: str
    graph_key: str = "graph"

    def load() -> Graph:
        """Method to load file"""
        if not filepath.endswith(".owl"):
            raise ValueError("OWL graph loader can only process .owl files")
        raise NotImplementedError("Not implemented yet.")