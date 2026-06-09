from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from app.core.config import settings


HEADER_ALIASES: dict[str, tuple[str, ...]] = {
    "school_name": ("school name", "institution", "law school", "school"),
    "aba_school_code": ("aba school code", "aba code", "school code"),
    "city": ("city",),
    "state": ("state", "state abbreviation"),
    "region": ("region", "geographic region"),
    "website_url": ("website", "website url", "website address"),
    "academic_year": ("academic year", "report year", "year"),
    "total_enrollment": ("total enrollment", "enrollment"),
    "first_year_enrollment": ("first year enrollment", "1l enrollment", "first-year enrollment"),
    "median_gpa": ("median gpa", "gpa 50th percentile", "gpa median"),
    "median_lsat": ("median lsat", "lsat 50th percentile", "lsat median"),
    "gpa_25th_percentile": ("gpa 25th percentile", "gpa 25th", "25th percentile gpa"),
    "gpa_50th_percentile": ("gpa 50th percentile", "gpa median", "median gpa"),
    "gpa_75th_percentile": ("gpa 75th percentile", "gpa 75th", "75th percentile gpa"),
    "lsat_25th_percentile": ("lsat 25th percentile", "lsat 25th", "25th percentile lsat"),
    "lsat_50th_percentile": ("lsat 50th percentile", "lsat median", "median lsat"),
    "lsat_75th_percentile": ("lsat 75th percentile", "lsat 75th", "75th percentile lsat"),
    "acceptance_rate": ("acceptance rate", "admit rate"),
    "student_faculty_ratio": ("student faculty ratio", "student/faculty ratio"),
    "resident_tuition": ("resident tuition", "in-state tuition", "tuition in state", "tuition in-state"),
    "nonresident_tuition": ("nonresident tuition", "out-of-state tuition", "tuition out state", "tuition out-of-state"),
    "required_fees": ("required fees", "fees"),
    "living_expenses": ("living expenses", "cost of living"),
    "total_cost_of_attendance": ("total cost of attendance", "coa", "cost of attendance"),
    "first_time_takers": ("first time takers", "first-time takers"),
    "first_time_pass_rate": ("first time pass rate", "first-time pass rate"),
    "ultimate_pass_rate": ("ultimate pass rate", "bar passage rate"),
    "employed_full_time_long_term": ("employed full time long term", "full-time long-term employment"),
    "employed_part_time": ("employed part time", "part-time employment"),
    "employed_jd_required": ("employed jd required", "jd required employment"),
    "employed_jd_advantage": ("employed jd advantage", "jd advantage employment"),
    "unemployed_seeking": ("unemployed seeking", "seeking employment"),
    "graduation_year": ("graduation year", "class year"),
}

SPECIAL_NAME_ALIASES = {
    "new york university school of law": "nyu school of law",
    "university of pennsylvania carey law school": "penn carey law",
    "university of california los angeles school of law": "ucla school of law",
    "university of california berkeley school of law": "uc berkeley school of law",
    "university of texas school of law": "university of texas school of law",
    "northwestern university pritzker school of law": "northwestern pritzker school of law",
    "university of virginia school of law": "university of virginia school of law",
}


@dataclass(slots=True)
class Aba509Record:
    school_name: str
    city: str
    state: str
    academic_year: int
    aba_school_code: str | None = None
    region: str | None = None
    website_url: str | None = None
    total_enrollment: int | None = None
    first_year_enrollment: int | None = None
    median_gpa: float | None = None
    median_lsat: int | None = None
    gpa_25th_percentile: float | None = None
    gpa_50th_percentile: float | None = None
    gpa_75th_percentile: float | None = None
    lsat_25th_percentile: int | None = None
    lsat_50th_percentile: int | None = None
    lsat_75th_percentile: int | None = None
    acceptance_rate: float | None = None
    student_faculty_ratio: float | None = None
    resident_tuition: float | None = None
    nonresident_tuition: float | None = None
    required_fees: float | None = None
    living_expenses: float | None = None
    total_cost_of_attendance: float | None = None
    first_time_takers: int | None = None
    first_time_pass_rate: float | None = None
    ultimate_pass_rate: float | None = None
    employed_full_time_long_term: float | None = None
    employed_part_time: float | None = None
    employed_jd_required: float | None = None
    employed_jd_advantage: float | None = None
    unemployed_seeking: float | None = None
    graduation_year: int | None = None


def normalize_school_name(name: str) -> str:
    cleaned = normalize_text(name)
    if cleaned in SPECIAL_NAME_ALIASES:
        return SPECIAL_NAME_ALIASES[cleaned]

    tokens = [token for token in cleaned.split() if token not in {"the", "of", "and"}]
    compact = " ".join(tokens)
    compact = re.sub(r"\blaw school\b", "law", compact)
    return compact.strip()


def normalize_text(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.strip().lower()).strip()


def normalize_header(value: str) -> str:
    return normalize_text(value)


def _parse_int(value: Any) -> int | None:
    if value is None:
        return None
    text_value = str(value).strip().replace(",", "")
    if not text_value:
        return None
    match = re.search(r"[-+]?\d+", text_value)
    if not match:
        return None
    return int(match.group(0))


def _parse_float(value: Any) -> float | None:
    if value is None:
        return None
    text_value = str(value).strip().replace(",", "").replace("%", "")
    if not text_value:
        return None
    match = re.search(r"[-+]?\d*\.?\d+", text_value)
    if not match:
        return None
    return float(match.group(0))


def _parse_percent(value: Any) -> float | None:
    parsed = _parse_float(value)
    if parsed is None:
        return None
    return parsed


def _parse_year(value: Any) -> int | None:
    parsed = _parse_int(value)
    if parsed is not None:
        return parsed
    if value is None:
        return None
    match = re.search(r"(19|20)\d{2}", str(value))
    return int(match.group(0)) if match else None


def _alias_map() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for canonical, aliases in HEADER_ALIASES.items():
        mapping[normalize_header(canonical.replace("_", " "))] = canonical
        for alias in aliases:
            mapping[normalize_header(alias)] = canonical
    return mapping


HEADER_MAP = _alias_map()


def _extract(row: Mapping[str, Any], field: str) -> Any:
    normalized_row = {normalize_header(key): value for key, value in row.items() if key}
    for alias, canonical in HEADER_MAP.items():
        if canonical == field and alias in normalized_row:
            return normalized_row[alias]
    return None


def _get_required(row: Mapping[str, Any], field: str) -> str:
    value = _extract(row, field)
    if value is None or str(value).strip() == "":
        raise ValueError(f"Missing required field: {field}")
    return str(value).strip()


def _record_from_row(row: Mapping[str, Any], fallback_year: int | None = None) -> Aba509Record:
    school_name = _get_required(row, "school_name")
    city = _get_required(row, "city")
    state = _get_required(row, "state").upper()
    report_year = _parse_year(_extract(row, "academic_year")) or fallback_year
    if report_year is None:
        raise ValueError(f"Unable to determine academic year for {school_name}")

    gpa_50th = _parse_float(_extract(row, "gpa_50th_percentile")) or _parse_float(_extract(row, "median_gpa"))
    lsat_50th = _parse_int(_extract(row, "lsat_50th_percentile")) or _parse_int(_extract(row, "median_lsat"))

    return Aba509Record(
        school_name=school_name,
        city=city,
        state=state,
        academic_year=report_year,
        aba_school_code=(_extract(row, "aba_school_code") or None),
        region=(_extract(row, "region") or None),
        website_url=(_extract(row, "website_url") or None),
        total_enrollment=_parse_int(_extract(row, "total_enrollment")),
        first_year_enrollment=_parse_int(_extract(row, "first_year_enrollment")),
        median_gpa=_parse_float(_extract(row, "median_gpa")),
        median_lsat=_parse_int(_extract(row, "median_lsat")),
        gpa_25th_percentile=_parse_float(_extract(row, "gpa_25th_percentile")),
        gpa_50th_percentile=gpa_50th,
        gpa_75th_percentile=_parse_float(_extract(row, "gpa_75th_percentile")),
        lsat_25th_percentile=_parse_int(_extract(row, "lsat_25th_percentile")),
        lsat_50th_percentile=lsat_50th,
        lsat_75th_percentile=_parse_int(_extract(row, "lsat_75th_percentile")),
        acceptance_rate=_parse_percent(_extract(row, "acceptance_rate")),
        student_faculty_ratio=_parse_float(_extract(row, "student_faculty_ratio")),
        resident_tuition=_parse_float(_extract(row, "resident_tuition")),
        nonresident_tuition=_parse_float(_extract(row, "nonresident_tuition")),
        required_fees=_parse_float(_extract(row, "required_fees")),
        living_expenses=_parse_float(_extract(row, "living_expenses")),
        total_cost_of_attendance=_parse_float(_extract(row, "total_cost_of_attendance")),
        first_time_takers=_parse_int(_extract(row, "first_time_takers")),
        first_time_pass_rate=_parse_percent(_extract(row, "first_time_pass_rate")),
        ultimate_pass_rate=_parse_percent(_extract(row, "ultimate_pass_rate")),
        employed_full_time_long_term=_parse_percent(_extract(row, "employed_full_time_long_term")),
        employed_part_time=_parse_percent(_extract(row, "employed_part_time")),
        employed_jd_required=_parse_percent(_extract(row, "employed_jd_required")),
        employed_jd_advantage=_parse_percent(_extract(row, "employed_jd_advantage")),
        unemployed_seeking=_parse_percent(_extract(row, "unemployed_seeking")),
        graduation_year=_parse_year(_extract(row, "graduation_year")) or report_year,
    )


def _load_csv(path: Path) -> list[Aba509Record]:
    delimiter = "\t" if path.suffix.lower() == ".tsv" else ","
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle, delimiter=delimiter)
        fallback_year = _parse_year(path.stem)
        return [_record_from_row(row, fallback_year=fallback_year) for row in reader]


def _load_json(path: Path) -> list[Aba509Record]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)

    if isinstance(payload, dict):
        rows = payload.get("records") or payload.get("data") or []
        fallback_year = _parse_year(payload.get("report_year")) or _parse_year(path.stem)
    elif isinstance(payload, list):
        rows = payload
        fallback_year = _parse_year(path.stem)
    else:
        raise ValueError(f"Unsupported JSON structure in {path}")

    return [_record_from_row(row, fallback_year=fallback_year) for row in rows]


def load_records_from_path(path: Path) -> list[Aba509Record]:
    if path.is_dir():
        records: list[Aba509Record] = []
        for child in sorted(path.rglob("*")):
            if child.is_file() and child.suffix.lower() in {".csv", ".tsv", ".json"}:
                records.extend(load_records_from_path(child))
        return records

    if path.suffix.lower() in {".csv", ".tsv"}:
        return _load_csv(path)
    if path.suffix.lower() == ".json":
        return _load_json(path)

    raise ValueError(f"Unsupported file type: {path.suffix}")


def _iter_source_files(path: Path) -> Iterable[Path]:
    if path.is_dir():
        return [child for child in sorted(path.rglob("*")) if child.is_file() and child.suffix.lower() in {".csv", ".tsv", ".json"}]
    return [path]


def _compute_checksum(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.name.encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


def _school_lookup_key(record: Aba509Record) -> str:
    normalized_name = normalize_school_name(record.school_name)
    return f"{normalized_name}|{record.city.strip().lower()}|{record.state.strip().upper()}"


def _load_school_index(conn) -> dict[str, int]:
    rows = conn.execute(text("SELECT id, aba_school_code, name, city, state FROM law_schools")).mappings().all()
    index: dict[str, int] = {}
    for row in rows:
        if row["aba_school_code"]:
            index[f"code:{str(row['aba_school_code']).strip().upper()}"] = int(row["id"])
        index[
            f"{normalize_school_name(str(row['name']))}|{str(row['city']).strip().lower()}|{str(row['state']).strip().upper()}"
        ] = int(row["id"])
    return index


def _upsert_school(conn, record: Aba509Record, index: dict[str, int]) -> int:
    code_key = f"code:{record.aba_school_code.strip().upper()}" if record.aba_school_code else None
    school_key = _school_lookup_key(record)

    existing_id = index.get(code_key) if code_key else None
    if existing_id is None:
        existing_id = index.get(school_key)

    if existing_id is not None:
        conn.execute(
            text(
                """
                UPDATE law_schools
                SET aba_school_code = COALESCE(:aba_school_code, aba_school_code),
                    name = :name,
                    city = :city,
                    state = :state,
                    region = :region,
                    website_url = :website_url,
                    is_aba_accredited = TRUE
                WHERE id = :id
                """
            ),
            {
                "id": existing_id,
                "aba_school_code": record.aba_school_code,
                "name": record.school_name,
                "city": record.city,
                "state": record.state,
                "region": record.region,
                "website_url": record.website_url,
            },
        )
        if code_key:
            index[code_key] = existing_id
        index[school_key] = existing_id
        return existing_id

    if record.aba_school_code:
        inserted_id = conn.execute(
            text(
                """
                INSERT INTO law_schools (aba_school_code, name, city, state, region, website_url, is_aba_accredited)
                VALUES (:aba_school_code, :name, :city, :state, :region, :website_url, TRUE)
                ON CONFLICT (aba_school_code) DO UPDATE
                SET name = EXCLUDED.name,
                    city = EXCLUDED.city,
                    state = EXCLUDED.state,
                    region = EXCLUDED.region,
                    website_url = EXCLUDED.website_url,
                    is_aba_accredited = TRUE
                RETURNING id
                """
            ),
            {
                "aba_school_code": record.aba_school_code,
                "name": record.school_name,
                "city": record.city,
                "state": record.state,
                "region": record.region,
                "website_url": record.website_url,
            },
        ).scalar_one()
    else:
        inserted_id = conn.execute(
            text(
                """
                INSERT INTO law_schools (name, city, state, region, website_url, is_aba_accredited)
                VALUES (:name, :city, :state, :region, :website_url, TRUE)
                ON CONFLICT ON CONSTRAINT law_schools_name_city_state_key DO UPDATE
                SET region = EXCLUDED.region,
                    website_url = EXCLUDED.website_url,
                    is_aba_accredited = TRUE
                RETURNING id
                """
            ),
            {
                "name": record.school_name,
                "city": record.city,
                "state": record.state,
                "region": record.region,
                "website_url": record.website_url,
            },
        ).scalar_one()

    inserted_id = int(inserted_id)
    if code_key:
        index[code_key] = inserted_id
    index[school_key] = inserted_id
    return inserted_id


def _upsert_school_statistics(conn, school_id: int, record: Aba509Record) -> None:
    conn.execute(
        text(
            """
            INSERT INTO school_statistics (
                law_school_id,
                academic_year,
                total_enrollment,
                first_year_enrollment,
                median_gpa,
                median_lsat,
                gpa_25th_percentile,
                gpa_50th_percentile,
                gpa_75th_percentile,
                lsat_25th_percentile,
                lsat_50th_percentile,
                lsat_75th_percentile,
                acceptance_rate,
                student_faculty_ratio
            ) VALUES (
                :law_school_id,
                :academic_year,
                :total_enrollment,
                :first_year_enrollment,
                :median_gpa,
                :median_lsat,
                :gpa_25th_percentile,
                :gpa_50th_percentile,
                :gpa_75th_percentile,
                :lsat_25th_percentile,
                :lsat_50th_percentile,
                :lsat_75th_percentile,
                :acceptance_rate,
                :student_faculty_ratio
            )
            ON CONFLICT (law_school_id, academic_year) DO UPDATE
            SET total_enrollment = EXCLUDED.total_enrollment,
                first_year_enrollment = EXCLUDED.first_year_enrollment,
                median_gpa = EXCLUDED.median_gpa,
                median_lsat = EXCLUDED.median_lsat,
                gpa_25th_percentile = EXCLUDED.gpa_25th_percentile,
                gpa_50th_percentile = EXCLUDED.gpa_50th_percentile,
                gpa_75th_percentile = EXCLUDED.gpa_75th_percentile,
                lsat_25th_percentile = EXCLUDED.lsat_25th_percentile,
                lsat_50th_percentile = EXCLUDED.lsat_50th_percentile,
                lsat_75th_percentile = EXCLUDED.lsat_75th_percentile,
                acceptance_rate = EXCLUDED.acceptance_rate,
                student_faculty_ratio = EXCLUDED.student_faculty_ratio
            """
        ),
        {
            "law_school_id": school_id,
            "academic_year": record.academic_year,
            "total_enrollment": record.total_enrollment,
            "first_year_enrollment": record.first_year_enrollment,
            "median_gpa": record.median_gpa,
            "median_lsat": record.median_lsat,
            "gpa_25th_percentile": record.gpa_25th_percentile,
            "gpa_50th_percentile": record.gpa_50th_percentile,
            "gpa_75th_percentile": record.gpa_75th_percentile,
            "lsat_25th_percentile": record.lsat_25th_percentile,
            "lsat_50th_percentile": record.lsat_50th_percentile,
            "lsat_75th_percentile": record.lsat_75th_percentile,
            "acceptance_rate": record.acceptance_rate,
            "student_faculty_ratio": record.student_faculty_ratio,
        },
    )


def _upsert_tuition(conn, school_id: int, record: Aba509Record) -> None:
    conn.execute(
        text(
            """
            INSERT INTO tuition_costs (
                law_school_id,
                academic_year,
                resident_tuition,
                nonresident_tuition,
                required_fees,
                living_expenses,
                total_cost_of_attendance
            ) VALUES (
                :law_school_id,
                :academic_year,
                :resident_tuition,
                :nonresident_tuition,
                :required_fees,
                :living_expenses,
                :total_cost_of_attendance
            )
            ON CONFLICT (law_school_id, academic_year) DO UPDATE
            SET resident_tuition = EXCLUDED.resident_tuition,
                nonresident_tuition = EXCLUDED.nonresident_tuition,
                required_fees = EXCLUDED.required_fees,
                living_expenses = EXCLUDED.living_expenses,
                total_cost_of_attendance = EXCLUDED.total_cost_of_attendance
            """
        ),
        {
            "law_school_id": school_id,
            "academic_year": record.academic_year,
            "resident_tuition": record.resident_tuition,
            "nonresident_tuition": record.nonresident_tuition,
            "required_fees": record.required_fees,
            "living_expenses": record.living_expenses,
            "total_cost_of_attendance": record.total_cost_of_attendance,
        },
    )


def _upsert_employment(conn, school_id: int, record: Aba509Record) -> None:
    graduation_year = record.graduation_year or record.academic_year
    conn.execute(
        text(
            """
            INSERT INTO employment_outcomes (
                law_school_id,
                graduation_year,
                employed_full_time_long_term,
                employed_part_time,
                employed_jd_required,
                employed_jd_advantage,
                unemployed_seeking
            ) VALUES (
                :law_school_id,
                :graduation_year,
                :employed_full_time_long_term,
                :employed_part_time,
                :employed_jd_required,
                :employed_jd_advantage,
                :unemployed_seeking
            )
            ON CONFLICT (law_school_id, graduation_year) DO UPDATE
            SET employed_full_time_long_term = EXCLUDED.employed_full_time_long_term,
                employed_part_time = EXCLUDED.employed_part_time,
                employed_jd_required = EXCLUDED.employed_jd_required,
                employed_jd_advantage = EXCLUDED.employed_jd_advantage,
                unemployed_seeking = EXCLUDED.unemployed_seeking
            """
        ),
        {
            "law_school_id": school_id,
            "graduation_year": graduation_year,
            "employed_full_time_long_term": record.employed_full_time_long_term,
            "employed_part_time": record.employed_part_time,
            "employed_jd_required": record.employed_jd_required,
            "employed_jd_advantage": record.employed_jd_advantage,
            "unemployed_seeking": record.unemployed_seeking,
        },
    )


def _start_import_run(conn, source_name: str, checksum: str, report_year: int | None, file_count: int) -> int:
    return int(
        conn.execute(
            text(
                """
                INSERT INTO aba_509_import_runs (source_name, source_checksum, report_year, file_count, status)
                VALUES (:source_name, :source_checksum, :report_year, :file_count, 'processing')
                ON CONFLICT (source_checksum) DO UPDATE
                SET source_name = EXCLUDED.source_name,
                    report_year = EXCLUDED.report_year,
                    file_count = EXCLUDED.file_count,
                    status = 'processing',
                    completed_at = NULL,
                    notes = NULL
                RETURNING id
                """
            ),
            {
                "source_name": source_name,
                "source_checksum": checksum,
                "report_year": report_year,
                "file_count": file_count,
            },
        ).scalar_one()
    )


def _finish_import_run(conn, run_id: int, row_count: int, notes: str | None = None, status: str = 'completed') -> None:
    conn.execute(
        text(
            """
            UPDATE aba_509_import_runs
            SET row_count = :row_count,
                status = :status,
                notes = :notes,
                completed_at = NOW()
            WHERE id = :id
            """
        ),
        {"id": run_id, "row_count": row_count, "status": status, "notes": notes},
    )


def ingest_aba509(paths: list[Path], database_url: str | None = None, dry_run: bool = False) -> dict[str, int]:
    if not paths:
        raise ValueError("At least one input path is required")

    source_files: list[Path] = []
    records: list[Aba509Record] = []
    for path in paths:
        source_files.extend(list(_iter_source_files(path)))
        records.extend(load_records_from_path(path))

    if not records:
        return {"files": len(source_files), "records": 0, "schools": 0, "statistics": 0, "tuition": 0, "employment": 0}

    report_years = sorted({record.academic_year for record in records if record.academic_year is not None})
    report_year = report_years[0] if len(report_years) == 1 else None
    checksum = _compute_checksum(source_files)
    source_name = ", ".join(path.name for path in source_files)

    if dry_run:
        return {"files": len(source_files), "records": len(records), "schools": 0, "statistics": 0, "tuition": 0, "employment": 0}

    engine: Engine = create_engine(database_url or settings.database_url, pool_pre_ping=True)

    summary = {"files": len(source_files), "records": len(records), "schools": 0, "statistics": 0, "tuition": 0, "employment": 0}

    with engine.begin() as conn:
        run_id = _start_import_run(conn, source_name, checksum, report_year, len(source_files))
        school_index = _load_school_index(conn)

        try:
            for record in records:
                school_id = _upsert_school(conn, record, school_index)
                _upsert_school_statistics(conn, school_id, record)
                _upsert_tuition(conn, school_id, record)
                _upsert_employment(conn, school_id, record)
                summary["schools"] += 1
                summary["statistics"] += 1
                summary["tuition"] += 1
                summary["employment"] += 1

            _finish_import_run(conn, run_id, len(records), status="completed")
        except Exception as exc:
            _finish_import_run(conn, run_id, len(records), notes=str(exc), status="failed")
            raise

    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Import ABA 509 report exports into PostgreSQL")
    parser.add_argument("input", nargs="+", help="A CSV, TSV, JSON file, or directory containing report exports")
    parser.add_argument("--database-url", dest="database_url", default=None, help="PostgreSQL SQLAlchemy URL")
    parser.add_argument("--dry-run", action="store_true", help="Parse and validate files without writing to the database")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    paths = [Path(item).expanduser().resolve() for item in args.input]
    summary = ingest_aba509(paths, database_url=args.database_url, dry_run=args.dry_run)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()