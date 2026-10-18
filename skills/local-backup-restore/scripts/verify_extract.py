#!/usr/bin/env python3
"""Prüft einen Sicherungssatz und entpackt nur in ein neues Prüfverzeichnis."""
import argparse
import hashlib
import os
from pathlib import Path, PurePosixPath
import shutil
import sys
import tarfile

from backup import checked, below, read_open, require, verify_set


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--set", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    source, output = checked(args.set), checked(args.output)
    home = checked(Path.home())
    # Absichtlich nur ein NEUES direktes Kind des Benutzer-Homes zulassen.
    require(output.parent == home and not output.exists())
    require(not below(source, output) and not below(output, source))
    manifest = verify_set(source)
    for key in ("hermes_home", "vault", "backup_root", "compose_file"):
        original = checked(manifest["sources"][key])
        if key == "compose_file":
            original = original.parent
        require(not below(output, original) and not below(original, output))
    output.mkdir(mode=0o700)
    try:
        # Nochmals streamweise prüfen, keine extract/extractall-Nutzung, keine Links.
        seen = set()
        for name in ("hermes.tar", "vault.tar", "sensitive.tar"):
            metadata = manifest["payloads"][name]
            with tarfile.open(source / name, "r:") as tar:
                for member in tar:
                    require(member.isfile() and member.name not in seen)
                    parts = PurePosixPath(member.name).parts
                    require(parts and parts[0] in ("hermes", "vault", "service"))
                    require(not PurePosixPath(member.name).is_absolute() and ".." not in parts)
                    target = checked(output.joinpath(*parts))
                    require(below(target, output) and target != output)
                    target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
                    data = tar.extractfile(member)
                    if data is None:
                        raise ValueError("archive member")
                    h = hashlib.sha256()
                    size = 0
                    with data, target.open("xb") as dest:
                        while block := data.read(1024 * 1024):
                            dest.write(block)
                            h.update(block)
                            size += len(block)
                    expected = metadata["entries"][member.name]
                    require(size == expected["size"] and h.hexdigest() == expected["sha256"])
                    seen.add(member.name)
        with read_open(source / "hindsight.dump") as src:
            with (output / "hindsight.dump").open("xb") as dst:
                shutil.copyfileobj(src, dst)
        from backup import digest
        require(digest(output / "hindsight.dump") == manifest["payloads"]["hindsight.dump"]["sha256"])
        with (output / "EXTRACTED.ok").open("x") as f:
            f.write("Nur Archivprüfung/Extraktion; kein PostgreSQL- oder API-Restore-Test.\n")
        print("Archivprüfung und isolierte Extraktion erfolgreich; DB/API-Prüfung offen.")
    except BaseException:
        # Teilstände bleiben zur Untersuchung stehen, niemals pauschal löschen.
        raise


if __name__ == "__main__":
    try:
        main()
    except BaseException:
        print("Archivprüfung/Extraktion fehlgeschlagen; Prüfverzeichnis nicht verwenden.", file=sys.stderr)
        sys.exit(1)
