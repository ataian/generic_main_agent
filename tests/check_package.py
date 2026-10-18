#!/usr/bin/env python3
"""Static package checks only. Never import/execute target helpers or commands."""
import ast
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "generic-main-agent-maker", "hermes-agent", "obsidian", "gedaechtnis-praxis",
    "grounded-citations", "minimal-change-engineering", "fremde-installer-pruefen",
    "pdf", "local-backup-restore", "obsidian-daily-summary",
}
ERRORS = []


def check(ok, message):
    if not ok:
        ERRORS.append(message)


def public_files():
    roots = [ROOT / "skills", ROOT / "docs", ROOT / "tests"]
    out = [p for p in ROOT.iterdir() if p.is_file() and p.suffix in {".md", ".json"}]
    out += [ROOT / "LICENSE", ROOT / ".gitignore"]
    for base in roots:
        if base.is_dir():
            out += [p for p in base.rglob("*") if p.is_file() and "__pycache__" not in p.parts]
    return sorted(set(out))


def frontmatter(text, path):
    check(text.startswith("---\n"), f"{path}: frontmatter missing")
    parts = text.split("---\n", 2)
    if len(parts) != 3:
        check(False, f"{path}: frontmatter not closed")
        return
    # Deliberately restricted YAML subset: scalars, inline string lists,
    # and the optional metadata.hermes mapping. Reject all other syntax.
    fields = {}
    section = None
    related = []
    for line in parts[1].splitlines():
        if not line or line.startswith("#"):
            continue
        if line == "metadata:":
            check(section is None, f"{path}: duplicate metadata mapping")
            section = "metadata"
            continue
        if line == "  hermes:" and section == "metadata":
            section = "hermes"
            continue
        if line.startswith(" "):
            nested = re.fullmatch(r"    (tags|related_skills): \[([a-z0-9_, -]*)\]", line)
            check(section == "hermes" and bool(nested), f"{path}: malformed nested metadata")
            if nested and nested[1] == "related_skills":
                related = [value.strip() for value in nested[2].split(",") if value.strip()]
            continue
        m = re.fullmatch(r"([a-z_]+):\s*(.+)", line)
        check(bool(m), f"{path}: unsupported/malformed metadata line")
        if m:
            check(m[1] not in fields, f"{path}: duplicate metadata {m[1]}")
            fields[m[1]] = m[2].strip().strip('"').strip("'")
    check(fields.get("name") == path.parent.name, f"{path}: skill name/path mismatch")
    check(bool(fields.get("description")) and len(fields.get("description", "")) <= 60,
          f"{path}: description must be 1..60 characters")
    check(fields.get("license") == "MIT", f"{path}: MIT missing")
    check(fields.get("version") == "0.1.0", f"{path}: version mismatch")
    check(bool(fields.get("author")), f"{path}: author missing")
    check(fields.get("platforms") == "[linux]", f"{path}: platform mismatch")
    check(fields.get("description", "").endswith("."), f"{path}: description punctuation")
    for name in related:
        check(name in EXPECTED, f"{path}: unknown related skill {name}")
    check(bool(parts[2].strip()), f"{path}: empty body")


def main():
    manifest = json.loads((ROOT / "manifest.json").read_text())
    declared = [row["name"] for row in manifest["skills"]]
    actual = {p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")}
    check(len(declared) == len(set(declared)), "duplicate manifest skill")
    check(set(declared) == EXPECTED == actual, f"skill-set mismatch: actual={sorted(actual)}")
    for row in manifest["skills"]:
        check(row["path"] == "skills/" + row["name"], "manifest path mismatch")
        check(row.get("required") is True, "starter skill must be required")
    check(manifest["license"] == "MIT", "manifest license")
    check(manifest["defaults"]["backup_schedule"] == "0 3 * * *", "backup schedule")
    check(manifest["defaults"]["daily_summary_schedule"] == "0 2 * * *", "summary schedule")
    check(manifest["defaults"]["retention_days"] == 30, "retention")
    files = public_files()
    public_paths = {p.resolve() for p in files}
    for base in (ROOT / "skills", ROOT / "docs", ROOT / "tests"):
        for p in base.rglob("*"):
            check(not p.is_symlink(), f"symlink in public tree: {p.relative_to(ROOT)}")
    counts = {"files": 0, "skills": 0, "python_ast": 0, "json": 0, "local_links": 0}
    forbidden = [r"/home/(?:mariko|joi)/", r"\b(?:dockerdev[0-9]*|iamdev01|devauth|dockergfx[0-9]*)\b",
                 r"192\.168\.111\.", r"BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY",
                 r"\b(?:sk-proj-|ghp_)[A-Za-z0-9]{12,}"]
    for p in files:
        check(not p.is_symlink(), f"symlink: {p.relative_to(ROOT)}")
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeError, OSError):
            check(False, f"not a readable text artifact: {p}")
            continue
        counts["files"] += 1
        if p.name == "SKILL.md":
            frontmatter(text, p)
            counts["skills"] += 1
        if p.suffix == ".py" or p.name.endswith(".py.example"):
            try:
                ast.parse(text, filename=str(p))
                counts["python_ast"] += 1
            except SyntaxError as exc:
                check(False, f"Python syntax: {p}:{exc.lineno}")
        if p.suffix == ".json" or p.name.endswith(".json.example"):
            try:
                json.loads(text)
                counts["json"] += 1
            except ValueError:
                check(False, f"JSON syntax: {p}")
        if p.name != "check_package.py":
            for pattern in forbidden:
                check(not re.search(pattern, text), f"private/secret pattern in {p.relative_to(ROOT)}")
        if p.suffix == ".md" or p.name.endswith(".md.template"):
            for link in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
                if re.match(r"(?:[a-z]+:|#)", link):
                    continue
                target = unquote(link.split("#", 1)[0])
                if not target:
                    continue
                resolved = (p.parent / target).resolve()
                check(resolved.is_relative_to(ROOT), f"link escapes package: {p}: {link}")
                check(resolved.exists(), f"missing link: {p.relative_to(ROOT)} -> {link}")
                if resolved.is_file():
                    check(resolved in public_paths, f"link targets private/unpackaged file: {p}: {link}")
                elif resolved.is_dir():
                    check(any(item.is_relative_to(resolved) for item in public_paths),
                          f"link targets unpackaged directory: {p}: {link}")
                counts["local_links"] += 1
    readme = (ROOT / "README.md").read_text()
    check("nicht ausgeführt" in readme, "README must disclose non-execution")
    soul = (ROOT / "skills/generic-main-agent-maker/templates/SOUL.md.template").read_text()
    check(set(re.findall(r"\{\{(\w+)\}\}", soul)) == {"AGENT_NAME", "USER_NAME"}, "SOUL placeholders")
    principles = soul.split("## Kernprinzipien\n", 1)[-1].split("\n## ", 1)[0]
    check(re.findall(r"^(\d+)\. \*\*", principles, re.M) == [str(n) for n in range(1, 11)],
          "SOUL must retain ten explicit core principles")
    for contract in (
        "### Level 1 — Autonom", "### Level 2 — Autonom, ankündigen und verifizieren",
        "### Level 3 — Vorherige ausdrückliche Zustimmung",
        "höchste zutreffende Level", "warte nicht auf Zustimmung",
        "ausschließlich deine eigene VM", "deren Server administrierst du nicht",
        "## Geschützte lokale Grundlagen", "direkte und indirekte Abhängigkeiten",
        "Eine einmalige Zustimmung ist keine Dauerfreigabe",
        "Regeländerungen gelten nicht rückwirkend", "Aufräumen ist keine pauschale Löschbefugnis",
        "offengelegte und ausdrücklich genehmigte Backup-Rotation",
    ):
        check(contract in soul, f"SOUL contract missing: {contract}")
    schedules = (ROOT / "skills/generic-main-agent-maker/references/zeitplaene.md").read_text()
    for contract in ("[CRON_FAILURE]", "failure_deliver", "HERMES_TIMEZONE", "paused=false"):
        check(contract in schedules, f"cron contract missing: {contract}")
    for relative in ["/references/", ".local/", "/dist/", ".env"]:
        check(relative in (ROOT / ".gitignore").read_text().splitlines(), f"ignore missing {relative}")
    if ERRORS:
        print("STATIC CHECK FAILED")
        for error in ERRORS:
            print("- " + error)
        return 1
    print("STATIC CHECK OK")
    print(json.dumps(counts, sort_keys=True))
    print("No maker, installation, helper, network or runtime function was executed.")
    print("YAML/Compose runtime validation and end-to-end behaviour are not proven by this check.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
