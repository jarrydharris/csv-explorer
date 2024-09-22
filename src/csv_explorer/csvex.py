from typing import Iterable, Optional
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, DirectoryTree, DataTable, Static
from pathlib import Path
from textual import log


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

    def on_directory_tree_file_selected(self, file: DirectoryTree.FileSelected):
        if file.path.suffix == ".csv":
            if self.currently_displayed_file == file.path:
                return
            log(f"Selected: {file.path}")
            with open(file.path, "r") as fp:
                self.currently_displayed_file = file.path
                rows = [row.split(",") for row in fp.readlines()]
                log(rows)
            table = self.query_one(DataTable)
            table.add_columns(*rows[0])
            table.add_rows(rows[1:])

    def compose(self) -> ComposeResult:
        yield Header(id="header")
        with Horizontal():
            with Vertical():
                yield CsvDirectoryTree(id="dir-viewer", path="./")
                yield Static("Placehholder")
            yield DataTable(id="csv-viewer")


if __name__ == "__main__":
    app = CsvExplorer()
    app.run()
