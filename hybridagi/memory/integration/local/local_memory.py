from urllib.parse import quote
from uuid import uuid4


def isolate(html_code: str) -> str:
    """
    When drawing the same pyvis graph from multiple cells in a jupyter notebook
    They end up sharing the same id for the javascript <script> and thus messing each other
    display(display_id=...) or making unique IDs in HTML() doesn't work unfortunately
    Here's the issue that proposes this workaround https://github.com/jupyter/notebook/issues/6598
    """
    content = quote(html_code, safe='')
    return """
    <iframe
        width="100%"
        height="610px"
        style="border: none"
        sandbox="allow-scripts allow-modals"
        referrerpolicy="no-referrer"
        src="data:text/html;charset=UTF-8,{content}"
    ></iframe>
    """.format(content=content)


class LocalMemory:       
    def show(self, notebook: bool = False, cdn_resources: str = 'in_line') -> None:
        """
        Visualize the local memory as a network graph.

        Parameters:
            notebook (bool): Whether to display the graph in a Jupyter notebook or not.
            cdn_resources (str): Where to pull resources for css and js files. Defaults to local.
                Options ['local','in_line','remote'].
                local: pull resources from local lib folder.
                in_line: insert lib resources as inline script tags.
                remote: pull resources from hash checked cdns.
        """
        from pyvis.network import Network
        net = Network(notebook=notebook, directed=True, cdn_resources=cdn_resources)
        net.from_nx(self._graph)
        net.toggle_physics(True)

        if notebook:
            from IPython.display import display, HTML
            unique_id = f'{uuid4().hex}.html'
            html = net.generate_html(unique_id, notebook=True)
            display(HTML(isolate(html)), display_id=unique_id)
        else:
            net.show(f'{self.index_name}.html', notebook=notebook)
