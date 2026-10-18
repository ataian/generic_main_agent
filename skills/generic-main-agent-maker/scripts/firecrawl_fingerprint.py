#!/usr/bin/env python3
"""Read a local dotenv assignment; emit only its router-compatible SHA-256.
No evaluation, network, writes or credential output. Run only on the target.
"""
import argparse
import hashlib
import os
from pathlib import Path
import re
import stat
import sys


def fingerprint(path):
    path = Path(path).expanduser()
    if path.is_symlink():
        raise ValueError("symlink")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid():
            raise ValueError("ownership")
        if stat.S_IMODE(info.st_mode) & 0o077 or info.st_size > 1024 * 1024:
            raise ValueError("permissions/size")
        with os.fdopen(fd, encoding="utf-8") as stream:
            fd = None
            lines = stream.read().splitlines()
    finally:
        if fd is not None:
            os.close(fd)
    values = []
    for line in lines:
        match = re.match(r"^\s*(?:export\s+)?FIRECRAWL_API_KEY\s*=(.*)$", line)
        if not match:
            continue
        raw = match.group(1).strip()
        if raw.startswith(("'", '"')):
            quote = raw[0]
            end = raw.find(quote, 1)
            if end < 0 or raw[end + 1:].strip() and not raw[end + 1:].strip().startswith("#"):
                raise ValueError("format")
            value = raw[1:end]
            if "\\" in value or "$" in value or "`" in value:
                raise ValueError("interpolation")
        else:
            value = re.split(r"\s+#", raw, maxsplit=1)[0].strip()
            if any(c.isspace() for c in value) or any(c in value for c in "\\$`'\""):
                raise ValueError("format")
        if not value.strip():
            raise ValueError("empty")
        values.append(value.strip())
    if len(values) != 1:
        raise ValueError("missing/duplicate")
    return hashlib.sha256(values[0].encode("utf-8")).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = fingerprint(args.env_file)
    except (OSError, UnicodeError, ValueError):
        print("Fingerprint nicht ermittelt: Datei/Rechte oder eindeutige einfache FIRECRAWL_API_KEY-Zuweisung prüfen; kein Secret ausgegeben.", file=sys.stderr)
        return 1
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
