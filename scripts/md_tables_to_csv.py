"""Convert the tables in Markdown versions of the MRNF annual reports
"Insectes, maladies et feux dans les forêts du Québec" to CSV files.

Usage: python3 md_tables_to_csv.py <folder with .md files> <output folder>

Each Markdown table (lines starting with '|') becomes one CSV. The caption is
taken from the closest "Tableau N ..." line above the table (within 6 lines).
Inside cells: bold/italic markers are removed, <sup>n</sup> footnote marks
become "^n", and <br> line breaks are kept as line breaks.
Tables of contents (rows of dot leaders) are skipped.
Writes <out>/tables/YYYY/YYYY_md_tN.csv and <out>/index_tables_md.csv.
"""
import csv
import glob
import os
import re
import sys

SRC, OUT = sys.argv[1], sys.argv[2]
CAPTION = re.compile(r"^\W*(Tableau|TABLEAU)\s+(\d+[A-Za-z]?)\b\s*[.:–-]?\s*(.*)")
YEAR = re.compile(r"(19|20)\d\d")


def year_of(path, text):
    m = YEAR.search(os.path.basename(path))
    if m:
        return m.group(0)
    m = re.search(r"(?:en|annuel)\s+((?:19|20)\d\d)", text[:3000])
    return m.group(1) if m else "unknown"


def clean_cell(c):
    c = re.sub(r"<sup>\s*([^<]*?)\s*</sup>", r"^\1", c)
    c = re.sub(r"<br\s*/?>", "\n", c)
    c = re.sub(r"<[^>]+>", "", c)
    c = c.replace("**", "").replace("__", "")
    lines = [re.sub(r"[ \t]+", " ", l).strip() for l in c.split("\n")]
    return "\n".join(l for l in lines if l)


def split_row(line):
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [clean_cell(c) for c in re.split(r"(?<!\\)\|", s)]


def is_separator(cells):
    return all(re.fullmatch(r":?-{2,}:?", c.replace(" ", "")) or c == "" for c in cells) and any(cells)


def is_toc(rows):
    cells = [c for r in rows for c in r if c]
    return bool(cells) and sum("....." in c for c in cells) / len(cells) > 0.3


def tables_in(lines):
    i = 0
    while i < len(lines):
        if lines[i].lstrip().startswith("|"):
            start = i
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                i += 1
            yield start, lines[start:i]
        else:
            i += 1


def caption_before(lines, start):
    for j in range(start - 1, max(-1, start - 7), -1):
        text = re.sub(r"<[^>]+>", "", lines[j]).replace("**", "")
        m = CAPTION.match(text)
        if m:
            return m.group(2), re.sub(r"\s+", " ", text).strip(" #")
        if lines[j].lstrip().startswith("|"):
            break
    return "", ""


def caption_row(row):
    """'Tableau N ...' printed as a table row. The converter sometimes cuts the
    caption across cells mid-word, so each text line is rebuilt by joining the
    cells without spaces."""
    parts = [c.split("\n") for c in row if c]
    text = " ".join("".join(p[i] for p in parts if i < len(p)) for i in range(max(map(len, parts), default=0)))
    m = CAPTION.match(text)
    return (m.group(2), re.sub(r"\s+", " ", text).strip()) if m else None


def segments(rows, num, cap):
    """Split a table wherever a caption row appears; yields (number, caption, rows)."""
    seg = []
    for r in rows:
        found = caption_row(r)
        if found:
            if seg:
                yield num, cap, seg
            (num, cap), seg = found, []
        else:
            seg.append(r)
    if seg:
        yield num, cap, seg


def main():
    index = []
    for path in sorted(glob.glob(os.path.join(SRC, "*.md"))):
        text = open(path, encoding="utf-8").read()
        lines = text.split("\n")
        y = year_of(path, text)
        ydir = os.path.join(OUT, "tables", y)
        os.makedirs(ydir, exist_ok=True)
        k = 0
        for start, block in tables_in(lines):
            rows = [split_row(l) for l in block]
            rows = [r for r in rows if not is_separator(r) and any(r)]
            if len(rows) < 2 or is_toc(rows):
                continue
            width = max(len(r) for r in rows)
            rows = [r + [""] * (width - len(r)) for r in rows]
            keep = [j for j in range(width) if any(r[j] for r in rows)]
            rows = [[r[j] for j in keep] for r in rows]
            if len(keep) < 2:
                continue
            num, cap = caption_before(lines, start)
            for num, cap, seg in segments(rows, num, cap):
                k += 1
                name = f"{y}_md_t{k:02d}.csv"
                with open(os.path.join(ydir, name), "w", newline="", encoding="utf-8") as f:
                    w = csv.writer(f)
                    if cap:
                        w.writerow([f"# {cap}"])
                    w.writerow([f"# Source: Insectes, maladies et feux dans les forêts du Québec {y} ({os.path.basename(path)}, line {start + 1})"])
                    w.writerows(seg)
                index.append([y, os.path.basename(path), start + 1, k, num, cap, len(seg), len(seg[0]), f"tables/{y}/{name}"])
        print(f"{y}: {k} tables from {os.path.basename(path)}", flush=True)
    with open(os.path.join(OUT, "index_tables_md.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["year", "source_md", "md_line", "table_in_report", "tableau_number", "caption", "rows", "columns", "file"])
        w.writerows(index)


if __name__ == "__main__":
    main()
