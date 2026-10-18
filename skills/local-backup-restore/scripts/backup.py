#!/usr/bin/env python3
"""Lokales, instanzgebundenes Backup. Keine Installation, kein Restore."""
import argparse
from contextlib import closing
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sqlite3
import stat
import subprocess
import sys
import tarfile
import time
import uuid

FORMAT = "local-backup-restore/v1"
HOME_DIRS = ("memories", "skills", "cron", "sessions", "plugins", "scripts")
HOME_FILES = ("config.yaml", "SOUL.md", "AGENTS.md", "backup-config.json", "state.db",
              "skills.db", "memory.db", "memories.db", "cron.db", "hindsight/config.json",
              "maker/environment.json", "maker/state.json") + HOME_DIRS
SECRET_FILES = (".env", "auth.json", "credentials.json")
SERVICE_FILES = (".env", "hindsight.env", "api.env", "config.yaml", "config.json",
                 "hindsight.yaml", "hindsight.service", "hindsight-api.service",
                 "run-api.sh", "requirements.txt", "requirements.lock", "init-db.sh", "check.py")
PAYLOADS = ("hermes.tar", "vault.tar", "sensitive.tar", "hindsight.dump")
SET_FILES = set(PAYLOADS) | {"manifest.json", "COMPLETE.json"}


class QuietParser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError("arguments")


def require(ok):
    if not ok:
        raise ValueError("validation")


def checked(path):
    p = Path(path)
    require(p.is_absolute() and ".." not in p.parts)
    for part in (p, *p.parents):
        require(not part.is_symlink())
    return p


def below(a, b):
    return a == b or b in a.parents


def regular(path):
    checked(path)
    s = path.lstat()
    require(stat.S_ISREG(s.st_mode) and s.st_nlink == 1)
    return s


def read_open(path):
    before = regular(path)
    f = os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW), "rb")
    after = os.fstat(f.fileno())
    require((before.st_dev, before.st_ino) == (after.st_dev, after.st_ino))
    return f


def digest(path):
    with read_open(path) as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def write_json(path, obj):
    with path.open("x", encoding="utf-8") as f:
        json.dump(obj, f, sort_keys=True, indent=2)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())


def load_json(path):
    with read_open(path) as f:
        return json.load(f)


def safe_name(name):
    p = PurePosixPath(name)
    return bool(name) and not p.is_absolute() and ".." not in p.parts and str(p) == name


def private_dir(path):
    checked(path)
    if not path.exists():
        path.mkdir(mode=0o700)
    s = path.stat()
    require(stat.S_ISDIR(s.st_mode) and s.st_uid == os.getuid() and s.st_mode & 0o077 == 0)


def walk(path, device):
    checked(path)
    s = path.lstat()
    require(s.st_dev == device)
    if stat.S_ISDIR(s.st_mode):
        for child in sorted(path.iterdir()):
            yield from walk(child, device)
    else:
        regular(path)
        yield path


def is_sqlite(path):
    with read_open(path) as f:
        return f.read(16) == b"SQLite format 3\x00"


def archive(job, name, selections):
    records = {}
    with tarfile.open(job / name, "x", format=tarfile.PAX_FORMAT) as tar:
        for root, relative, prefix in selections:
            source = root / relative
            if not source.exists():
                require(not source.is_symlink())
                continue
            for p in walk(source, root.stat().st_dev):
                arc = str(PurePosixPath(prefix) / p.relative_to(root).as_posix())
                require(safe_name(arc) and arc not in records)
                if p.name.endswith(("-wal", "-shm", "-journal")):
                    base = p.with_name(p.name.rsplit("-", 1)[0])
                    require(base.is_file() and is_sqlite(base))
                    continue
                snapshot = is_sqlite(p)
                require(snapshot or p.suffix.lower() not in (".db", ".sqlite", ".sqlite3"))
                temp = job / ".snapshot"
                original = p
                if snapshot:
                    require(not temp.exists())
                    with closing(sqlite3.connect(p.as_uri() + "?mode=ro", uri=True)) as src:
                        with closing(sqlite3.connect(temp)) as dst:
                            deadline = time.monotonic() + 120
                            def progress(status, remaining, total):
                                require(time.monotonic() < deadline)
                            src.backup(dst, pages=256, progress=progress)
                            require(dst.execute("PRAGMA integrity_check").fetchall() == [("ok",)])
                    p = temp
                with read_open(p) as f:
                    before = os.fstat(f.fileno())
                    h = hashlib.file_digest(f, "sha256").hexdigest()
                    f.seek(0)
                    info = tarfile.TarInfo(arc)
                    info.size, info.mode, info.mtime = before.st_size, 0o600, 0
                    tar.addfile(info, f)
                    after = os.fstat(f.fileno())
                    require((before.st_size, before.st_mtime_ns, before.st_ctime_ns) ==
                            (after.st_size, after.st_mtime_ns, after.st_ctime_ns))
                records[arc] = {"sha256": h, "size": info.size, "sqlite_snapshot": snapshot}
                checked(original)
                if snapshot:
                    temp.unlink()
    return records


def verify_set(job, namespace=None, complete=True):
    checked(job)
    require(job.is_dir())
    manifest = load_json(job / "manifest.json")
    require(manifest["format"] == FORMAT)
    if namespace is not None:
        require(manifest["namespace"] == namespace)
    require(set(manifest["payloads"]) == set(PAYLOADS))
    if complete:
        require({p.name for p in job.iterdir()} == SET_FILES)
        marker = load_json(job / "COMPLETE.json")
        require(marker["namespace"] == manifest["namespace"] and marker["format"] == FORMAT)
        require(marker["manifest_sha256"] == digest(job / "manifest.json"))
        require(marker["created"] == manifest["created"])
    for name, metadata in manifest["payloads"].items():
        p = job / name
        require(regular(p).st_size == metadata["size"] and digest(p) == metadata["sha256"])
        if name.endswith(".tar"):
            seen = set()
            with tarfile.open(p, "r:") as tar:
                for member in tar:
                    require(member.isfile() and safe_name(member.name) and member.name not in seen)
                    require(member.name in metadata["entries"])
                    entry = metadata["entries"][member.name]
                    require(member.size == entry["size"])
                    stream = tar.extractfile(member)
                    if stream is None:
                        raise ValueError("archive member")
                    with stream:
                        h = hashlib.sha256()
                        while block := stream.read(1024 * 1024):
                            h.update(block)
                        require(h.hexdigest() == entry["sha256"])
                    seen.add(member.name)
            require(seen == set(metadata["entries"]))
    return manifest


def rotate(root, newest, namespace):
    # Keine rekursive Löschung: ausschließlich vollständig verifizierte feste Dateisätze.
    for candidate in sorted(root.iterdir()):
        if candidate == newest or candidate.is_symlink() or not candidate.is_dir():
            continue
        if not re.fullmatch(r"set-\d{8}T\d{12}Z-[0-9a-f]{32}", candidate.name):
            continue
        try:
            manifest = verify_set(candidate, namespace)
        except (OSError, ValueError, KeyError, TypeError, tarfile.TarError):
            continue
        if time.time() - manifest["created"] <= 30 * 86400:
            continue
        for name in sorted(SET_FILES - {"COMPLETE.json"}):
            (candidate / name).unlink()
        (candidate / "COMPLETE.json").unlink()
        candidate.rmdir()


def main():
    os.umask(0o077)
    parser = QuietParser(description=__doc__)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    config_path = checked(args.config)
    require(regular(config_path).st_mode & 0o077 == 0)
    cfg = load_json(config_path)
    keys = {"hermes_home", "vault", "backup_root", "compose_file", "compose_project",
            "db_service", "db_user", "db_name"}
    require(set(cfg) == keys and all(isinstance(v, str) and v for v in cfg.values()))
    require(not any("REPLACE" in v for v in cfg.values()))
    require(cfg["db_service"] == "db" and cfg["db_user"] == cfg["db_name"] == "hindsight")
    require(re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,62}", cfg["compose_project"]))
    home = checked(Path.home())
    hh, vault, root, compose = (checked(cfg[k]) for k in
                                ("hermes_home", "vault", "backup_root", "compose_file"))
    service = compose.parent
    require(root.parent == home / "backups" and root.name not in ("", ".", ".."))
    require(all(below(p, home) and p != home for p in (hh, vault, service)))
    require(hh.is_dir() and vault.is_dir() and service.is_dir())
    require(compose.is_file() and (hh / "config.yaml").is_file() and (hh / "SOUL.md").is_file())
    require((vault / ".git").is_dir())  # Keine externen Git-Worktree-Metadaten.
    roots = (hh, vault, service, root)
    require(all(not below(a, b) and not below(b, a) for i, a in enumerate(roots) for b in roots[i+1:]))
    for p in (hh, vault, service):
        checked(p)
    namespace = hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()
    private_dir(home / "backups")
    if root.exists():
        private_dir(root)
        require(load_json(root / "OWNER.json") == {"format": FORMAT, "namespace": namespace})
    else:
        private_dir(root)
        write_json(root / "OWNER.json", {"format": FORMAT, "namespace": namespace})
    lockpath = root / ".lock"
    fd = os.open(lockpath, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    lock = os.fdopen(fd, "r+")
    regular(lockpath)
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    created = time.time()
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    job = root / ("set-" + stamp + "-" + uuid.uuid4().hex)
    job.mkdir(mode=0o700)
    write_json(job / "INCOMPLETE.json", {"format": FORMAT, "namespace": namespace})
    manifest = {"format": FORMAT, "namespace": namespace, "created": created,
                "sources": cfg, "payloads": {}, "missing_optional": []}
    normal = [(hh, name, "hermes") for name in HOME_FILES]
    sensitive = [(hh, name, "hermes") for name in SECRET_FILES]
    sensitive += [(service, name, "service") for name in sorted(set(SERVICE_FILES) | {compose.name})]
    require(all(p.name in HOME_FILES for p in hh.iterdir()
                if p.suffix.lower() in (".db", ".sqlite", ".sqlite3")))
    for base, name, prefix in normal + sensitive:
        item = base / name
        if item.exists():
            if prefix == "hermes" and name in HOME_DIRS:
                require(item.is_dir())
            else:
                regular(item)
        else:
            manifest["missing_optional"].append(prefix + "/" + name)
    for name, selection in (("hermes.tar", normal), ("vault.tar", [(vault, ".", "vault")]),
                            ("sensitive.tar", sensitive)):
        entries = archive(job, name, selection)
        manifest["payloads"][name] = {"entries": entries}
    docker = ["docker", "--host", "unix:///var/run/docker.sock", "compose", "--project-directory",
              str(service), "-f", str(compose), "-p", cfg["compose_project"], "exec", "-T",
              "--user", "postgres", "db"]
    env = {"PATH": os.defpath, "HOME": str(home), "LANG": "C"}
    dump = job / "hindsight.dump"
    with dump.open("xb") as out:
        # Expansion ausschließlich im Container; weder Host-ENV noch argv enthält das Secret.
        subprocess.run(docker + ["sh", "-eu", "-c",
                       'PGPASSWORD="${HINDSIGHT_DB_PASSWORD:?}" exec pg_dump '
                       '-h 127.0.0.1 -U hindsight -d hindsight -Fc -w --no-owner --no-acl'],
                       stdout=out, stderr=subprocess.DEVNULL, env=env, check=True, timeout=1800)
    require(dump.stat().st_size > 0)
    with read_open(dump) as src:
        subprocess.run(docker + ["pg_restore", "--list"], stdin=src, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, env=env, check=True, timeout=180)
    manifest["payloads"]["hindsight.dump"] = {}
    for name, metadata in manifest["payloads"].items():
        metadata.update(sha256=digest(job / name), size=(job / name).stat().st_size)
        with read_open(job / name) as f:
            os.fsync(f.fileno())
    write_json(job / "manifest.json", manifest)
    verify_set(job, namespace, complete=False)
    (job / "INCOMPLETE.json").unlink()
    write_json(job / "COMPLETE.json", {"format": FORMAT, "namespace": namespace,
               "created": created, "manifest_sha256": digest(job / "manifest.json")})
    verify_set(job, namespace)
    for directory in (job, root):
        dirfd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            os.fsync(dirfd)
        finally:
            os.close(dirfd)
    rotate(root, job, namespace)
    # Erfolgreiches no_agent-Cron bleibt durch leeres stdout still.


if __name__ == "__main__":
    try:
        main()
    except (Exception, KeyboardInterrupt):
        print("Backup fehlgeschlagen; lokal und ohne Secret-Ausgabe prüfen.", file=sys.stderr)
        sys.exit(1)
