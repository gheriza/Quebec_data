"""Download all Quebec climate data behind changements-climatiques.canada.ca
(Climate Data Extraction Tool -> MSC GeoMet OGC API, api.weather.gc.ca) to CSV.

Usage: python3 fetch_quebec_climate.py [collection ...]
Collections: climate-stations climate-monthly climate-normals climate-daily climate-hourly
Resumable: per-station part files are kept in parts/<collection>/ until merged.
"""
import csv
import io
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

API = "https://api.weather.gc.ca/collections"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIMATE = os.path.join(ROOT, "1_climate")
PARTS = os.path.join(ROOT, "parts")
SUBDIR = {"climate-normals": "normals"}  # everything else goes to measurements/
PAGE = 10000
WORKERS = 8
SORT = {"climate-normals": "ID", "climate-stations": "STN_ID"}


def get(url, tries=8):
    for i in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=300) as r:
                return r.read().decode("utf-8")
        except Exception as e:
            if i == tries - 1:
                raise
            time.sleep(min(60, 2 ** i))
            print(f"  retry {i + 1} {url}: {e}", file=sys.stderr)


def url(coll, fmt, **params):
    params = {"f": fmt, **params}
    return f"{API}/{coll}/items?" + urllib.parse.urlencode(params)


def count(coll, **params):
    return json.loads(get(url(coll, "json", limit=1, **params)))["numberMatched"]


def stations():
    text = get(url("climate-stations", "csv", limit=PAGE, PROV_STATE_TERR_CODE="QC", sortby="STN_ID"))
    rows = list(csv.DictReader(io.StringIO(text)))
    with open(os.path.join(CLIMATE, "stations", "quebec_climate_stations.csv"), "w", newline="", encoding="utf-8") as f:
        f.write(text)
    return sorted({r["CLIMATE_IDENTIFIER"] for r in rows if r["CLIMATE_IDENTIFIER"]})


def fetch_station(coll, cid):
    part = os.path.join(PARTS, coll, f"{cid}.csv")
    if os.path.exists(part):
        return cid, None
    q = {"PROVINCE_CODE": "QC", "CLIMATE_IDENTIFIER": cid, "sortby": SORT.get(coll, "LOCAL_DATE")}
    expected = count(coll, **q)
    header, rows, offset = None, [], 0
    while offset < expected:
        reader = csv.reader(io.StringIO(get(url(coll, "csv", limit=PAGE, offset=offset, **q))))
        page_header = next(reader, None)
        if page_header is None:
            break
        if header is None:
            header = page_header
        elif page_header != header:
            raise RuntimeError(f"{coll}/{cid}: header changed at offset {offset}")
        page = list(reader)
        if not page:
            break
        rows.extend(page)
        offset += len(page)
    if len(rows) != expected:
        raise RuntimeError(f"{coll}/{cid}: got {len(rows)} rows, expected {expected}")
    tmp = part + ".tmp"
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if header:
            w.writerow(header)
        w.writerows(rows)
    os.replace(tmp, part)
    return cid, len(rows)


def merge(coll, cids):
    out = os.path.join(CLIMATE, SUBDIR.get(coll, "measurements"), f"quebec_{coll.replace('-', '_')}.csv")
    header, total = None, 0
    with open(out, "w", newline="", encoding="utf-8") as fo:
        w = csv.writer(fo)
        for cid in cids:
            with open(os.path.join(PARTS, coll, f"{cid}.csv"), newline="", encoding="utf-8") as fi:
                r = csv.reader(fi)
                h = next(r, None)
                if h is None:
                    continue
                if header is None:
                    header = h
                    w.writerow(header)
                if h != header:
                    # Re-map columns by name if a station's export differs in order.
                    idx = [h.index(c) if c in h else None for c in header]
                    for row in r:
                        w.writerow(["" if i is None else row[i] for i in idx])
                        total += 1
                    continue
                for row in r:
                    w.writerow(row)
                    total += 1
    return out, total


def run(coll, cids):
    os.makedirs(os.path.join(PARTS, coll), exist_ok=True)
    expected = count(coll, PROVINCE_CODE="QC")
    print(f"[{coll}] {expected:,} rows for QC across {len(cids)} stations", flush=True)
    done = 0
    with ThreadPoolExecutor(WORKERS) as ex:
        futs = [ex.submit(fetch_station, coll, c) for c in cids]
        for fut in as_completed(futs):
            cid, n = fut.result()
            done += 1
            if n:
                print(f"[{coll}] {done}/{len(cids)} {cid}: {n:,} rows", flush=True)
    out, total = merge(coll, cids)
    status = "OK" if total == expected else f"MISMATCH (API says {expected:,})"
    print(f"[{coll}] wrote {total:,} rows -> {out} {status}", flush=True)


if __name__ == "__main__":
    colls = sys.argv[1:] or ["climate-monthly", "climate-normals", "climate-daily", "climate-hourly"]
    cids = stations()
    print(f"{len(cids)} Quebec stations", flush=True)
    for c in colls:
        run(c, cids)
