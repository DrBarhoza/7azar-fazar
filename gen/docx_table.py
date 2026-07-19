"""Read the first table out of a .docx, as rows of plain-text cells.

Shared by the Word-file question banks (medicine_gen_docx.py, animals_gen_docx.py).
Treats the .docx as the zip it is and walks the table XML, so nothing outside the
standard library is needed.
"""
import zipfile
import xml.etree.ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def cell_text(tc):
    """A cell's paragraphs joined by newline, runs within a paragraph concatenated."""
    paras = ["".join(t.text or "" for t in p.iter(f"{W}t")) for p in tc.iter(f"{W}p")]
    return "\n".join(paras).strip()


def rows_from_docx(path, width=None):
    """Yield the first table's rows. With `width`, skip rows of any other size."""
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    tbl = next(root.iter(f"{W}tbl"))
    for tr in tbl.findall(f"{W}tr"):
        cells = [cell_text(tc) for tc in tr.findall(f"{W}tc")]
        if width is None or len(cells) == width:
            yield cells
