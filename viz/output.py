"""Gravação das imagens e das notas em disco."""

import csv
from pathlib import Path

from matplotlib.figure import Figure

from viz.notes import Note


def save_images(figures: dict[str, Figure], out: Path, dpi: int) -> None:
    """Salva cada figura como `<nome>.png` em `out`, criando a pasta se preciso."""
    out.mkdir(parents=True, exist_ok=True)
    for name, figure in figures.items():
        path = out / f"{name}.png"
        figure.savefig(path, dpi=dpi)
        print(path)


def save_notes(notes: dict[str, Note], out: Path) -> None:
    """Salva cada nota como `<nome>.md` e, se ela tiver tabela, também `<nome>.csv`, em UTF-8."""
    out.mkdir(parents=True, exist_ok=True)
    for name, note in notes.items():
        (out / f"{name}.md").write_text(note.markdown, encoding="utf-8")
        if note.table is not None:
            _write_csv(out / f"{name}.csv", *note.table)


def _write_csv(path: Path, header: list[str], rows: list[list[str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(rows)
