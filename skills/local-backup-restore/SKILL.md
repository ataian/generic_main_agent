---
name: local-backup-restore
description: Eigene lokale Backups sichern, prüfen und wiederherstellen.
version: 0.1.0
author: Max, Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [backup, restore, sqlite, hindsight]
    related_skills: []
---

# Lokale Backups und kontrollierter Restore

Sichert genau eine Hermes-Instanz, ihren Vault mit Git und ihre lokale
Hindsight-Datenbank. Eigene Neuentwicklung unter MIT; kein übernommenes
Betriebsskript, kein Installer und keine Freigabe für fremde Systeme.

## Wann verwenden

- Eigenes lokales Backup einrichten, kontrollieren oder wiederherstellen.
- Nicht für andere Profile, fremde Banken, Remote-Dienste oder Host-Vollbackups.
- Bei Restore immer zuerst [Restore-Anleitung](references/restore.md) lesen.

## Voraussetzungen und Freigabe

1. Vor Änderungen Herkunft und Stand dieses Pakets prüfen: Skripte lesen,
   Zielpfade und Schutzgrenzen mit dem Benutzer abgleichen. Es gilt weiterhin
   die SOUL; dieser Skill erteilt keine zusätzlichen Rechte.
2. Linux, Python **3.11+** mit stdlib `sqlite3`, `fcntl` und `tarfile`; Docker
   Compose v2 mit lokalem Unix-Socket `/var/run/docker.sock`. Rootless-Sockets,
   Remote-Kontexte und externe Vault-Git-Worktrees unterstützt diese Fassung nicht.
3. Eigene laufende Compose-DB: Dienst `db`, Datenbank und Rolle `hindsight`,
   Container-Benutzer `postgres`, `pg_dump` und `pg_restore` vorhanden. Passend zum
   [Hindsight-Rezept](../generic-main-agent-maker/references/hindsight.md) liegt
   `HINDSIGHT_DB_PASSWORD` bereits in der DB-Containerumgebung. Der Dump nutzt
   die eigene App-Rolle über Container-Loopback mit SCRAM, nicht einen
   passwortlosen Socket. Fehlendes/falsches Passwort bricht ab, ohne Rückfrage
   oder Fallback. Niemals zur Backup-Einrichtung Authentifizierung abschwächen.
   Anders als das manuelle Admin-Dump-Beispiel des Rezepts bleibt dieser Helper
   bei `db_user=hindsight`: die App-Rolle muss alle eigenen Anwendungsobjekte
   lesen können. Fehlende Rechte sind ein Abnahmeblocker, kein automatischer
   Wechsel zum Adminpasswort.
4. Tatsächliche Zielinstanz anhand ihrer bestehenden Konfiguration auflösen,
   nicht pauschal `~/.hermes` verwenden. Alle Quellen müssen im eigenen Home
   liegen; Hermes-Home, Vault, Compose-Verzeichnis und Backupziel dürfen sich
   weder enthalten noch identisch sein. Compose-Datei und zusätzliche Betriebs-
   konfiguration liegen in einem eigenen Verzeichnis außerhalb des Hermes-Homes.
5. Vor dem ersten Lauf die Aufnahmegrenzen in [Umfang](references/scope.md)
   abgleichen. Nicht gelistete Restore-Abhängigkeiten sind ein Abnahmeblocker,
   kein Anlass für einen rekursiven Home-Scan. Fremde Inhalte nicht übernehmen.
6. Einrichtungsfreigabe umfasst Quelllesezugriffe, lokale Docker-DB-Dumps,
   geschützte Backupdateien, den täglichen Job und **nur dessen 30-Tage-Rotation**.
   Beim Maker-Kickoff diesen begrenzten Löschumfang erklären und freigeben lassen;
   eine dokumentierte passende Freigabe nicht pro Schritt erneut erfragen.
   In-place-Restore und tatsächliche isolierte Restore-Probe separat freigeben.

## Einrichtung nach Freigabe

- [config.example.json](config.example.json) als lokale
  `$HERMES_HOME/backup-config.json` mit Modus `0600` anlegen. Alle `REPLACE`-Werte
  durch die tatsächlich ermittelten absoluten Pfade/Projektkennung ersetzen.
  Keine Tilde, keine Variablen und keine Credentials im JSON. Unbekannte oder
  zusätzliche Felder werden abgelehnt. Compose-Projekt: Kleinbuchstaben,
  Ziffern, `_`, `-`, erstes Zeichen alphanumerisch.
- `backup_root` ist exakt `<eigenes Home>/backups/<eindeutige-instanz>`.
  Einen neuen stabilen Namespace wählen; nie einen fremden bestehenden Ordner
  übernehmen. `~/backups` und Namespace müssen `0700` haben und dem Benutzer
  gehören. Bestehende Rechte nicht ungefragt ändern; Konflikte vorlegen.
- Default: **täglich 03:00 lokale Systemzeitzone, 30 Tage Aufbewahrung**.
  Tatsächlich erkannte Zeitzone anzeigen, nicht ändern. Keine Auswahlabfrage.
- [scripts/backup.py](scripts/backup.py) ist das deterministische, LLM-freie
  Programm. Für den Cron kopiert der freigegebene Maker es nach
  `$HERMES_HOME/scripts/local-backup.py` und erzeugt dort einen kleinen Wrapper,
  der den geprüften absoluten Python-Pfad sowie den absoluten JSON-Pfad verwendet.
  Nicht nur das Skill-Verzeichnis als Cronziel angeben.
- Native Hermes-Cronanlage anhand der aktuellen offiziellen Dokumentation:
  `no_agent`, Wrapper **innerhalb des aufgelösten `$HERMES_HOME/scripts/`**,
  `--script` bekommt einen Dateinamen, **keine Kommandozeile**. Genau ein Job,
  aktive Zustellung an den eingerichteten Benutzerkanal, kein LLM-Prompt. Der
  Maker verwaltet diesen Job; dieses Paket installiert keine Systemjobs.
- Bereinigte Cron-Umgebung berücksichtigen: keine geerbten Secrets notwendig.
  Docker Compose liest seine lokale `.env`; das Hindsight-Rezept reicht nur
  explizite Variablen an die Container weiter, keine zusätzliche `env_file`-
  Durchreichung ergänzen. Keine `.env` als Shellskript ausführen. Das Backup
  setzt einen minimalen Unterprozess-ENV. Erst die Container-Shell setzt
  `PGPASSWORD` aus `HINDSIGHT_DB_PASSWORD`; keine Secretwerte in Host-Argumenten,
  Ausgaben oder Manifest. Der Dump enthält keine Clusterrollen/Passwörter;
  Rollen und Rechte werden beim Restore separat geprüft.
- Direkter manueller Aufruf, erst bei späterer ausdrücklich freigegebener Nutzung:

  ```text
  /ABS/PYTHON3 /ABS/SKILL/scripts/backup.py --config /ABS/HERMES_HOME/backup-config.json
  ```

  Alle Platzhalter vorher auflösen. Erfolg: Exit `0`, **stdout und stderr leer**.
  Fehler einschließlich Locksperre: knappe generische Meldung auf stderr,
  Exit ungleich `0`. Unterprozess-Ausgaben und Exceptiondetails werden nicht
  weitergegeben. Hermes liefert Fehler/Timeouts; diese Zustellung später separat
  testen. Ein vollständig erzeugter Satz mit Rotationsfehler führt ebenfalls
  zu einer Fehlermeldung, nicht zu verborgenem Teil-Erfolg.

## Sicherheitsmodell und Grenzen

- `flock` verhindert parallele Läufe innerhalb desselben Namespace. Eindeutige
  UTC-Zeitstempel plus UUID verhindern Überschreiben; `INCOMPLETE.json` kennzeichnet
  laufende/abgebrochene Sätze. `COMPLETE.json` entsteht erst nach Archiv-, Hash-
  und Dump-Listenprüfung. Jeder Satz und seine Archive sind `0700`/`0600` geschützt.
- Rotation löscht ausschließlich ältere verifizierte Sätze dieses Namespace
  nach einem neuen vollständigen Satz und erst bei Alter **größer 30 Tage**.
  Der neue letzte erfolgreiche Satz, unbekannte Dateien, Fremdverzeichnisse,
  Symlinks und unvollständige Sätze bleiben erhalten. Keine rekursive Löschung.
- Symlinks, Hardlinks, Spezialdateien und Dateisystemwechsel im Quellbaum führen
  zum Abbruch. Ausgewählte Dateien werden nicht automatisch außerhalb der
  Allowlist gesucht. Gleichartige Bind-Mounts auf demselben Dateisystem und
  absichtlich konkurrierende Änderungen desselben Benutzers kann dieses kleine
  Programm nicht zuverlässig isolieren: Quellen vorher prüfen, keine fremden
  Mounts, schreibbaren gemeinsamen Verzeichnisse oder untrusted Hooks zulassen.
- SQLite wird über die Backup-API gesichert, WAL/SHM/Journal nicht roh kopiert.
  Einzeldatenbanken sind konsistent; zwischen Hermes, Vault und PostgreSQL besteht
  **kein global atomarer Zeitpunkt**. Für eine übergreifende konsistente Probe
  Schreibaktivität nach Freigabe pausieren. Laufende Dateiumbenennungen können
  einen Lauf sicher abbrechen oder zwischen Auflistungen liegen.
- Ein `pg_restore --list` ist **kein Restore-Test**. Siehe getrennte Abnahme unten.
- Alle Archive sind vertraulich, auch Sessions und Vault. Separates Sensitive-
  Archiv bedeutet **keine Verschlüsselung**. Benutzer müssen Secrets aus normaler
  Konfiguration, Notizen und Git heraushalten. Hashes erkennen Veränderungen,
  beweisen ohne getrennt vertrauenswürdige Referenz aber keine Authentizität.
- Leere Verzeichnisse, ursprüngliche Unix-Modi und Besitzer werden nicht
  wiederhergestellt; extrahierte Dateien erhalten sicher `0600`, Verzeichnisse
  `0700`. Ausführungsrechte nur gezielt nach Codeprüfung wieder vergeben.
- Gleicher Host bedeutet keinen Schutz vor Host-/Datenträgerverlust. Geschützte
  Remote-Spiegelung ist Benutzersache; keine automatische Cloud- oder Syncanlage.

## Verifikation und Abnahme

Bei späterer Einrichtung getrennt dokumentieren:

1. Native Auffindbarkeit/Laden dieses vollständigen Skills; genaue Quellliste,
   Pfade, DB-Zuordnung und Ausschluss anderer Profile geprüft.
2. Ein echter vollständiger Backup-Lauf, Exit `0`, leeres stdout, passender
   Eigentümer/Modus, `COMPLETE.json`, Manifest und alle Hashprüfungen erfolgreich.
3. Isolierte Extraktion und SQLite-Integrität, echter PostgreSQL-Restore in
   separater temporärer Docker-DB, geprüfte Git-Historie und Stichproben.
4. Hindsight-API-/Retain-/Recall-/Reflect-Prüfung gegen die **Test-DB**, nicht
   gegen Produktion. Fehlende Modellanbindung als offene Funktionsabnahme nennen.
5. Genau ein aktiver 03:00-Job, lokale Zeitzone, betriebsbereiter Scheduler,
   erfolgreicher stiller Lauf und nachgewiesene secretfreie Fehlerzustellung.
   Rotation erst in eigens genehmigten synthetischen Testdaten testen.

**Paketstand:** Nur Dateien und statische Prüfungen; weder Backup noch Helper,
Docker, Hermes-Cron, SQLite-Snapshot oder Restore wurden hier ausgeführt.
Reine AST-/Textregression: `python3 skills/local-backup-restore/tests/check_static.py`
im Repository. Dieser Test importiert und startet keine Pakethelfer.
Das Backup-Skript überschreitet bewusst 250 Zeilen: Pfadprüfung, Archivprüfung,
SQLite-Snapshots und konservative Rotation werden nicht zugunsten einer
künstlichen Zeilengrenze entfernt. Keine getestete Betriebsreife behaupten.

## Quellen und Herkunft

Eigene Implementierung und deutschsprachige Anleitung, MIT, Max / Hermes Agent.
Die Quellen dienen bei späterer Verwendung zur Prüfung der installierten Version;
kein Anspruch, sie während der reinen Paketerstellung live abgerufen zu haben.

- [Hermes-Dokumentation](https://hermes-agent.nousresearch.com/docs/), dort aktuelle
  Cron-/Scheduling-Anleitung sowie Profil- und Datenpfade prüfen.
- [SQLite Python Backup-API](https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.backup).
- [Python tarfile](https://docs.python.org/3/library/tarfile.html): keine ungeprüfte Extraktion.
- [PostgreSQL pg_dump](https://www.postgresql.org/docs/current/app-pgdump.html)
  und [pg_restore](https://www.postgresql.org/docs/current/app-pgrestore.html).
- [Docker Compose exec](https://docs.docker.com/reference/cli/docker/compose/exec/).
- [Hindsight](https://hindsight.vectorize.io/): Funktionsabnahme getrennt vom DB-Dump.
