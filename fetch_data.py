#!/usr/bin/env python3
"""Build docs/data.json for the China training-compute plot.

Source 1 (primary): Epoch AI's public notable-models data (CC-BY)
  https://epoch.ai/data/notable_ai_models.csv
  Filtered to China-based organizations, models published 2023-01-01 or later,
  with a training-compute (FLOP) estimate.

Source 2 (augmentation): data/additions_*.json — hand-researched models Epoch
  is missing, contributed by the research team. See data/SCHEMA.md.

Each plotted point carries a `source` field ("Epoch" | "Team research") so the
provenance is visible on hover. Stdlib only. Run: python3 fetch_data.py
"""
import csv
import glob
import io
import json
import re
import sys
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

CSV_URL = "https://epoch.ai/data/notable_ai_models.csv"
ECI_URL = "https://epoch.ai/data/benchmarked_models.csv"
ROOT = Path(__file__).parent
OUT = ROOT / "docs" / "data.json"
CSV_CACHE = ROOT / "data" / "epoch_notable_ai_models.csv"
ECI_CACHE = ROOT / "data" / "epoch_benchmarked_models.csv"
MIN_DATE = "2023-01-01"


def fetch_csv(url: str, cache: Path) -> str:
    """Fetch a CSV, falling back to the local cache on network failure."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "china-training-compute/1.0"})
        with urllib.request.urlopen(req, timeout=90) as r:
            text = r.read().decode("utf-8")
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(text)
        return text
    except Exception as e:  # noqa: BLE001
        if cache.exists():
            print(f"WARN: fetch {url} failed ({e}); using cached copy", file=sys.stderr)
            return cache.read_text()
        raise


def fetch_epoch_csv() -> str:
    return fetch_csv(CSV_URL, CSV_CACHE)


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def _parse_date(s: str):
    try:
        return date.fromisoformat((s or "")[:10])
    except ValueError:
        return None


def eci_index() -> dict:
    """normalized model name -> list of {date, eci, ci_low, ci_high} from benchmarked_models.csv.

    ECI (Epoch Capabilities Index) is only computed for benchmarked models, so most
    plotted models will have no entry — that is expected.
    """
    rows = list(csv.DictReader(io.StringIO(fetch_csv(ECI_URL, ECI_CACHE))))
    idx = {}
    for r in rows:
        eci = r.get("eci")
        if not eci:
            continue
        try:
            entry = {
                "date": (r.get("Version release date") or "")[:10],
                "eci": float(eci),
                "ci_low": float(r["eci_ci_low"]) if r.get("eci_ci_low") else None,
                "ci_high": float(r["eci_ci_high"]) if r.get("eci_ci_high") else None,
            }
        except ValueError:
            continue
        for key in (r.get("Display name"), r.get("Model")):
            if key:
                idx.setdefault(_norm(key), []).append(entry)
    return idx


def attach_eci(model: dict, idx: dict) -> None:
    """Attach ECI to a model by name match; on multiple matches pick the nearest release date."""
    cands = idx.get(_norm(model["model"]))
    if not cands:
        return
    md = _parse_date(model["date"])
    def dist(c):
        cd = _parse_date(c["date"])
        return abs((cd - md).days) if (cd and md) else 10**6
    best = min(cands, key=dist)
    model["eci"] = round(best["eci"], 1)
    if best["ci_low"] is not None and best["ci_high"] is not None:
        model["eci_ci"] = [round(best["ci_low"], 1), round(best["ci_high"], 1)]


def is_china(row: dict) -> bool:
    return "china" in (row.get("Country (of organization)") or "").lower()


def to_float(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def short_org(org: str) -> str:
    """Collapse multi-affiliation strings to the lead organization for coloring."""
    if not org:
        return "Unknown"
    lead = org.split(",")[0].strip()
    # Normalize a few names for consistent coloring across sources
    norm = {
        "Z.ai (Zhipu AI)": "Zhipu AI",
        "Zhipu": "Zhipu AI",
        "Z.ai": "Zhipu AI",
        "Huawei Noah's Ark Lab": "Huawei",
        "Kunlun Inc.": "Kunlun (Skywork)",
        "Kunlun (Skywork AI)": "Kunlun (Skywork)",
        "Kunlun": "Kunlun (Skywork)",
        "Xiaomi Corp": "Xiaomi",
        "Meituan Inc": "Meituan",
        "Moonshot": "Moonshot AI",
        "01.AI": "01.AI",
        "Shanghai AI Laboratory": "Shanghai AI Lab",
    }
    return norm.get(lead, lead)


def epoch_models() -> list:
    rows = list(csv.DictReader(io.StringIO(fetch_epoch_csv())))
    out = []
    for r in rows:
        date = (r.get("Publication date") or "").strip()
        if not is_china(r) or date < MIN_DATE:
            continue
        compute = to_float(r.get("Training compute (FLOP)"))
        if compute is None:
            continue  # plot only models with a compute estimate
        out.append(
            {
                "model": r.get("Model") or "Unknown",
                "org": short_org(r.get("Organization")),
                "org_full": r.get("Organization") or "Unknown",
                "date": date,
                "compute": compute,
                "params": (r.get("Parameters") or "").strip() or None,
                "domain": (r.get("Domain") or "").strip() or None,
                "compute_basis": (r.get("Training compute notes") or "").strip() or None,
                "confidence": (r.get("Confidence") or "").strip() or None,
                "source": "Epoch",
                "link": (r.get("Link") or "").strip() or None,
            }
        )
    return out


def addition_models() -> list:
    out = []
    for path in sorted(glob.glob(str(ROOT / "data" / "additions_*.json"))):
        try:
            items = json.loads(Path(path).read_text())
        except Exception as e:  # noqa: BLE001
            print(f"WARN: could not parse {path}: {e}", file=sys.stderr)
            continue
        for it in items:
            compute = it.get("training_compute_flop")
            date = (it.get("publication_date") or "").strip()
            if compute is None or not date or date < MIN_DATE:
                continue
            urls = it.get("source_urls") or []
            out.append(
                {
                    "model": it.get("model") or "Unknown",
                    "org": short_org(it.get("organization")),
                    "org_full": it.get("organization") or "Unknown",
                    "date": date,
                    "compute": float(compute),
                    "params": it.get("parameters"),
                    "domain": None,
                    "compute_basis": it.get("compute_basis"),
                    "confidence": it.get("confidence"),
                    "source": "Team research",
                    "link": urls[0] if urls else None,
                }
            )
    return out


def main() -> None:
    models = epoch_models()
    epoch_names = {(m["model"], m["org"]) for m in models}
    n_epoch = len(models)

    added = 0
    for m in addition_models():
        if (m["model"], m["org"]) in epoch_names:
            continue  # don't duplicate an Epoch model
        models.append(m)
        added += 1

    # Join Epoch Capabilities Index (ECI) where the model is benchmarked
    idx = eci_index()
    for m in models:
        attach_eci(m, idx)
    n_eci = sum(1 for m in models if "eci" in m)

    models.sort(key=lambda m: m["date"])
    orgs = sorted({m["org"] for m in models})
    payload = {
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "n_epoch": n_epoch,
        "n_team": added,
        "n_eci": n_eci,
        "orgs": orgs,
        "models": models,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, separators=(",", ":")))
    print(
        f"wrote {OUT}: {len(models)} models "
        f"({n_epoch} from Epoch, {added} from team research), {len(orgs)} orgs, "
        f"{n_eci} with ECI"
    )
    if len(models) < 40:
        print("WARNING: suspiciously few models — check upstream schema", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
