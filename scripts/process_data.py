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
PLAYER_FOCUS_NAMES = (
    "LeBron James",
    "Stephen Curry",
    "James Harden",
    "Kevin Durant",
    "Nikola Jokic",
    "Luka Doncic",
    "Anthony Edwards",
    "Kobe Bryant",
    "Tim Duncan",
    "Giannis Antetokounmpo",
    "Shaquille O'Neal",
    "Jayson Tatum",
)
SHOT_TYPE_ORDER = ("2PT Field Goal", "3PT Field Goal")
ZONE_ORDER = (
    "Restricted Area",
    "In The Paint (Non-RA)",
    "Mid-Range",
    "Left Corner 3",
    "Right Corner 3",
    "Above the Break 3",
    "Backcourt",
)


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


def iter_rows(raw_dir: Path):
    csv_files = discover_csv_files(raw_dir)
    if not csv_files:
        raise SystemExit(f"No CSV files found in {raw_dir}. Add season CSVs to data_raw and rerun.")

    for csv_path in csv_files:
        log(f"Reading {csv_path.name} ...")
        with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                yield {(key or "").strip().upper(): (value or "").strip() for key, value in row.items()}


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


def normalize_name(raw: str) -> str:
    return " ".join(raw.strip().lower().split())


def fold_to_half_court(x: float, y: float) -> tuple[float, float]:
    if y > HALF_COURT_LENGTH:
        return (-x, FULL_COURT_LENGTH - y)
    return (x, y)


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def make_counter() -> dict[str, int]:
    return {"attempts": 0, "made": 0, "missed": 0}


def make_distance_counter() -> dict[str, float]:
    return {
        "attempts": 0,
        "made": 0,
        "missed": 0,
        "distanceTotal": 0.0,
        "madeDistanceTotal": 0.0,
        "missedDistanceTotal": 0.0,
    }


def update_counter(counter: dict[str, int], made: bool) -> None:
    counter["attempts"] += 1
    if made:
        counter["made"] += 1
    else:
        counter["missed"] += 1


def update_distance_counter(counter: dict[str, float], shot_distance: float, made: bool) -> None:
    counter["attempts"] += 1
    counter["distanceTotal"] += shot_distance
    if made:
        counter["made"] += 1
        counter["madeDistanceTotal"] += shot_distance
    else:
        counter["missed"] += 1
        counter["missedDistanceTotal"] += shot_distance


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


def finalize_distance_counter(counter: dict[str, float]) -> dict[str, Any]:
    attempts = int(counter["attempts"])
    made = int(counter["made"])
    missed = int(counter["missed"])
    distance_total = counter["distanceTotal"]
    made_distance_total = counter["madeDistanceTotal"]
    missed_distance_total = counter["missedDistanceTotal"]
    return {
        "attempts": attempts,
        "made": made,
        "missed": missed,
        "avgShotDistance": round(distance_total / attempts, 2) if attempts else 0.0,
        "avgMadeShotDistance": round(made_distance_total / made, 2) if made else 0.0,
        "avgMissedShotDistance": round(missed_distance_total / missed, 2) if missed else 0.0,
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

    csv_files = discover_csv_files(raw_dir)
    if not csv_files:
        raise SystemExit(f"No CSV files found in {raw_dir}. Add season CSVs to data_raw and rerun.")

    heatmap_all: dict[tuple[float, float], dict[str, int]] = defaultdict(make_counter)
    heatmap_by_season: dict[str, dict[tuple[float, float], dict[str, int]]] = defaultdict(
        lambda: defaultdict(make_counter)
    )
    monthly_all: dict[str, dict[str, int]] = defaultdict(make_counter)
    monthly_by_season: dict[str, dict[str, dict[str, int]]] = defaultdict(lambda: defaultdict(make_counter))
    distance_all: dict[int, dict[str, int]] = defaultdict(make_counter)
    distance_by_season: dict[str, dict[int, dict[str, int]]] = defaultdict(lambda: defaultdict(make_counter))
    shot_type_by_season: dict[str, dict[str, dict[str, int]]] = defaultdict(lambda: defaultdict(make_counter))
    zone_by_season: dict[str, dict[str, dict[str, int]]] = defaultdict(lambda: defaultdict(make_counter))
    season_distance_all: dict[str, dict[str, float]] = defaultdict(make_distance_counter)
    player_distance_by_player: dict[str, dict[str, dict[str, float]]] = {
        player: defaultdict(make_distance_counter) for player in PLAYER_FOCUS_NAMES
    }
    player_heatmap_all: dict[str, dict[tuple[float, float], dict[str, int]]] = {
        player: defaultdict(make_counter) for player in PLAYER_FOCUS_NAMES
    }
    player_heatmap_by_season: dict[str, dict[str, dict[tuple[float, float], dict[str, int]]]] = {
        player: defaultdict(lambda: defaultdict(make_counter)) for player in PLAYER_FOCUS_NAMES
    }
    player_name_map = {normalize_name(player): player for player in PLAYER_FOCUS_NAMES}

    seasons_set: set[str] = set()
    skipped_rows = 0
    processed_rows = 0

    for row in iter_rows(raw_dir):
        season = row.get("SEASON_2") or row.get("SEASON") or row.get("SEASON_1")
        made = parse_bool(row.get("SHOT_MADE", "") or row.get("SHOT_MADE_FLAG", ""))
        x = parse_float(row.get("LOC_X", ""))
        y = parse_float(row.get("LOC_Y", ""))
        shot_distance = parse_float(row.get("SHOT_DISTANCE", ""))
        game_date = parse_date(row.get("GAME_DATE", "") or row.get("DATE", ""))
        shot_type = row.get("SHOT_TYPE", "")
        basic_zone = row.get("BASIC_ZONE", "")
        player_name = (
            row.get("PLAYER_NAME")
            or row.get("PLAYER")
            or row.get("NAME")
            or row.get("PLAYER_1")
            or ""
        )
        processed_rows += 1

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
        if shot_type in SHOT_TYPE_ORDER:
            update_counter(shot_type_by_season[season][shot_type], made)
        if basic_zone:
            update_counter(zone_by_season[season][basic_zone], made)
        update_distance_counter(season_distance_all[season], shot_distance, made)
        matched_player = player_name_map.get(normalize_name(player_name))
        if matched_player:
            update_distance_counter(player_distance_by_player[matched_player][season], shot_distance, made)
            update_counter(player_heatmap_all[matched_player][(cell_x, cell_y)], made)
            update_counter(player_heatmap_by_season[matched_player][season][(cell_x, cell_y)], made)
        seasons_set.add(season)

    log(f"Loaded {processed_rows:,} shots from {len(csv_files)} CSV files.")

    seasons = sorted(seasons_set, key=season_sort_key)
    generated_at = datetime.now(timezone.utc).isoformat()
    metadata = {
        "dataset": DATASET_LABEL,
        "generatedAt": generated_at,
        "recordCount": processed_rows - skipped_rows,
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

    season_distance_payload = {
        "metadata": metadata,
        "seasons": seasons,
        "all": [
            {
                "season": season,
                **finalize_distance_counter(season_distance_all[season]),
            }
            for season in seasons
        ],
    }

    player_distance_payload = {
        "metadata": metadata,
        "seasons": seasons,
        "players": [
            {
                "player": player,
                "firstSeason": next(
                    (season for season in seasons if season in player_distance_by_player[player]),
                    None,
                ),
                "seasons": [
                    {
                        "season": season,
                        **finalize_distance_counter(player_distance_by_player[player][season]),
                    }
                    for season in seasons
                    if season in player_distance_by_player[player]
                ],
            }
            for player in PLAYER_FOCUS_NAMES
        ],
    }

    player_heatmap_payload = {
        "metadata": {
            **metadata,
            "cellSize": HEATMAP_CELL_SIZE,
            "fullCourtLength": FULL_COURT_LENGTH,
            "halfCourtLength": HALF_COURT_LENGTH,
            "halfCourtWidth": HALF_COURT_WIDTH,
        },
        "seasons": seasons,
        "players": [
            {
                "player": player,
                "all": [
                    {
                        "x": key[0],
                        "y": key[1],
                        **finalize_counter(player_heatmap_all[player][key]),
                    }
                    for key in sorted(player_heatmap_all[player])
                ],
                "bySeason": {
                    season: [
                        {
                            "x": key[0],
                            "y": key[1],
                            **finalize_counter(player_heatmap_by_season[player][season][key]),
                        }
                        for key in sorted(player_heatmap_by_season[player][season])
                    ]
                    for season in seasons
                    if season in player_heatmap_by_season[player]
                },
            }
            for player in PLAYER_FOCUS_NAMES
        ],
    }

    shot_type_payload = {
        "metadata": metadata,
        "seasons": seasons,
        "all": [
            {
                "season": season,
                "totalAttempts": sum(
                    shot_type_by_season[season][shot_type]["attempts"]
                    for shot_type in SHOT_TYPE_ORDER
                    if shot_type in shot_type_by_season[season]
                ),
                "shotTypes": [
                    {
                        "shotType": shot_type,
                        **finalize_counter(shot_type_by_season[season][shot_type]),
                        "share": round(
                            shot_type_by_season[season][shot_type]["attempts"]
                            / max(
                                1,
                                sum(
                                    shot_type_by_season[season][candidate]["attempts"]
                                    for candidate in SHOT_TYPE_ORDER
                                    if candidate in shot_type_by_season[season]
                                ),
                            ),
                            4,
                        ),
                    }
                    for shot_type in SHOT_TYPE_ORDER
                    if shot_type in shot_type_by_season[season]
                ],
            }
            for season in seasons
        ],
    }

    zone_names = [
        zone
        for zone in ZONE_ORDER
        if any(zone in zone_by_season[season] for season in seasons)
    ] + sorted(
        {
            zone
            for season in seasons
            for zone in zone_by_season[season]
            if zone not in ZONE_ORDER
        }
    )

    zone_trend_payload = {
        "metadata": metadata,
        "seasons": seasons,
        "zones": zone_names,
        "all": [
            {
                "season": season,
                "totalAttempts": sum(counter["attempts"] for counter in zone_by_season[season].values()),
                "zones": [
                    {
                        "zone": zone,
                        **finalize_counter(zone_by_season[season][zone]),
                        "share": round(
                            zone_by_season[season][zone]["attempts"]
                            / max(1, sum(counter["attempts"] for counter in zone_by_season[season].values())),
                            4,
                        ),
                    }
                    for zone in zone_names
                    if zone in zone_by_season[season]
                ],
            }
            for season in seasons
        ],
    }

    write_json(out_dir, "heatmap.json", heatmap_payload)
    write_json(out_dir, "monthly-trends.json", monthly_payload)
    write_json(out_dir, "distance-profile.json", distance_payload)
    write_json(out_dir, "season-distance-trend.json", season_distance_payload)
    write_json(out_dir, "player-distance-trend.json", player_distance_payload)
    write_json(out_dir, "player-heatmap.json", player_heatmap_payload)
    write_json(out_dir, "shot-type-trend.json", shot_type_payload)
    write_json(out_dir, "zone-trend.json", zone_trend_payload)

    log("")
    log("Data pipeline complete.")
    log(f"Processed shots: {metadata['recordCount']:,}")
    log(f"Skipped rows: {skipped_rows:,}")
    log(f"Seasons available: {len(seasons)}")


if __name__ == "__main__":
    main()
