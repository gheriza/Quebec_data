"""Extract Hansen Global Forest Change 2025 v1.13 (UMD) for Quebec into CSV files.

Inputs : raw 10x10 degree tiles (datamask, treecover2000, lossyear, gain) in
         <out>/raw_tiles, and Quebec administrative regions as GeoJSON.
Outputs: <out>/quebec_forest_by_region.csv        one row per region (+ Quebec total)
         <out>/quebec_forest_loss_by_region_year.csv  region x year 2001-2025
         <out>/quebec_forest_grid_0.01deg.csv     one row per 0.01 degree cell (~1 km)
         <out>/quebec_forest_loss_pixels.csv      one row per 30 m pixel with loss

Usage: python3 hansen_quebec.py <regions.geojson> <out dir>
Forest = tree canopy cover in 2000 > 30 % (Global Forest Watch convention).
"""
import csv
import glob
import json
import math
import os
import sys

import numpy as np
import rasterio
from rasterio.features import rasterize
from rasterio.windows import Window
from shapely.geometry import box, shape

REGIONS, OUT = sys.argv[1], sys.argv[2]
RAW = os.path.join(OUT, "raw_tiles")
VERSION = "GFC-2025-v1.13"
TILES = ["50N_080W", "50N_070W", "50N_060W", "60N_080W", "60N_070W", "60N_060W",
         "70N_080W", "70N_070W", "70N_060W"]
RES = 0.00025          # degrees per pixel
CELL = 40              # pixels per grid cell -> 0.01 degree
BLOCK = 800            # rows per processing block (multiple of CELL)
NY = 26                # loss year codes 0 (no loss) .. 25 (2025)
THRESH = 30
R_EARTH = 6371007.2    # authalic radius (m)

# Regions: index 1..N. The disputed "Tracé de 1927" polygon is burned first so
# that the regular regions win wherever the two overlap.
feats = json.load(open(REGIONS, encoding="utf-8"))["features"]
feats.sort(key=lambda f: "1927" not in f["properties"]["RES_NM_REG"])
regions = [(f["properties"]["RES_CO_REG"], f["properties"]["RES_NM_REG"]) for f in feats]
geoms = [shape(f["geometry"]).buffer(0) for f in feats]
N = len(regions) + 1
b = np.array([g.bounds for g in geoms])
qc_bounds = box(b[:, 0].min(), b[:, 1].min(), b[:, 2].max(), b[:, 3].max())

reg_land = np.zeros(N)
reg_water = np.zeros(N)
reg_forest = np.zeros(N)
reg_gain = np.zeros(N)
reg_loss30 = np.zeros(N * NY)
reg_lossall = np.zeros(N * NY)

os.makedirs(OUT, exist_ok=True)
names = {i + 1: r for i, r in enumerate(regions)}
grid_f = open(os.path.join(OUT, "quebec_forest_grid_0.01deg.csv"), "w", newline="", encoding="utf-8")
grid = csv.writer(grid_f)
grid.writerow(["cell_lon", "cell_lat", "region_code", "region_name", "land_ha", "forest2000_ha",
               "mean_treecover2000_pct", "gain_ha_2000_2020"]
              + [f"loss_ha_{2000 + y}" for y in range(1, NY)] + ["loss_ha_total"])
pix_f = open(os.path.join(OUT, "quebec_forest_loss_pixels.csv"), "w", newline="", encoding="utf-8")
pix_f.write("lon,lat,loss_year,treecover2000_pct,region_code\n")
n_pix = 0


def tile_path(layer, t):
    return os.path.join(RAW, f"Hansen_{VERSION}_{layer}_{t}.tif")


for t in TILES:
    srcs = {l: rasterio.open(tile_path(l, t)) for l in ("datamask", "treecover2000", "gain")}
    ly_path = tile_path("lossyear", t)
    ly_src = rasterio.open(ly_path) if os.path.exists(ly_path) else None
    ref = srcs["datamask"]
    W, H = ref.width, ref.height
    for r0 in range(0, H, BLOCK):
        win = Window(0, r0, W, BLOCK)
        wt = ref.window_transform(win)
        west, north = wt.c, wt.f
        bb = box(west, north - BLOCK * RES, west + W * RES, north)
        if not bb.intersects(qc_bounds):
            continue
        shapes = [(g, i + 1) for i, g in enumerate(geoms) if g.intersects(bb)]
        if not shapes:
            continue
        reg = rasterize(shapes, out_shape=(BLOCK, W), transform=wt, fill=0, dtype="uint8")
        if not reg.any():
            continue
        dm = srcs["datamask"].read(1, window=win)
        tc = srcs["treecover2000"].read(1, window=win)
        gn = srcs["gain"].read(1, window=win)
        ly = ly_src.read(1, window=win) if ly_src else np.zeros_like(dm)

        lat = north - (np.arange(BLOCK) + 0.5) * RES
        area_row = (RES * math.pi / 180 * R_EARTH) ** 2 * np.cos(np.radians(lat)) / 1e4  # ha
        area = np.broadcast_to(area_row[:, None], (BLOCK, W)).astype(np.float64)

        q = reg > 0
        land = q & (dm == 1)
        forest = land & (tc > THRESH)

        # Region totals.
        rl = reg.ravel()
        a = area.ravel()
        reg_land += np.bincount(rl, a * land.ravel(), N)
        reg_water += np.bincount(rl, a * (q & (dm == 2)).ravel(), N)
        reg_forest += np.bincount(rl, a * forest.ravel(), N)
        reg_gain += np.bincount(rl, a * (land & (gn == 1)).ravel(), N)
        idx = rl.astype(np.int64) * NY + ly.ravel()
        reg_loss30 += np.bincount(idx, a * forest.ravel(), N * NY)
        reg_lossall += np.bincount(idx, a * land.ravel(), N * NY)

        # 0.01 degree grid.
        ncr, ncc = BLOCK // CELL, W // CELL
        cell = ((np.arange(BLOCK) // CELL)[:, None] * ncc + (np.arange(W) // CELL)[None, :]).ravel()
        nc = ncr * ncc
        c_land = np.bincount(cell, a * land.ravel(), nc)
        keep = np.nonzero(c_land > 0)[0]
        if keep.size:
            c_forest = np.bincount(cell, a * forest.ravel(), nc)
            c_tc = np.bincount(cell, a * (tc.ravel() * land.ravel()), nc)
            c_gain = np.bincount(cell, a * (land & (gn == 1)).ravel(), nc)
            c_loss = np.bincount(cell * NY + ly.ravel(), a * forest.ravel(), nc * NY).reshape(nc, NY)
            # Region of each cell = region holding the most pixels in it.
            c_reg = np.bincount(cell * N + rl, minlength=nc * N).reshape(nc, N)
            c_reg[:, 0] = 0
            c_reg = c_reg.argmax(1)
            for k in keep:
                cr, cc = divmod(k, ncc)
                code, name = names[c_reg[k]]
                losses = c_loss[k, 1:]
                grid.writerow([round(west + (cc + 0.5) * CELL * RES, 3),
                               round(north - (cr + 0.5) * CELL * RES, 3), code, name,
                               round(c_land[k], 2), round(c_forest[k], 2),
                               round(c_tc[k] / c_land[k], 1), round(c_gain[k], 2)]
                              + [round(x, 2) for x in losses] + [round(losses.sum(), 2)])

        # Loss pixels (any canopy cover, on land, inside Quebec).
        rr, cc = np.nonzero(land & (ly > 0))
        if rr.size:
            out = np.column_stack([west + (cc + 0.5) * RES, north - (rr + 0.5) * RES,
                                   2000 + ly[rr, cc].astype(int), tc[rr, cc], reg[rr, cc]])
            codes = np.array([names[i][0] for i in range(1, N)])
            lines = [f"{x:.6f},{y:.6f},{int(yr)},{int(c)},{codes[int(r) - 1]}\n"
                     for x, y, yr, c, r in out]
            pix_f.writelines(lines)
            n_pix += rr.size
        print(f"{t} rows {r0}-{r0 + BLOCK}: loss pixels so far {n_pix:,}", flush=True)
    for s in srcs.values():
        s.close()
    if ly_src:
        ly_src.close()

grid_f.close()
pix_f.close()

loss30 = reg_loss30.reshape(N, NY)
lossall = reg_lossall.reshape(N, NY)
with open(os.path.join(OUT, "quebec_forest_by_region.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["region_code", "region_name", "land_ha", "water_ha", "forest2000_ha",
                "gain_ha_2000_2020", "loss_ha_2001_2025_forest", "loss_ha_2001_2025_any_canopy",
                "loss_pct_of_forest2000"])
    rows = []
    for i in range(1, N):
        code, name = names[i]
        rows.append([code, name, reg_land[i], reg_water[i], reg_forest[i], reg_gain[i],
                     loss30[i, 1:].sum(), lossall[i, 1:].sum()])
    rows.sort(key=lambda r: (r[0], r[1]))
    tot = ["", "QUÉBEC (total)"] + [sum(r[k] for r in rows) for k in range(2, 8)]
    for r in rows + [tot]:
        pct = 100 * r[6] / r[4] if r[4] else 0
        w.writerow(r[:2] + [round(x, 2) for x in r[2:]] + [round(pct, 3)])

with open(os.path.join(OUT, "quebec_forest_loss_by_region_year.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["region_code", "region_name", "year", "loss_ha_forest", "loss_ha_any_canopy"])
    for i in sorted(range(1, N), key=lambda i: names[i]):
        for y in range(1, NY):
            w.writerow([*names[i], 2000 + y, round(loss30[i, y], 2), round(lossall[i, y], 2)])
    for y in range(1, NY):
        w.writerow(["", "QUÉBEC (total)", 2000 + y, round(loss30[1:, y].sum(), 2), round(lossall[1:, y].sum(), 2)])

print(f"done: {n_pix:,} loss pixels")
