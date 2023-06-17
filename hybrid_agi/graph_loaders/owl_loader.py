## The OWL graph loader.
## Copyright (C) 2023 SynaLinks.
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program. If not, see <https://www.gnu.org/licenses/>.

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