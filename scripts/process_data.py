#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT_DIR / "data_raw"
OUT_DIR = ROOT_DIR / "src" / "lib" / "data"

FULL_COURT_LENGTH = 94.0
HALF_COURT_LENGTH = FULL_COURT_LENGTH / 2
HALF_COURT_WIDTH = 25.0
HEATMAP_CELL_SIZE = 2.0
DISTANCE_BUCKET_SIZE = 2
LONG_DISTANCE_BUCKET = 40
DATASET_LABEL = "Local data_raw CSV files"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Aggregate NBA shot CSVs from data_raw into frontend-friendly JSON."
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=RAW_DIR,
        help="Directory containing the raw season CSV files.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=OUT_DIR,
        help="Directory where aggregated JSON output should be written.",
    )
    return parser.parse_args()


def log(message: str) -> None:
    print(message)


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def discover_csv_files(raw_dir: Path) -> list[Path]:
    return sorted(raw_dir.glob("*.csv"))


def load_rows(raw_dir: Path) -> list[dict[str, str]]:
    csv_files = discover_csv_files(raw_dir)
    if not csv_files:
        raise SystemExit(f"No CSV files found in {raw_dir}. Add season CSVs to data_raw and rerun.")

    rows: list[dict[str, str]] = []
    for csv_path in csv_files:
        log(f"Reading {csv_path.name} ...")
        with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                rows.append({(key or "").strip().upper(): (value or "").strip() for key, value in row.items()})

    log(f"Loaded {len(rows):,} shots from {len(csv_files)} CSV files.")
    return rows


def parse_bool(raw: str) -> bool | None:
    value = raw.strip().lower()
    if value in {"true", "1", "made", "made shot"}:
        return True
    if value in {"false", "0", "missed", "missed shot"}:
        return False
    return None


def parse_float(raw: str) -> float | None:
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None


def parse_date(raw: str) -> datetime | None:
    for fmt in ("%m-%d-%Y", "%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    return None


def fold_to_half_court(x: float, y: float) -> tuple[float, float]:
    if y > HALF_COURT_LENGTH:
        return (-x, FULL_COURT_LENGTH - y)
    return (x, y)


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def make_counter() -> dict[str, int]:
    return {"attempts": 0, "made": 0, "missed": 0}


def update_counter(counter: dict[str, int], made: bool) -> None:
    counter["attempts"] += 1
    if made:
        counter["made"] += 1
    else:
        counter["missed"] += 1


def finalize_counter(counter: dict[str, int]) -> dict[str, Any]:
    attempts = counter["attempts"]
    made = counter["made"]
    fg_pct = round(made / attempts, 4) if attempts else 0.0
    return {
        "attempts": attempts,
        "made": made,
        "missed": counter["missed"],
        "fgPct": fg_pct,
    }


def season_sort_key(season: str) -> tuple[int, str]:
    prefix = season.split("-")[0]
    try:
        return (int(prefix), season)
    except ValueError:
        return (9999, season)


def build_collection(
    all_map: dict[Any, dict[str, int]],
    by_season_map: dict[str, dict[Any, dict[str, int]]],
    formatter: Callable[[Any, dict[str, int]], dict[str, Any]],
    seasons: list[str],
) -> dict[str, Any]:
    return {
        "seasons": seasons,
        "all": [formatter(key, all_map[key]) for key in sorted(all_map)],
        "bySeason": {
            season: [formatter(key, by_season_map[season][key]) for key in sorted(by_season_map[season])]
            for season in seasons
        },
    }


def write_json(out_dir: Path, filename: str, payload: dict[str, Any]) -> None:
    ensure_dir(out_dir)
    target = out_dir / filename
    target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    log(f"Wrote {target.relative_to(ROOT_DIR)}")


def main() -> None:
    args = parse_args()
    raw_dir = args.raw_dir.resolve()
    out_dir = args.out_dir.resolve()

    rows = load_rows(raw_dir)

    heatmap_all: dict[tuple[float, float], dict[str, int]] = defaultdict(make_counter)
    heatmap_by_season: dict[str, dict[tuple[float, float], dict[str, int]]] = defaultdict(
        lambda: defaultdict(make_counter)
    )
    monthly_all: dict[str, dict[str, int]] = defaultdict(make_counter)
    monthly_by_season: dict[str, dict[str, dict[str, int]]] = defaultdict(lambda: defaultdict(make_counter))
    distance_all: dict[int, dict[str, int]] = defaultdict(make_counter)
    distance_by_season: dict[str, dict[int, dict[str, int]]] = defaultdict(lambda: defaultdict(make_counter))

    seasons_set: set[str] = set()
    skipped_rows = 0

    for row in rows:
        season = row.get("SEASON_2") or row.get("SEASON") or row.get("SEASON_1")
        made = parse_bool(row.get("SHOT_MADE", "") or row.get("SHOT_MADE_FLAG", ""))
        x = parse_float(row.get("LOC_X", ""))
        y = parse_float(row.get("LOC_Y", ""))
        shot_distance = parse_float(row.get("SHOT_DISTANCE", ""))
        game_date = parse_date(row.get("GAME_DATE", "") or row.get("DATE", ""))

        if not season or made is None or x is None or y is None or shot_distance is None or game_date is None:
            skipped_rows += 1
            continue

        folded_x, folded_y = fold_to_half_court(x, y)
        folded_x = clamp(folded_x, -HALF_COURT_WIDTH, HALF_COURT_WIDTH)
        folded_y = clamp(folded_y, 0.0, HALF_COURT_LENGTH)

        cell_x = round(math.floor(folded_x / HEATMAP_CELL_SIZE) * HEATMAP_CELL_SIZE, 2)
        cell_y = round(math.floor(folded_y / HEATMAP_CELL_SIZE) * HEATMAP_CELL_SIZE, 2)
        month = game_date.strftime("%Y-%m")
        distance_bucket = min(
            int(math.floor(shot_distance / DISTANCE_BUCKET_SIZE) * DISTANCE_BUCKET_SIZE),
            LONG_DISTANCE_BUCKET,
        )

        update_counter(heatmap_all[(cell_x, cell_y)], made)
        update_counter(heatmap_by_season[season][(cell_x, cell_y)], made)
        update_counter(monthly_all[month], made)
        update_counter(monthly_by_season[season][month], made)
        update_counter(distance_all[distance_bucket], made)
        update_counter(distance_by_season[season][distance_bucket], made)
        seasons_set.add(season)

    seasons = sorted(seasons_set, key=season_sort_key)
    generated_at = datetime.now(timezone.utc).isoformat()
    metadata = {
        "dataset": DATASET_LABEL,
        "generatedAt": generated_at,
        "recordCount": len(rows) - skipped_rows,
        "skippedRows": skipped_rows,
    }

    heatmap_payload = {
        "metadata": {
            **metadata,
            "cellSize": HEATMAP_CELL_SIZE,
            "fullCourtLength": FULL_COURT_LENGTH,
            "halfCourtLength": HALF_COURT_LENGTH,
            "halfCourtWidth": HALF_COURT_WIDTH,
        },
        **build_collection(
            heatmap_all,
            heatmap_by_season,
            lambda key, counter: {
                "x": key[0],
                "y": key[1],
                **finalize_counter(counter),
            },
            seasons,
        ),
    }

    monthly_payload = {
        "metadata": metadata,
        **build_collection(
            monthly_all,
            monthly_by_season,
            lambda key, counter: {
                "month": key,
                **finalize_counter(counter),
            },
            seasons,
        ),
    }

    distance_payload = {
        "metadata": {
            **metadata,
            "bucketSize": DISTANCE_BUCKET_SIZE,
            "longDistanceBucket": LONG_DISTANCE_BUCKET,
        },
        **build_collection(
            distance_all,
            distance_by_season,
            lambda key, counter: {
                "distanceBucket": key,
                **finalize_counter(counter),
            },
            seasons,
        ),
    }

    write_json(out_dir, "heatmap.json", heatmap_payload)
    write_json(out_dir, "monthly-trends.json", monthly_payload)
    write_json(out_dir, "distance-profile.json", distance_payload)

    log("")
    log("Data pipeline complete.")
    log(f"Processed shots: {metadata['recordCount']:,}")
    log(f"Skipped rows: {skipped_rows:,}")
    log(f"Seasons available: {len(seasons)}")


if __name__ == "__main__":
    main()
