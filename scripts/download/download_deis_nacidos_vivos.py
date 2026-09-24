#!/usr/bin/env python3
"""Download the DEIS live-birth files without modifying existing raw data."""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "data" / "source-catalog.csv"
RAW_DIR = ROOT / "data" / "raw"
LOCAL_MANIFEST = RAW_DIR / "download-manifest.csv"
CHUNK_SIZE = 1024 * 1024


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def looks_like_html(path: Path) -> bool:
    with path.open("rb") as stream:
        prefix = stream.read(512).lstrip().lower()
    return prefix.startswith(b"<!doctype html") or prefix.startswith(b"<html")


def load_catalog() -> list[dict[str, str]]:
    with CATALOG.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    required = {"resource_id", "year", "kind", "url", "filename", "bytes", "sha256"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError(f"Unexpected catalog columns in {CATALOG}")
    return rows


def download(row: dict[str, str], timeout: int) -> tuple[Path, str]:
    destination = RAW_DIR / row["filename"]
    if destination.exists():
        if destination.stat().st_size == 0 or looks_like_html(destination):
            raise ValueError(f"Invalid existing raw file: {destination}")
        return destination, "existing"

    temporary = destination.with_suffix(destination.suffix + ".part")
    temporary.unlink(missing_ok=True)
    request = Request(
        row["url"],
        headers={"User-Agent": "menos-cunas-otro-pais/1.0 data-audit"},
    )
    try:
        with urlopen(request, timeout=timeout) as response, temporary.open("wb") as output:
            while chunk := response.read(CHUNK_SIZE):
                output.write(chunk)
        if temporary.stat().st_size == 0 or looks_like_html(temporary):
            raise ValueError(f"Downloaded content is not a valid data file: {row['url']}")
        os.replace(temporary, destination)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    return destination, "downloaded"


def write_manifest(rows: list[dict[str, str]]) -> None:
    fields = [
        "resource_id",
        "year",
        "kind",
        "url",
        "filename",
        "bytes",
        "sha256",
        "status",
        "checked_at_utc",
    ]
    with LOCAL_MANIFEST.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=int, default=60)
    args = parser.parse_args()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    checked_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    manifest_rows: list[dict[str, str]] = []

    for source in load_catalog():
        path, status = download(source, args.timeout)
        actual_bytes = path.stat().st_size
        actual_sha256 = sha256_file(path)
        if actual_bytes != int(source["bytes"]):
            raise ValueError(f"Size mismatch for {source['resource_id']}")
        if actual_sha256 != source["sha256"]:
            raise ValueError(f"Checksum mismatch for {source['resource_id']}")
        manifest_rows.append(
            {
                **source,
                "bytes": str(actual_bytes),
                "sha256": actual_sha256,
                "status": status,
                "checked_at_utc": checked_at,
            }
        )
        print(f"{status:10} {source['resource_id']}: {path.name}")

    write_manifest(manifest_rows)
    print(f"manifest   {LOCAL_MANIFEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
