from __future__ import annotations

import json
import re
from pathlib import Path

from IPython.core.inputtransformer2 import TransformerManager


PROJECT_ROOT = Path(__file__).resolve().parents[1]
POLISH_CHARACTERS = set(
    "ąćęłńóśźżĄĆĘŁŃÓŚŹŻ"
)
LOCAL_PATH_PATTERN = re.compile(
    r"(?:"
    r"[A-Za-z]:\\(?:Users|Zbiory danych|Downloads|Documents|Desktop)\\|"
    r"[A-Za-z]:/(?:Users|home)/|"
    r"/Users/|/home/|~\\AppData"
    r")"
)
POLISH_WORD_PATTERN = re.compile(
    r"\b(?:brak|blad|kompresja|liczba|plik|predykcja|przetworzono|"
    r"usunieto|wczytano|wyniki|zapisano|zbior)\b",
    flags=re.IGNORECASE,
)
DYNAMIC_PATH_OUTPUT_PATTERN = re.compile(
    r"(?:print|raise|write).*\{[^}]*(?:path|dir|DIR|filepath)"
)


def notebook_paths() -> list[Path]:
    return sorted((PROJECT_ROOT / "notebooks").rglob("*.ipynb"))


def source_text(cell: dict) -> str:
    source = cell.get("source", "")
    return "".join(source) if isinstance(source, list) else source


def nested_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from nested_strings(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from nested_strings(item)


def test_notebooks_are_valid_and_outputs_are_sanitized() -> None:
    paths = notebook_paths()
    assert paths, "No notebooks found under notebooks/"

    for path in paths:
        label = path.relative_to(PROJECT_ROOT).as_posix()
        notebook = json.loads(path.read_text(encoding="utf-8"))
        for index, cell in enumerate(notebook.get("cells", [])):
            if cell.get("cell_type") != "code":
                continue
            for text in nested_strings(cell.get("outputs", [])):
                assert not (POLISH_CHARACTERS & set(text)), (
                    f"{label}: cell {index} has Polish text in its output"
                )
                assert not POLISH_WORD_PATTERN.search(text), (
                    f"{label}: cell {index} has Polish words in its output"
                )
                assert not LOCAL_PATH_PATTERN.search(text), (
                    f"{label}: cell {index} output contains a local path"
                )


def test_notebook_sources_do_not_contain_local_paths_or_polish_text() -> None:
    for path in notebook_paths():
        label = path.relative_to(PROJECT_ROOT).as_posix()
        notebook = json.loads(path.read_text(encoding="utf-8"))
        for index, cell in enumerate(notebook.get("cells", [])):
            text = source_text(cell)
            assert not LOCAL_PATH_PATTERN.search(text), (
                f"{label}: cell {index} contains a local absolute path"
            )
            assert not (POLISH_CHARACTERS & set(text)), (
                f"{label}: cell {index} contains Polish characters"
            )
            assert not POLISH_WORD_PATTERN.search(text), (
                f"{label}: cell {index} contains Polish words"
            )
            assert "index_script" not in text, (
                f"{label}: cell {index} imports the legacy module"
            )
            for line in text.splitlines():
                if not DYNAMIC_PATH_OUTPUT_PATTERN.search(line):
                    continue
                assert "display_path" in line or ".name" in line, (
                    f"{label}: cell {index} can expose an absolute path"
                )


def test_notebook_code_cells_compile_after_ipython_transformation() -> None:
    transformer = TransformerManager()

    for path in notebook_paths():
        label = path.relative_to(PROJECT_ROOT).as_posix()
        notebook = json.loads(path.read_text(encoding="utf-8"))
        for index, cell in enumerate(notebook.get("cells", [])):
            if cell.get("cell_type") != "code":
                continue
            text = source_text(cell)
            transformed = transformer.transform_cell(text)
            compile(
                transformed,
                f"{label}::cell-{index}",
                "exec",
            )
