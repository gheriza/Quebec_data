# 1 — Climate and weather (Environment and Climate Change Canada)

Measurements from **1,051 weather stations in Quebec**, full history (earliest records: 1870).
Source: Climate Data Extraction Tool, changements-climatiques.canada.ca
(data served by api.weather.gc.ca). License: Open Government Licence – Canada.

## Files

| File | Rows | Size | One row = |
|---|---|---|---|
| `stations/quebec_climate_stations.csv` | 1,051 | 0.3 MB | One station: name, position, elevation, years of data |
| `measurements/quebec_climate_monthly.csv` | 298,949 | 59 MB | One station × one month |
| `measurements/quebec_climate_daily.csv.gz.part00`–`part03` **(large, split)** | 23,229,497 | 3.1 GB unzipped | One station × one day |
| `quebec_climate_hourly.csv.gz.part00`–`part10` **(large, split)**, in [gheriza/Quebec_data_1](https://github.com/gheriza/Quebec_data_1/tree/main/climate_hourly) | 40,470,113 | 9.5 GB unzipped | One station × one hour |
| `normals/quebec_climate_normals.csv` | 81,712 | 18 MB | One station × one variable × one month, averaged over 1981–2010 |

## How the files connect

Every file has `CLIMATE_IDENTIFIER` (e.g. `7025250` = Montréal-Trudeau airport) and `STN_ID`.
Use either one to join measurements to the station list.

## Main columns

**Station list:** `STATION_NAME`, `LATITUDE`/`LONGITUDE` (in this file only: degrees × 10,000,000),
`ELEVATION` (m), `FIRST_DATE`/`LAST_DATE`, and the first/last date of hourly (`HLY_`), daily (`DLY_`) and monthly (`MLY_`) data.

**Monthly:** `LOCAL_YEAR`, `LOCAL_MONTH`, `MEAN_/MIN_/MAX_TEMPERATURE` (°C), `TOTAL_PRECIPITATION` (mm),
`TOTAL_SNOWFALL` (cm), `SNOW_ON_GROUND_LAST_DAY` (cm), `BRIGHT_SUNSHINE` (hours),
`HEATING_/COOLING_DEGREE_DAYS`, `DAYS_WITH_VALID_…` (number of days actually measured that month).

**Daily:** `LOCAL_DATE`, `MEAN_/MIN_/MAX_TEMPERATURE` (°C), `TOTAL_PRECIPITATION`, `TOTAL_RAIN` (mm),
`TOTAL_SNOW` (cm), `SNOW_ON_GROUND` (cm), `SPEED_MAX_GUST` (km/h), `DIRECTION_MAX_GUST` (tens of degrees),
`MIN_REL_HUMIDITY` (%).

**Hourly:** `LOCAL_DATE` + `LOCAL_HOUR`, `TEMP`, `DEW_POINT_TEMP` (°C), `RELATIVE_HUMIDITY` (%),
`PRECIP_AMOUNT` (mm), `STATION_PRESSURE` (kPa), `VISIBILITY` (km), `WIND_SPEED` (km/h),
`WIND_DIRECTION` (tens of degrees), `HUMIDEX`, `WINDCHILL`, `WEATHER_ENG_DESC`/`WEATHER_FRE_DESC`.

**Normals:** `E_NORMAL_ELEMENT_NAME`/`F_NORMAL_ELEMENT_NAME` (what is measured, e.g. "Mean daily temperature deg C"),
`MONTH` (1–12; 13 = whole year), `VALUE`, `PERIOD_BEGIN`–`PERIOD_END` (1981–2010),
`PERCENT_OF_POSSIBLE_OBS` (data completeness).

## Things to know

- **Empty cells mean the value wasn't measured.** Many stations measure only temperature and precipitation.
- **Columns ending in `_FLAG` mark special values**: `E` = estimated, `M` = missing,
  `T` = trace (too small to measure), `A` = accumulated over several days.
- `x` and `y` repeat longitude and latitude in decimal degrees.
- Stations open and close over time. Check `FIRST_DATE`/`LAST_DATE` before comparing stations or years.
