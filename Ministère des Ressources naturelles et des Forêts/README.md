# Ministère des Ressources naturelles et des Forêts — annual reports on forest insects, diseases and fires

Every table from the Quebec ministry's annual report
**« Insectes, maladies et feux dans les forêts du Québec »**, 1999 to 2025 (27 reports),
converted to CSV. The 1999 and 2000 editions were titled
*« Insectes et maladies des arbres – Bilan annuel »*.

Source: Ministère des Ressources naturelles et des Forêts (MRNF), formerly MFFP / MRN,
Direction de la protection des forêts. PDFs downloaded from mrnf.gouv.qc.ca in October 2026.

## Contents

| Folder / file | What it is |
|---|---|
| `index_tables.csv` | **Start here.** One row per table: year, table number, title, how it was extracted, where it is in the report, size, and CSV file |
| `tables/YYYY/` | 767 tables extracted automatically from the Markdown version of each report |
| `tables_manuelles/YYYY/` | 25 tables typed out by hand because the PDF prints them as pictures |
| `rapports_pdf/` | The 27 original reports (PDF) |
| `rapports_md/` | The same reports converted to Markdown (pymupdf4llm), used for the extraction |

**Coverage:** 792 tables in total. All 274 numbered tables ("Tableau N") in the 27 reports are included.
The other tables have no number in the report: appendix lists of insects and diseases, fire statistics,
seed orchard results, etc.

## What the files look like

Each CSV starts with comment lines beginning with `#`: the table's title as printed, and where it comes from.
The data follows. In a spreadsheet, skip the `#` lines, or in Python use `pandas.read_csv(file, comment="#")`.

**Automatic tables (`tables/`):** these keep the layout of the printed table.

- **Two values in one cell.** Many tables print the current year and the previous year in the same cell, the
  previous year in parentheses or grey. These cells contain both values on two lines, e.g. `486 219` / `927 692`.
- **Numbers.** They use spaces as thousands separators (`1 321 052`) and commas as decimal marks (`15,87`),
  exactly as printed.
- **Headers.** Multi-line headers can span several rows at the top of the table.
- **Footnote marks.** These appear as `^1`, `^a`, `*`.

**Hand-typed tables (`tables_manuelles/`):** these are cleaned up. There is one value per cell and plain
numbers, and the current and previous years are on separate rows with a `Année` column. Wherever a table
has totals, every row and column was checked against them. One error in the source report was found and
kept as printed, with a note in the file: 2010, Tableau 2, Sapinière row total.

| Year | Hand-typed tables | Why |
|---|---|---|
| 2004 | Tableaux 1–14 | The whole report prints its tables as images |
| 2005 | Tableau 2 | Image |
| 2006 | Tableau 15 | Image |
| 2007 | Tableau 1 | Image |
| 2010, 2015, 2016, 2017 | Tableau 2 (plantations visitées) | Image |
| 2022, 2023 | Tableau 1 (plantations visitées) | Image |
| 2022, 2024 | Tableau 6 (œufs d'arpenteuse de la pruche) | Garbled by the Markdown conversion |

## Things to know

- **The tables change from year to year.** Titles, columns, regions and units vary, so the same subject
  (e.g. spruce budworm areas) is not always in the same table number. Use `index_tables.csv` to find tables
  by title.
- **Check against the PDF.** The automatic extraction keeps all the printed values, but complex tables
  (merged cells, rotated headers) can end up with values shifted by a column. The `emplacement_source`
  column of the index tells you where to look in the PDF.
- **Symbols are kept as printed.** For example `X` (negligible losses), `●` (not quantified), `s.o.`
  (sans objet), `<1` (less than 1 ha). Each report explains its symbols below the table.

## How it was made

The scripts are in [`../scripts/`](../scripts/):
1. PDFs converted to Markdown with pymupdf4llm.
2. `md_tables_to_csv.py` extracts every Markdown table to CSV and attaches each "Tableau N" caption.
3. Picture tables were read from the PDF page images and typed out by hand.
