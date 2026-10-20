#!/usr/bin/env python3
"""Read one Hermes DB; emit day-scoped message metadata, never content.

Contract and later verification: ../references/helper-und-pruefung.md
No Hermes imports, profile discovery, database migrations or vault writes.
"""
from __future__ import annotations

import argparse
from contextlib import closing
from datetime import date, datetime, time, timedelta, timezone
import json
from pathlib import Path
import re
import sqlite3
import sys
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

EPOCH_MAX = 4_200_000_000.0
SAFE_ID = re.compile(r"[A-Za-z0-9_.:-]{1,200}\Z")
ROLES = {"system", "developer", "user", "assistant", "tool", "function", "session_meta"}
FLAGS = ("_compressed_summary", "active", "compacted")


class ContractError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


class Parser(argparse.ArgumentParser):
    def error(self, message):
        # Do not echo arbitrary argument values, paths or identifiers.
        raise ContractError("arguments", "Erwartet: --db ABS --date YYYY-MM-DD --timezone IANA.")


def window(day_text: str, zone_text: str):
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", day_text):
        raise ContractError("date", "Datum muss YYYY-MM-DD entsprechen.")
    try:
        day = date.fromisoformat(day_text)
        zone = ZoneInfo(zone_text)
        # Construct both local midnights separately: a day need not have 24 h.
        start = datetime.combine(day, time.min, tzinfo=zone)
        end = datetime.combine(day + timedelta(days=1), time.min, tzinfo=zone)
    except (ValueError, OverflowError, ZoneInfoNotFoundError):
        raise ContractError("calendar", "Datum oder IANA-Zeitzone ist nicht verfügbar.") from None
    for boundary in (start, end):
        epoch = boundary.timestamp()
        if not 0 <= epoch <= EPOCH_MAX:
            raise ContractError("calendar_range", "Datum außerhalb des unterstützten Epoch-Bereichs.")
        roundtrip = datetime.fromtimestamp(epoch, zone)
        if roundtrip.replace(tzinfo=None) != boundary.replace(tzinfo=None):
            raise ContractError("calendar_gap", "Nicht vorhandene lokale Mitternacht; manuell prüfen.")
    if end.timestamp() <= start.timestamp():
        raise ContractError("calendar_gap", "Kein eindeutiges positives Tagesfenster.")
    return zone, start, end


def schema(conn):
    tables = {row[0] for row in conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name IN ('messages', 'sessions')"
    )}
    if tables != {"messages", "sessions"}:
        raise ContractError("schema", "Benötigte echte Tabellen messages/sessions fehlen.")
    messages = {row[1]: row for row in conn.execute("PRAGMA table_info(messages)")}
    sessions = {row[1]: row for row in conn.execute("PRAGMA table_info(sessions)")}
    if not {"id", "session_id", "role", "timestamp"} <= messages.keys() or "id" not in sessions:
        raise ContractError("schema", "Benötigte ID-, Rollen- oder Zeitspalten fehlen.")
    expected = {"id": {"INTEGER"}, "session_id": {"TEXT"}, "role": {"TEXT"},
                "timestamp": {"REAL", "INTEGER"}}
    if any(messages[key][2].upper() not in types for key, types in expected.items()):
        raise ContractError("schema_type", "Unbekannte Spaltentypen; keine automatische Konvertierung.")
    if messages["id"][5] != 1 or sessions["id"][2].upper() != "TEXT" or sessions["id"][5] != 1:
        raise ContractError("schema_id", "Nicht unterstützte Primärschlüssel.")
    # Metadata-only global guard: malformed times cannot silently become an empty day.
    bad_time = conn.execute(
        "SELECT 1 FROM messages WHERE typeof(timestamp) NOT IN ('integer','real') "
        "OR timestamp < 0 OR timestamp > ? LIMIT 1", (EPOCH_MAX,)
    ).fetchone()
    if bad_time:
        raise ContractError("timestamp", "Ungültige gespeicherte Zeitstempel; Tagesabdeckung ungesichert.")
    return [name for name in FLAGS if name in messages]


def collect(db_text: str, day_text: str, zone_text: str):
    zone, start, end = window(day_text, zone_text)
    db = Path(db_text)
    if not db.is_absolute():
        raise ContractError("db_path", "DB-Pfad muss absolut und bereits aufgelöst sein.")
    try:
        db = db.resolve(strict=True)
    except (OSError, RuntimeError):
        raise ContractError("db_missing", "Ziel-DB fehlt oder ist nicht erreichbar.") from None
    if not db.is_file():
        raise ContractError("db_path", "Ziel-DB ist keine reguläre Datei.")
    # SQLite mode=ro may need WAL sidecars. Never force immutable=1: that
    # would ignore uncheckpointed live WAL data and silently lose messages.
    with db.open("rb") as handle:
        header = handle.read(20)
    if len(header) != 20 or header[:16] != b"SQLite format 3\x00":
        raise ContractError("db_format", "Zieldatei ist keine unterstützte SQLite-Datenbank.")
    if header[18] == 2 and not all(Path(str(db) + suffix).is_file() for suffix in ("-wal", "-shm")):
        raise ContractError("wal_sidecars", "WAL-Lesevoraussetzungen fehlen; keine Sidecars erzeugen.")
    with closing(sqlite3.connect(db.as_uri() + "?mode=ro", uri=True, timeout=5)) as conn:
        conn.execute("PRAGMA query_only = ON")
        conn.execute("PRAGMA trusted_schema = OFF")
        conn.execute("BEGIN")  # One consistent read snapshot, including live WAL.
        flags = schema(conn)
        columns = ", ".join("m." + name for name in flags)
        sql = (
            "SELECT m.id, m.session_id, m.role, m.timestamp, s.id"
            + (", " + columns if columns else "")
            + " FROM messages AS m LEFT JOIN sessions AS s ON s.id = m.session_id"
              " WHERE m.timestamp >= ? AND m.timestamp < ? ORDER BY m.timestamp, m.id"
        )
        grouped = {}
        message_count = 0
        for row in conn.execute(sql, (start.timestamp(), end.timestamp())):
            message_id, session_id, role, epoch, parent_id = row[:5]
            if not isinstance(message_id, int) or message_id < 1:
                raise ContractError("message_id", "Ungültige Nachrichten-ID im Tagesfenster.")
            if not isinstance(session_id, str) or not SAFE_ID.fullmatch(session_id):
                raise ContractError("session_id", "Nicht unterstützte Sitzungs-ID im Tagesfenster.")
            if parent_id is None:
                raise ContractError("orphan", "Tagesnachricht ohne zugehörige Sitzung.")
            if role not in ROLES:
                raise ContractError("role", "Unbekannte Nachrichtenrolle im Tagesfenster.")
            stored_flags = dict(zip(flags, row[5:]))
            if any(value not in (None, 0, 1) for value in stored_flags.values()):
                raise ContractError("flags", "Unbekannte Nachrichtenmarkierung im Tagesfenster.")
            stamp = datetime.fromtimestamp(epoch, timezone.utc)
            item = {"id": message_id, "role": role, "timestamp_epoch": epoch,
                    "timestamp_utc": stamp.isoformat(), "timestamp_local": stamp.astimezone(zone).isoformat(),
                    "flags": stored_flags}
            grouped.setdefault(session_id, []).append(item)
            message_count += 1
        conn.rollback()
    sessions = [{"session_id": sid, "message_count": len(rows), "messages": rows}
                for sid, rows in sorted(grouped.items())]
    return {
        "ok": True, "contract_version": 1, "date": day_text, "timezone": zone.key,
        "window": {"start_inclusive": start.isoformat(), "end_exclusive": end.isoformat(),
                   "start_epoch": start.timestamp(), "end_epoch": end.timestamp()},
        "timestamp_storage": "unix_seconds_numeric", "available_flags": flags,
        "coverage": "all_stored_message_rows_in_window_not_all_lifetime_activity",
        "session_count": len(sessions), "message_count": message_count, "sessions": sessions,
    }


def main():
    try:
        parser = Parser(description=__doc__)
        parser.add_argument("--db", required=True)
        parser.add_argument("--date", required=True)
        parser.add_argument("--timezone", required=True)
        args = parser.parse_args()
        result = collect(args.db, args.date, args.timezone)
    except ContractError as exc:
        result = {"ok": False, "error": {"code": exc.code, "message": str(exc)}}
    except (sqlite3.Error, OSError, ValueError, OverflowError):
        # SQLite/OS errors may contain sensitive filenames or row values.
        result = {"ok": False, "error": {"code": "read_failed", "message": "DB nicht sicher lesbar; keine Tagesabdeckung bestätigt."}}
    print(json.dumps(result, ensure_ascii=False, allow_nan=False, separators=(",", ":")))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
