#!/usr/bin/env python3
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import pandas as pd

LOGGER = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert all .xlsx files to one CSV per file, merging all sheets."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Directory containing .xlsx files (default: script directory).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory for CSV output (default: <input-dir>/csv).",
    )
    parser.add_argument(
        "--pattern",
        default="*.xlsx",
        help="Glob pattern to match Excel files (default: *.xlsx).",
    )
    parser.add_argument(
        "--sheet-name-column",
        default="sheet_name",
        help="Column name to store sheet name (default: sheet_name).",
    )
    parser.add_argument(
        "--sep",
        default=",",
        help="CSV delimiter (default: ,).",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="CSV encoding (default: utf-8).",
    )
    parser.add_argument(
        "--engine",
        default="openpyxl",
        help="Excel engine for pandas (default: openpyxl).",
    )
    parser.add_argument(
        "--keep-index",
        action="store_true",
        help="Write DataFrame index to CSV.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on first read error instead of skipping sheets/files.",
    )
    parser.add_argument(
        "--include-temp",
        action="store_true",
        help="Include temporary Excel files (default: skip ~$/lock files).",
    )
    return parser.parse_args()


def collect_excel_files(input_dir: Path, pattern: str, include_temp: bool) -> list[Path]:
    files = sorted(input_dir.glob(pattern))
    if include_temp:
        return files
    return [path for path in files if not path.name.startswith("~$")]


def read_all_sheets(
    xlsx_path: Path, sheet_name_column: str, engine: str, strict: bool
) -> list[pd.DataFrame]:
    frames: list[pd.DataFrame] = []
    try:
        with pd.ExcelFile(xlsx_path, engine=engine) as xls:
            for sheet_name in xls.sheet_names:
                try:
                    df = pd.read_excel(xls, sheet_name=sheet_name)
                except Exception as exc:
                    LOGGER.error("Failed to read %s [%s]: %s", xlsx_path.name, sheet_name, exc)
                    if strict:
                        raise
                    continue
                df.insert(0, sheet_name_column, sheet_name)
                frames.append(df)
    except Exception as exc:
        LOGGER.error("Failed to open %s: %s", xlsx_path.name, exc)
        if strict:
            raise
        return frames

    return frames


def main() -> int:
    args = parse_args()
    input_dir = args.input_dir.expanduser().resolve()
    output_dir = (
        args.output_dir.expanduser().resolve()
        if args.output_dir
        else input_dir / "csv"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO, format="%(levelname)s: %(message)s", stream=sys.stdout
    )

    excel_files = collect_excel_files(input_dir, args.pattern, args.include_temp)
    if not excel_files:
        LOGGER.error("No .xlsx files found in %s", input_dir)
        return 1

    errors = 0
    for xlsx_path in excel_files:
        frames = read_all_sheets(
            xlsx_path, args.sheet_name_column, args.engine, args.strict
        )
        if not frames:
            LOGGER.warning("No readable sheets in %s", xlsx_path.name)
            errors += 1
            if args.strict:
                return 1
            continue

        merged = pd.concat(frames, ignore_index=True, sort=False)
        out_path = output_dir / f"{xlsx_path.stem}.csv"
        merged.to_csv(
            out_path, index=args.keep_index, sep=args.sep, encoding=args.encoding
        )
        LOGGER.info("Wrote %s", out_path)

    return 1 if errors > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
