# 2 — Forest

Two independent datasets about Quebec's forests.

| Folder | Question it answers | Method |
|---|---|---|
| `insect_defoliation_livree/` | Where and when did the **forest tent caterpillar** (*livrée des forêts*) eat the leaves of trees? | Aerial surveys (1985–2018) and satellite detection (2024–2025) by the Quebec government |
| `forest_cover_change_hansen/` | How much forest was there in 2000, and how much was **lost each year** 2001–2025 (from any cause)? | Global 30 m Landsat satellite analysis by the University of Maryland |

---

## insect_defoliation_livree/

Source: *Données sur les perturbations naturelles – Insecte : Livrée des forêts*,
MRNF, Données Québec. License: CC-BY 4.0.

| File | Rows | Size | One row = |
|---|---|---|---|
| `areas_aerial_surveys_1985_2018/Livree_1985_2010.csv` | 10,354 | 17 MB | One area seen defoliated from an aircraft |
| `areas_aerial_surveys_1985_2018/Livree_2014_2018.csv` | 4,961 | 56 MB | Same, 2014–2018 |
| `areas_satellite_2024_2025/Livree_des_forets_defoliation_2024.csv.gz` (compressed) | 37,050 | 233 MB unzipped | One area detected as defoliated by satellite |
| `areas_satellite_2024_2025/Livree_des_forets_defoliation_2025.csv` | 4,846 | 29 MB | Same, 2025 |
| `pixels_satellite_2024_2025/…_2024_pixels.csv` **(large)** | 1,789,101 | 91 MB | One 30 m pixel of the 2024 detection image |
| `pixels_satellite_2024_2025/…_2025_pixels.csv` | 133,960 | 7 MB | Same, 2025 |
| `data_dictionaries/` | — | — | Official column descriptions (French), from the source |

**Aerial survey columns:**
- `Annee`/`ANNEE`: year.
- `Niveau`: defoliation severity. In 1985–2010 it's a number (1 = light, 2 = moderate, 3 = severe); in 2014–2018 it's text (Léger/Modéré/Grave).
- `Ia`: severity as a number in 2014–2018.
- `Sup_Ha`/`SupHaCea`: area in hectares.

**Satellite columns:**
- `ANNEE`: year.
- `Niv_Confia`: confidence that the damage is caterpillar damage (Faible = low, Modéré = moderate, Élevé = high).
  2024 spells it with accents, 2025 without.
- `No_RegAdm`/`Nom_RegAdm`: administrative region.
- `SupHa_Cea`: area in hectares.

**Added to every area file:** `centroid_lon`, `centroid_lat` (center point) and `geometry_wkt` (full outline).

**Pixel files:** position in Quebec Lambert (`x_lambert_epsg32198`, `y_lambert_epsg32198`) and in degrees (`lon`, `lat`),
and the pixel's color (`R`, `G`, `B`). The source gives no legend for the colors, so they aren't translated into classes.

**Gaps:** no data for 2011–2013 or 2019–2023. 8 polygons in 1985–2010 have no valid shape (empty geometry, attributes kept).

---

## forest_cover_change_hansen/

Source: Hansen, M. C. et al. (2013), *High-Resolution Global Maps of 21st-Century Forest Cover Change*,
Science 342. Data version GFC-2025-v1.13, clipped to Quebec. License: CC-BY 4.0.

| File | Rows | Size | One row = |
|---|---|---|---|
| `summary_tables/quebec_forest_by_region.csv` | 19 | 4 KB | One administrative region (+ Quebec total) |
| `summary_tables/quebec_forest_loss_by_region_year.csv` | 475 | 20 KB | One region × one year |
| `grid_1km/quebec_forest_grid_0.01deg.csv.gz` **(large, compressed)** | 2,084,703 | 321 MB unzipped | One 0.01° square (~1.1 km × 0.7 km) |
| `loss_pixels_30m/quebec_forest_loss_pixels.csv.gz.part00`–`part10` **(large, split)** | 271,438,702 | 8.1 GB unzipped | One 30 m pixel where trees were lost |
| `boundaries/quebec_regions_administratives.geojson` | 18 | 1.4 MB | Region outlines used to clip and group the data |
| `raw_geotiff_tiles/` *(in [gheriza/Quebec_data_1](https://github.com/gheriza/Quebec_data_1))* | 35 files | 2.7 GB | Original image tiles (for QGIS/ArcGIS) |

**Definitions:**
- **Forest** = tree canopy cover above 30% in the year 2000.
- **Loss** = all trees in a pixel removed, from any cause: logging, fire, insects, wind. It is not only permanent deforestation; much of it grows back.
- **Gain** = new tree cover between 2000 and 2020 only (not updated after 2020 by the authors).
- All areas are in **hectares** (1 ha = 0.01 km²).

**Columns:**
- `forest2000_ha`: forest area in 2000.
- `loss_ha_YYYY`: forest lost that year.
- `loss_ha_any_canopy`: loss counting every tree-covered pixel, whatever its canopy cover.
- `gain_ha_2000_2020`: gain.
- `mean_treecover2000_pct`: average canopy cover in 2000.
- In the pixel file, `treecover2000_pct` (0–100) lets you apply a different forest threshold yourself.

**Original image tiles:** stored in [gheriza/Quebec_data_1](https://github.com/gheriza/Quebec_data_1). The 35 GeoTIFFs used here (layers `datamask`, `treecover2000`, `lossyear`, `gain`;
tiles `50N_080W`, `50N_070W`, `50N_060W`, `60N_080W`, `60N_070W`, `60N_060W`, `70N_080W`, `70N_070W`, `70N_060W`)
can also be downloaded from the source:
`https://storage.googleapis.com/earthenginepartners-hansen/GFC-2025-v1.13/Hansen_GFC-2025-v1.13_<layer>_<tile>.tif`
(there is no `lossyear` tile for `70N_060W`, which has no forest loss).

**Regions:** "Côte-Nord (Tracé de 1927)" is the area along the Labrador border that is disputed between Quebec and
Newfoundland-and-Labrador. It is a separate row, so you can include or exclude it. The Quebec total includes it.
