# 3 — Biodiversity

## insect_specimens_ciq/

Dragonfly and damselfly (Odonata) specimens kept in the **Collection d'insectes du Québec (CIQ)**.
Source: Canadensys IPT, dataset `ciq-specimens`, version 2.3 (July 6, 2020).
DOI: 10.5886/msuujw. License: CC0 (public domain).

| File | Rows | One row = |
|---|---|---|
| `ciq_specimens_odonates.csv` | 667 | One preserved specimen |
| `metadata_eml.xml` | — | Official dataset description: authors, citation, contacts |

**Format:** Darwin Core, the international standard for biodiversity records. Main columns:

- **What:** `scientificName`, `family`, `genus`, `specificEpithet`, `taxonRank`
- **Where:** `stateProvince`, `locality`, `decimalLatitude`, `decimalLongitude`,
  `coordinateUncertaintyInMeters` (how precise the position is)
- **When:** `eventDate`, `year`, `month`, `day`
- **Who/which:** `recordedBy` (collector), `catalogNumber` (museum number)

**Summary:** 74 species, collected 1930–2015, mostly 1937–38 and 1953–56. 655 specimens are from Quebec and have coordinates.

**Things to know:**
- This is only the odonate part of the collection (the CIQ holds about 60,000 specimens); the rest is not published online.
- 25 columns are empty in the source (e.g. sex, habitat). They are kept so the file matches the Darwin Core standard.
