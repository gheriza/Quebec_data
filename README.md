# Quebec environmental data

Public data about Quebec, downloaded from government and research websites
in October 2026 and converted to CSV. The data is organized by theme. Each
theme folder has its own `README.md` that explains every file and column.

## What's here

| Folder | Theme | What one row is | Years | Source |
|---|---|---|---|---|
| `1_climate/` | Weather and climate | One weather station at one time (hour, day or month) | 1870 – 2026 | Environment and Climate Change Canada |
| `2_forest/insect_defoliation_livree/` | Damage from the forest tent caterpillar (*livrée des forêts*) | One damaged forest area, or one 30 m satellite pixel | 1985 – 2025 | Quebec Ministry of Natural Resources and Forests (MRNF), via Données Québec |
| `2_forest/forest_cover_change_hansen/` | Tree cover and tree loss from satellite | One region-year, one ~1 km grid square, or one 30 m pixel | 2000 – 2025 | University of Maryland (Hansen et al.), Global Forest Change v1.13 |
| `3_biodiversity/insect_specimens_ciq/` | Museum insect specimens (dragonflies and damselflies) | One preserved specimen | 1930 – 2015 | Collection d'insectes du Québec, via Canadensys |
| `4_pesticides/` | Pesticide wholesale sales | One active ingredient × use sector × year | 2020 – 2024 | Quebec Ministry of the Environment (MELCCFP), via Données Québec |
| `Ministère des Ressources naturelles et des Forêts/` | Every table from the annual reports on forest insects, diseases and fires (792 tables, plus the 27 PDFs) | One table per CSV | 1999 – 2025 | Quebec Ministry of Natural Resources and Forests (MRNF) |

## The kinds of data you'll find

All files are CSV (comma-separated, UTF-8). They come in four kinds:

- **Summary tables**: small, ready for Excel. Start here.
  Examples: `2_forest/forest_cover_change_hansen/summary_tables/`, `4_pesticides/`.
- **Time series by location**: one row per place per date (weather stations).
  Every row has latitude/longitude. Files: `1_climate/measurements/`, `1_climate/normals/`.
- **Areas (polygons)**: each row is a mapped area. The `geometry_wkt` column holds its outline as text,
  and `centroid_lon`/`centroid_lat` give its center point. Open these in QGIS
  (*Layer → Add Delimited Text Layer → Geometry: WKT*), or simply use the center point.
- **Pixels and grids**: each row is one square of the map (30 m pixel or ~1 km cell)
  with its longitude/latitude. These are very large; use QGIS, Python or R.

**Excel limit:** Excel can open at most 1,048,576 rows. The files marked **(large)** in the
theme READMEs are bigger than that. Don't open them in Excel; it will cut off the data without warning.

## Compressed and split files

GitHub doesn't accept files over 100 MB, so the biggest CSVs are stored compressed:

| In the repository | Becomes |
|---|---|
| `….csv.gz` | one CSV: unzip it with 7-Zip (Windows), double-click (macOS), or `gunzip file.csv.gz` (Linux) |
| `….csv.gz.part00`, `.part01`, … | one CSV split into 90 MB pieces: join the pieces first, then unzip |

**Joining the pieces:**

- **Linux / macOS:** `cat quebec_forest_loss_pixels.csv.gz.part* | gunzip > quebec_forest_loss_pixels.csv`
- **Windows (Command Prompt):** `copy /b quebec_forest_loss_pixels.csv.gz.part* quebec_forest_loss_pixels.csv.gz`,
  then unzip the `.gz` with 7-Zip.
- **Python** (any system):

  ```python
  import glob, gzip, shutil
  name = "quebec_forest_loss_pixels.csv"
  with open(name + ".gz", "wb") as out:          # 1. join the pieces
      for part in sorted(glob.glob(name + ".gz.part*")):
          with open(part, "rb") as f:
              shutil.copyfileobj(f, out)
  with gzip.open(name + ".gz", "rb") as f, open(name, "wb") as out:   # 2. unzip
      shutil.copyfileobj(f, out)
  ```

  Or read them directly without unzipping: `pandas.read_csv("file.csv.gz")` works on any `.gz` file.

## Other folders

| Folder | Content |
|---|---|
| `scripts/` | The Python scripts used to download and convert the data, so it can be re-run or updated |
| `logs/` | Run logs |

The original Hansen image tiles (2.7 GB) are in the companion repository **[gheriza/Quebec_data_1](https://github.com/gheriza/Quebec_data_1)**.

## Data not included

- **Landsat mosaics (diffusion.mern.gouv.qc.ca)**: the server blocks connections from outside Canada.
- **Hansen `first`/`last` layers**: raw Landsat images (about 40 GB), not forest-change results.
