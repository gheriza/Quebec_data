# 4 — Pesticide wholesale sales

Quantities of pesticide active ingredients sold by licensed wholesalers in Quebec.
Source: *Ventes en gros de pesticides au Québec*, MELCCFP, Données Québec.

| File | Rows | One row = |
|---|---|---|
| `ventes_en_gros_pesticides_2020_2024.csv` | 2,998 | One active ingredient × use sector × year |

## Columns

| Column | Meaning |
|---|---|
| `Annee` | Year of sale (2020–2024) |
| `Secteur_utilisation` | Where it's used: agriculture, forestry, golf courses, domestic use, industry, etc. (9 sectors) |
| `Type_utilisation` | Kind of product as written in the source: herbicide, fungicide, insecticide, etc. |
| `Type_utilisation_harmonise` | The same, with 2020's different spellings standardized so all years match |
| `Code_groupe_chimique`, `Nom_groupe_chimique` | Chemical family |
| `Code_ingredient_actif`, `Nom_ingredient_actif` | The active ingredient |
| `Quantite_vendue_kg_ia` | Kilograms of active ingredient sold |

## Things to know

- **Group ingredients by `Code_ingredient_actif`, not by name.** Names are spelled differently from year to year
  (e.g. "GLYPHOSATE SEL DE POTASSIUM" vs "GLYPHOSATE (SEL DE POTASSIUM)").
- **The same ingredient can appear more than once in one year and sector** (134 cases, 2022–2024), with different
  quantities. These are separate declarations in the source. Add them together; don't delete any.
- **5 rows have no quantity.** They are microorganisms (e.g. *Bacillus thuringiensis*), which aren't measured in kg.
- **This is sales to resellers, not use.** It shows what wholesalers sold, not what was applied in fields.

**Total per year:** 4.58 M kg (2020), 5.09 M (2021), 5.06 M (2022), 5.42 M (2023), 4.77 M (2024).
