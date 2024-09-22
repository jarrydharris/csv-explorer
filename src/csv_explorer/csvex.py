from typing import Iterable, Optional
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, DirectoryTree, DataTable, ListView, ListItem, Label
from pathlib import Path
import duckdb
from datetime import datetime


class CsvDirectoryTree(DirectoryTree):
    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [path for path in paths if path.name.endswith(".csv") or path.is_dir()]


class CsvExplorer(App):
    currently_displayed_file: Optional[str] = None
    CSS = """
    #dir-viewer{
        width: 100%;
        height: auto;
        padding: 2;
        tint: magenta 10%;
    }
    #csv-viewer{
        width: 70%;
        height: 100%;
        tint: green 10%;
    }
    """

    def on_tree_node_highlighted(self, highlighted: DirectoryTree.NodeHighlighted):
        path: Path = highlighted.node.data.path
        if path.suffix == ".csv":
            parent: ListView = self.query_one("#metadata")
            csv = duckdb.read_csv(path)
            parent.clear()
            parent.append(ListItem(Label(str(path.name))))
            for header in csv.columns:
                parent.append(ListItem(Label(str(header))))

    def on_directory_tree_file_selected(self, file: DirectoryTree.FileSelected):
        if file.path.suffix == ".csv":
            table = self.query_one(DataTable)
            table.clear(columns=True)
            csv = duckdb.read_csv(file.path)
            rows: duckdb.DuckDBPyRelation = csv.select("*").fetchall()
            headers = csv.columns
            table.add_columns(*headers)
            for row in rows:
                if isinstance(row[0], datetime):
                    table.add_row(row[0].strftime("%Y-%b-%d %H:%M"), *row[1:])
                else:
                    table.add_row(*row)

    def compose(self) -> ComposeResult:
        yield Header(id="header")
        with Horizontal():
            with Vertical():
                yield CsvDirectoryTree(id="dir-viewer", path="./")
                yield ListView(id="metadata")
            yield DataTable(id="csv-viewer")


if __name__ == "__main__":
    app = CsvExplorer()
    app.run()
