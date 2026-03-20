#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import io
import zipfile
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT_DIR / "data_raw"
DEFAULT_DATASET = "mexwell/nba-shots"
DOWNLOAD_URL_TEMPLATE = "https://www.kaggle.com/api/v1/datasets/download/{dataset}"

KAGGLE_USERNAME = ""
KAGGLE_API_KEY = ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download the Kaggle dataset zip and extract CSVs into data_raw."
    )
    parser.add_argument(
        "--dataset",
        default=DEFAULT_DATASET,
        help="Kaggle dataset slug in owner/dataset format.",
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=RAW_DIR,
        help="Directory where extracted CSV files should be written.",
    )
    return parser.parse_args()


def ensure_credentials() -> tuple[str, str]:
    username = KAGGLE_USERNAME.strip()
    api_key = KAGGLE_API_KEY.strip()

    if not username or not api_key:
        raise SystemExit(
            "Set KAGGLE_USERNAME and KAGGLE_API_KEY near the top of scripts/download_data.py before running."
        )

    return username, api_key


def build_request(dataset: str, username: str, api_key: str) -> Request:
    token = base64.b64encode(f"{username}:{api_key}".encode("utf-8")).decode("ascii")
    return Request(
        DOWNLOAD_URL_TEMPLATE.format(dataset=dataset),
        headers={
            "Authorization": f"Basic {token}",
            "User-Agent": "nba-shot-evolution-data-downloader",
        },
    )


def download_zip(dataset: str, username: str, api_key: str) -> bytes:
    request = build_request(dataset, username, api_key)

    try:
        with urlopen(request) as response:
            return response.read()
    except HTTPError as exc:
        if exc.code in {401, 403}:
            raise SystemExit("Kaggle rejected the credentials. Double-check KAGGLE_USERNAME and KAGGLE_API_KEY.") from exc
        if exc.code == 404:
            raise SystemExit(f"Dataset '{dataset}' was not found on Kaggle.") from exc
        raise SystemExit(f"Kaggle download failed with HTTP {exc.code}.") from exc
    except URLError as exc:
        raise SystemExit(f"Unable to reach Kaggle: {exc.reason}") from exc


def extract_csvs(zip_bytes: bytes, raw_dir: Path) -> list[Path]:
    raw_dir.mkdir(parents=True, exist_ok=True)
    extracted: list[Path] = []

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        csv_members = [member for member in archive.namelist() if member.lower().endswith(".csv")]
        if not csv_members:
            raise SystemExit("The downloaded archive did not contain any CSV files.")

        for member in csv_members:
            target = raw_dir / Path(member).name
            target.write_bytes(archive.read(member))
            extracted.append(target)

    return extracted


def main() -> None:
    args = parse_args()
    username, api_key = ensure_credentials()

    print(f"Downloading Kaggle dataset '{args.dataset}' ...")
    zip_bytes = download_zip(args.dataset, username, api_key)

    extracted_files = extract_csvs(zip_bytes, args.raw_dir.resolve())
    print(f"Extracted {len(extracted_files)} CSV file(s) into {args.raw_dir.resolve()}")
    for path in extracted_files:
        print(f" - {path.name}")


if __name__ == "__main__":
    main()
