# Aufnahmegrenzen und Dateiformat

## Geschlossene Allowlist

Das Skript liest ausschließlich die nachfolgend benannten Quellen. Fehlende
optionale Einträge erscheinen in `manifest.json` unter `missing_optional`.
`config.yaml`, `SOUL.md`, Compose-Datei und Vault mit echtem `.git/` sind Pflicht.
Optional bedeutet nicht automatisch entbehrlich: beim Setup anhand der
installierten Hermes-/Hindsight-Version abnehmen, welche Dateien nötig sind.

| Quelle | Aufnahme |
|---|---|
| Hermes-Home: einzelne Dateien | `config.yaml`, `SOUL.md`, `AGENTS.md`, `backup-config.json`, `state.db`, `skills.db`, `memory.db`, `memories.db`, `cron.db`, `hindsight/config.json`, `maker/environment.json`, `maker/state.json` |
| Hermes-Home: rekursive Verzeichnisse | ausschließlich `memories/`, `skills/`, `cron/`, `sessions/`, `plugins/`, `scripts/` |
| Hermes-Home: separate sensitive Dateien | `.env`, `auth.json`, `credentials.json` |
| Vault | genau der konfigurierte Vault einschließlich `.git/`; keine externen Git-Worktrees |
| Compose-Verzeichnis: separate sensitive Dateien | konfigurierte Compose-Datei sowie `.env`, `hindsight.env`, `api.env`, `config.yaml`, `config.json`, `hindsight.yaml`, `hindsight.service`, `hindsight-api.service`, `run-api.sh`, `requirements.txt`, `requirements.lock`, `init-db.sh`, `check.py` |
| PostgreSQL | genau DB `hindsight` des Dienstes `db` im konfigurierten lokalen Compose-Projekt |

`profiles/`, Logs, Caches, komplette Hermes-Quellinstallationen, Python-venvs,
Docker-Volumes, weitere Projekte, Systemkonfiguration und Home-Wurzel sind nicht
pauschal enthalten. Das konfigurierte Hermes-Home darf ein einzelnes Profil
sein, aber niemals der gemeinsame `profiles/`-Container. Wer zusätzliche
notwendige Dateien entdeckt, stoppt die Vollständigkeitsabnahme und erweitert
nach Freigabe gezielt die Allowlist; keinen Catch-all-Scan hinzufügen.

Das Skript weist unbekannte SQLite-Dateiendungen unmittelbar im Hermes-Home
zurück. Innerhalb aufgenommener Bäume erkennt es SQLite am Header unabhängig
vom Dateinamen. `.db`, `.sqlite` oder `.sqlite3` ohne gültigen Header werden
abgelehnt statt unbemerkt roh kopiert. WAL/SHM/Journal werden nur ausgelassen,
wenn die zugehörige Hauptdatei vorhanden und als SQLite erkannt ist.
Andere Datenbankformate sind nicht unterstützt. Änderungen zwischen mehreren
SQLite-Snapshots oder Datenbanksystemen sind keine gemeinsame Transaktion.

Das aktuelle Hindsight-Rezept legt `compose.yaml`, `.env`, `init-db.sh` und
`check.py` im Betriebsverzeichnis ab; API und DB sind Compose-Dienste, keine
Systemd-Units. Die übrigen benannten Betriebsdateien bleiben optional für
bereits geprüfte Varianten. Plugin-JSON sowie Maker-Umgebung und -Status werden
als einzelne Dateien aufgenommen, nicht die kompletten `hindsight/`- oder
`maker/`-Bäume. Insbesondere `maker/rollback/` und Prüfausgaben sind nicht enthalten.
Beim Setup die fünf ergänzten Dateien anhand des Rezepts als erforderlich
abnehmen; ein Eintrag in `missing_optional` ersetzt diese Vollständigkeitsprüfung
nicht. Plugin-JSON und Maker-JSON dürfen keine Secrets enthalten.
Zusätzliche Compose-Includes,
Override-Dateien, externe `env_file`-/Secret-/Config-Pfade oder ein tatsächliches
Systemd-Unit-Drop-in sind **nicht automatisch enthalten**. Vor Freigabe prüfen:
Betriebskonfiguration vollständig in diese Dateien überführen beziehungsweise
den Scope gezielt erweitern, ohne fremde Verzeichnisse rekursiv zu erfassen.
Zugangsdaten bleiben in `.env`/`*.env`, nicht in normalen Konfigurationsdateien.
Eine sensitive Datei im Git-Verlauf bleibt trotz getrennter Sicherung ein Leck.

## Set-Verzeichnis

`~/backups/<instanz>/` enthält `OWNER.json`, `.lock` und eindeutige
`set-<UTC-Zeitstempel>-<UUID>/`-Verzeichnisse. `OWNER.json` bindet den Namespace
an den SHA-256 der sortierten JSON-Konfiguration. Geänderte Pfade oder
Projektkennung benötigen einen neuen Namespace beziehungsweise eine explizit
geprüfte Migration; keine fremden Marker überschreiben.

Ein erfolgreicher Satz enthält **genau**:

- `hermes.tar`: ausgewählte Hermes-Dateien unter `hermes/`.
- `vault.tar`: Vault einschließlich Git unter `vault/`.
- `sensitive.tar`: Hermes-Credentials unter `hermes/` sowie Compose-/API-
  Betriebskonfiguration unter `service/`; alle Dateien strikt `0600`.
- `hindsight.dump`: PostgreSQL-Custom-Dump, vor Abschluss `pg_restore --list` geprüft.
- `manifest.json`: Formatkennung, Namespace, Erstellungszeit, Quellen und
  fehlende optionale Dateien; Größe/SHA-256 jedes Payloads und jedes Tar-Mitglieds,
  Kennzeichnung jedes SQLite-Snapshots. Enthält keine Dateiinhalte oder Secrets.
- `COMPLETE.json`: Formatkennung, Namespace, Erstellungszeit und Manifest-Hash.

Im laufenden oder fehlgeschlagenen Satz kann `INCOMPLETE.json` und temporär
`.snapshot` vorhanden sein. Solche Sätze niemals als Erfolg zählen oder
automatisch rotieren. Auch ein Stromausfall im Abschlussfenster kann einen Satz
ohne vollständigen Marker hinterlassen; ausschließlich vollständig verifizierte
Sätze verwenden. Verwaiste Teilstände nur nach eigener Prüfung und Freigabe
entfernen. Sonst können sie Speicherplatz belegen; keine versteckte Aufräumroutine.

Tar-Dateien sind unkomprimiert, deterministisch sortiert und enthalten nur
reguläre Dateien mit normalisierten Metadaten. „Deterministisch“ meint einen
festen, LLM-freien Ablauf und definierte Aufnahmegrenzen, nicht bitidentische
Dumps eines veränderlichen Systems oder identische Laufverzeichnisnamen.

## Konfigurationsschema

Das JSON enthält exakt die acht Schlüssel aus `config.example.json`, alle als
nichtleere Strings. `hermes_home`, `vault`, `backup_root`, `compose_file` sind
absolute symlinkfreie Pfade. `db_service = db`, `db_user = hindsight` und
`db_name = hindsight` sind feste Werte. Keine Passwort-, URI-, Shell- oder
Command-Felder. `compose_project` muss dem tatsächlich eingerichteten Projekt
entsprechen. Nur die Zielinstanz wird gelesen; deren Konfigurationsidentität
vor der Einrichtung prüfen, nicht aus dem Autorensystem ableiten.
