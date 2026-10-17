"""Convert the Données Québec dataset "Données sur les perturbations naturelles -
Insecte : Livrée des forêts" (shapefiles + GeoTIFF) to CSV files.

Usage: python3 convert_livree_forets.py <folder with unzipped files> <output folder>
Needs: pyshp, shapely, pyproj, rasterio, numpy
"""
import csv
import glob
import os
import sys
from collections import Counter

import numpy as np
import rasterio
import shapefile
from pyproj import Transformer
from shapely.geometry import LinearRing, Polygon, shape
from shapely.ops import unary_union

SRC, OUT = sys.argv[1], sys.argv[2]


def read_shp(path):
    for enc in ("utf-8", "latin-1"):
        try:
            r = shapefile.Reader(path, encoding=enc)
            recs = r.shapeRecords()
            return [f[0] for f in r.fields[1:]], recs
        except shapefile.ShapefileException:
            continue
    raise RuntimeError(f"cannot decode {path}")


def to_geom(shp, stats):
    if not shp.points:
        return None
    try:
        return shape(shp.__geo_interface__)
    except ValueError:
        # Degenerate rings (< 4 points): rebuild from the valid rings only.
        # Shapefile outer rings are clockwise, holes counter-clockwise.
        stats["repaired"] += 1
        bounds = list(shp.parts) + [len(shp.points)]
        outers, holes = [], []
        for s, e in zip(bounds[:-1], bounds[1:]):
            ring = shp.points[s:e]
            if len(ring) < 4:
                continue
            poly = Polygon(ring).buffer(0)
            (holes if LinearRing(ring).is_ccw else outers).append(poly)
        if not outers:
            stats["dropped"] += 1
            return None
        return unary_union(outers).difference(unary_union(holes)) if holes else unary_union(outers)


def shp_to_csv(path, out):
    fields, recs = read_shp(path)
    stats = Counter()
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(fields + ["centroid_lon", "centroid_lat", "geometry_wkt"])
        for sr in recs:
            vals = [v.strip() if isinstance(v, str) else v for v in sr.record]
            geom = to_geom(sr.shape, stats)
            if geom is None:
                w.writerow(vals + ["", "", ""])
                continue
            c = geom.representative_point() if not geom.is_valid else geom.centroid
            w.writerow(vals + [round(c.x, 6), round(c.y, 6), geom.wkt])
    extra = f" ({stats['repaired']} malformed geometries repaired, {stats['dropped']} without valid rings)" if stats else ""
    print(f"{os.path.basename(out)}: {len(recs):,} polygons{extra}")


def raster_to_csv(tif, out):
    """Write one row per coloured (non-transparent) pixel. The file ships no
    legend for its colours, so the raw RGB values are kept as-is."""
    with rasterio.open(tif) as r:
        a = r.read()
        rows, cols = np.nonzero(a[3] > 0) if r.count == 4 else np.nonzero(a.any(0))
        xs, ys = rasterio.transform.xy(r.transform, rows, cols)
        to_ll = Transformer.from_crs(r.crs, "EPSG:4269", always_xy=True)
        lon, lat = to_ll.transform(np.asarray(xs), np.asarray(ys))
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["x_lambert_epsg32198", "y_lambert_epsg32198", "lon", "lat", "R", "G", "B"])
        for k, (i, j) in enumerate(zip(rows, cols)):
            w.writerow([round(xs[k], 2), round(ys[k], 2), round(lon[k], 6), round(lat[k], 6),
                        int(a[0, i, j]), int(a[1, i, j]), int(a[2, i, j])])
    print(f"{os.path.basename(out)}: {len(rows):,} pixels (30 m)")


os.makedirs(OUT, exist_ok=True)
for shp in sorted(glob.glob(os.path.join(SRC, "**", "*.shp"), recursive=True)):
    name = os.path.splitext(os.path.basename(shp))[0].replace(" ", "_")
    shp_to_csv(shp, os.path.join(OUT, f"{name}.csv"))

for tif in sorted(glob.glob(os.path.join(SRC, "**", "*.tif"), recursive=True)):
    name = os.path.splitext(os.path.basename(tif))[0]
    raster_to_csv(tif, os.path.join(OUT, f"{name}_pixels.csv"))
