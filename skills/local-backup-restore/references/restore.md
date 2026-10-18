# Wiederherstellung: erst isoliert, niemals Test über Live-Daten

Diese Anleitung wird bei der Paketerstellung **nicht ausgeführt**. Erst später
nach Prüfung der Quellen und ausdrücklicher Freigabe anwenden. Die SOUL bleibt
maßgeblich. Ein Backup-Erfolg, eine Hashprüfung und `pg_restore --list` sind
jeweils schwächere Aussagen als ein tatsächlich erfolgreicher Restore.

## 1. Vertrauenswürdigen Satz auswählen und offline prüfen

- Satz mit `COMPLETE.json` und bekanntem Namespace wählen; Herkunft, Eigentümer
  und private Rechte prüfen. Den Satz während der Prüfung nicht verändern lassen.
- Hashreferenz aus vertrauenswürdiger Sicherung verwenden. Ein Angreifer kann
  Payload und ungeschützten Manifest-Hash gemeinsam ersetzen. Dump-Restore kann
  SQL-Code ausführen: unbekannte Dumps nicht in eine vertrauenswürdige Umgebung laden.
- Genügend freien Platz für vollständige Extraktion und Test-DB sicherstellen.
  Diese Helper sind kein Sandbox-/Archivbomben-Scanner für beliebige Fremdarchive.
- `backup.py` und `verify_extract.py` aus demselben geprüften Paket nebeneinander
  behalten. Python 3.11+ benutzen. Der Helper importiert die Prüffunktionen,
  **ruft die Backup-Funktion nicht auf** und kontaktiert weder Docker noch APIs.

Erst nach Ersetzen sämtlicher Platzhalter:

```text
/ABS/PYTHON3 /ABS/SKILL/scripts/verify_extract.py --set /ABS/BACKUPSET --output /HOME/DES/BENUTZERS/NEUER_PRUEFORDNER
```

Der Zielordner muss ein **noch nicht vorhandenes direktes Kind des eigenen
Homes** sein, getrennt von allen ursprünglichen Quellen und Sicherungen. Der
Helper prüft die vollständige Dateiliste, Manifest-Hash, alle Payload- und
Dateihashes. Absolute Archivpfade, `..`, doppelte Mitglieder, Symlinks,
Hardlinks und Spezialdateien werden verworfen. Kein `extractall`: reguläre
Dateien werden exklusiv (`xb`) in den neuen Baum geschrieben und nochmals
gehasht. Zielpfade werden gegen Traversal geprüft. Alle Verzeichnisse `0700`,
Dateien `0600`; keine Owner/Execute-Bits aus dem Archiv übernehmen.

Nur `EXTRACTED.ok` plus erfolgreicher Exit bestätigt die Offline-Prüfung.
Bei Fehlern Teilverzeichnis nicht verwenden; kein automatisches Löschen.
`hermes/`, `vault/`, `service/` und `hindsight.dump` liegen danach im Prüfbaum.
Secrets nie ausgeben, Git-Hooks nie ausführen und wiederhergestellte Skripte
nicht starten. Python-SQLite-Dateien einzeln read-only öffnen und
`PRAGMA integrity_check` auf exakt `ok` prüfen; Session-/Memory-Stichproben ohne
private Inhalte im Bericht. Vault-Dateien und Git-Objekte/Referenzen überprüfen,
beispielsweise `git -C /ABS/PRUEF/vault fsck --full` nach Prüfung der Git-Konfig.
Git-Filters/Hooks und remotes dabei nicht ausführen oder kontaktieren.

## 2. Echter PostgreSQL-Restore in neuer temporärer Docker-DB

Voraussetzungen separat prüfen und genehmigen:

- Ein lokal vorhandenes, vertrauenswürdiges **digest-gepinntes pgvector-Image**,
  zunächst genau der Quellstand des Hindsight-Rezepts: PostgreSQL **18**,
  Kandidat `pgvector/pgvector:0.8.7-pg18-bookworm` mit tatsächlich geprüftem
  Digest. Dump-/Serverversion und Extensions vorher nachvollziehen; nicht blind
  `latest` oder eine ältere Major-Version verwenden.
- Keine Live-Compose-Datei für diese Probe benutzen. Neuer eindeutiger Container,
  kein Host-Home, keine Produktions-Secrets, kein Docker-Socket im Container, keine
  Produktionsvolumes, kein veröffentlichter Port, `--network none`.
- Die folgenden Mounts entsprechen PostgreSQL 18: `VOLUME /var/lib/postgresql`
  und explizites `PGDATA=/var/lib/postgresql/18/docker`. Image-Metadaten vorher
  gezielt prüfen. Abweichende PGDATA-/VOLUME-Pfade gezielt
  anpassen; nicht ungeprüft andere oder anonyme persistente Volumes akzeptieren.
- Daten in tmpfs; Größe an geprüften Restore-Bedarf anpassen. Nicht ausreichend
  RAM? Mit Freigabe eigenes einmaliges Testvolume verwenden und dessen Namen
  samt gezieltem Löschschritt dokumentieren. Niemals ein vorhandenes Volume nutzen.

Beispiel für die spätere bewusste Ausführung in Bash; keine echten Credentials
enthalten. `IMAGE`, `DUMP` und `TEST_ENV` vorher durch verifizierte Werte ersetzen.
`TEST_ENV` ist eine neue Datei im geschützten Prüfbaum, nicht die produktive
`.env`. Einmaliges Testpasswort direkt in diese Datei erzeugen; weder ausgeben
noch als Shellvariable/Argument verwenden. Shell-Tracing bleibt abgeschaltet:

```bash
set -euo pipefail
D=(docker --host unix:///var/run/docker.sock)
IMAGE='REPLACE_APPROVED_PGVECTOR_IMAGE@sha256:REPLACE_VERIFIED_DIGEST'
DUMP='/ABS/NEUER_PRUEFORDNER/hindsight.dump'
TEST_ENV='/ABS/NEUER_PRUEFORDNER/restore-test.env'
umask 077
python3 - "$TEST_ENV" <<'PY'
import os
from pathlib import Path
import secrets
import sys
os.umask(0o077)
with Path(sys.argv[1]).open('x', encoding='utf-8') as f:
    f.write('POSTGRES_PASSWORD=' + secrets.token_hex(32) + '\n')
PY
TEST="restore-probe-$(python3 -c 'import uuid; print(uuid.uuid4().hex)')"
"${D[@]}" run --pull=never --detach --name "$TEST" \
  --label local-backup-restore.probe=true \
  --network none --read-only --memory 3g --cpus 2 --pids-limit 256 \
  --tmpfs /tmp:rw,nosuid,nodev,size=64m \
  --tmpfs /var/run/postgresql:rw,nosuid,nodev,size=16m \
  --tmpfs /var/lib/postgresql:rw,nosuid,nodev,size=2g \
  -e PGDATA=/var/lib/postgresql/18/docker \
  -e POSTGRES_USER=hindsight -e POSTGRES_DB=hindsight \
  -e 'POSTGRES_INITDB_ARGS=--auth-host=scram-sha-256 --auth-local=scram-sha-256' \
  --env-file "$TEST_ENV" "$IMAGE"
```

Auch die wegwerfbare Test-DB bleibt bei **SCRAM**, kein `trust`-Fallback.
Nur Docker übergibt das neue Testpasswort per Containerumgebung; die folgenden
Clientaufrufe expandieren es erst dort in `PGPASSWORD`. Vor Fortsetzung
mit gezielten Inspect-Feldern (Name/ID, Labels, NetworkMode, Mounts, PortBindings;
niemals `.Config.Env` oder vollständiges Inspect) genau diese Testinstanz prüfen;
unerwartete Mounts oder Portfreigaben bedeuten Abbruch. Keine pauschalen
Containerlisten oder fremden Konfigurationen in Berichte kopieren.

Bereitschaft prüfen, bei anfänglichem Startzustand begrenzt erneut probieren:

```bash
"${D[@]}" exec --user postgres "$TEST" pg_isready -U hindsight -d hindsight
```

Erst bei erfolgreichem Readiness-Exit tatsächlich restaurieren:

```bash
"${D[@]}" exec -i --user postgres "$TEST" \
  sh -eu -c 'PGPASSWORD="${POSTGRES_PASSWORD:?}" exec pg_restore -w -U hindsight -d hindsight --exit-on-error --no-owner --no-privileges' < "$DUMP"
"${D[@]}" exec -i --user postgres "$TEST" \
  sh -eu -c 'PGPASSWORD="${POSTGRES_PASSWORD:?}" exec psql -w -X -U hindsight -d hindsight -v ON_ERROR_STOP=1' <<'SQL'
SELECT extname, extversion FROM pg_extension ORDER BY extname;
SQL
```

Vor dem Restore noch einmal Containeridentität prüfen. Es gibt absichtlich kein
`--clean` und keinen Befehl gegen das Live-Projekt. Restore-Ausgaben können
Datenbankinhalte enthalten: lokal geschützt behandeln, nicht ungeprüft an den
Chatkanal zustellen. Fehler secretfrei zusammenfassen.

Erfolgskriterien: `pg_restore` Exit `0`, erwartete Extensions einschließlich
pgvector, erwartetes Schema, Bankzuordnung und repräsentative Datenzählungen.
Für tatsächliche vorhandene Tabellen anhand des wiederhergestellten Schemas
prüfen; keine geratenen Hindsight-Tabellennamen als erfolgreiche Prüfung ausgeben.
Testrolle ist hier die eigene Initialrolle, Quell-ACLs/Ownership werden bewusst
nicht restauriert; Rechtewiederherstellung ist eine eigene spätere Abnahme.

Nach abgeschlossener Probe genau diesen Container entfernen. Den gespeicherten
Namen und Label zuvor erneut prüfen; keine globale Prune-/Volume-Bereinigung:

```bash
"${D[@]}" inspect --format '{{ index .Config.Labels "local-backup-restore.probe" }}' "$TEST"
# Nur wenn Label == true und Name/ID dem gerade angelegten Container entsprechen:
"${D[@]}" rm --force "$TEST"
```

Bei Prozessabbruch bleibt der Testcontainer möglicherweise bestehen. Namen/ID
lokal festhalten, später nur dieses Objekt nach Prüfung aufräumen. Extrahierte
Secrets im Prüfbaum ebenfalls erst nach eigener gezielter Löschfreigabe entfernen.
Das gilt auch für `restore-test.env`; niemals in Git/Vault oder Berichte aufnehmen.

## 3. Funktionale Hindsight-Abnahme ist separat

Die isolierte DB-Probe beweist kein laufendes Hindsight-API-/Modellverhalten.
Für eine echte Funktionsprobe einen **eigenen** Testdienst derselben freigegebenen
Hindsight-Version samt separater Konfiguration ausschließlich an die Test-DB
binden. Niemals die Live-API auf den Prüfsatz umkonfigurieren. Testbanken nicht
mit fremden Banken zusammenführen. Modellzugriff kann Daten extern verarbeiten
und Kosten verursachen; Netzfreigabe und Zielendpunkte vorher erklären.

Im vollständig netzlosen DB-Test sind API-/Modellprüfungen **offen**. Ein separater
API-Test benötigt einen kontrollierten isolierten Netzweg; nicht beiläufig die
Netzwerksperre aufheben. Bekannte eigene Bank lesend prüfen (Recall/Reflect),
anschließend Retain/Recall/Reflect mit eindeutig neuen synthetischen Inhalten
in einer eigenen Testbank und Konsolidierung prüfen. Tatsächliche Ergebnisse,
DB-Zuordnung und Persistenz dokumentieren. Keine erfundenen Erfolgsausgaben.

Für diese getrennte Vollprobe gilt der Restore-Auftrag im
[Hindsight-Rezept](../../generic-main-agent-maker/references/hindsight.md):
eigenes Projekt/Volume, freier anderer Loopback-DB-Port, Initialisierung von
App-Rolle/Extensions aus dem geprüften `init-db.sh`, Restore mit `--role=hindsight`
und explizite Rechteprüfung. Das obige netzlose Minimalbeispiel ersetzt diese
Topologie- und Rechteabnahme nicht. Die separate API braucht einen **anderen
freien API-Port**; Command, Healthcheck, DB-DSN und Client-URLs gemeinsam anpassen
und vor Start gegen das Live-Inventar prüfen. Wiederhergestelltes `check.py`
nicht unverändert starten: es ist auf `127.0.0.1:9177` festgelegt und würde
sonst die Live-API treffen. Produktives Hermes nicht für die Probe umschalten.

## 4. Produktiver Restore nur nach ausdrücklicher eigener Freigabe

Vor Überschreiben eines Zieles Quell-/Zielinstanz, Pfade, DB/Compose-Projekt,
Unterbrechung, konkrete Dateien, Geheimnisse, Rückweg und Löschumfang vorlegen.
Bevorzugt neue Zielinstanz statt In-place-Restore. Vorzustand separat sichern;
Dienste/Schreiber nach Freigabe stoppen, Scheduler zunächst deaktiviert lassen.

Nur den geprüften Extraktionsbaum übernehmen, keine ungeprüfte Tar-Extraktion
über das Live-Home. SQLite nur bei gestopptem Ziel einsetzen; alte WAL/SHM-Dateien
nicht mit neuen Snapshots mischen. Konkrete Sidecar-Entfernung mitfreigeben lassen.
Sensitive Dateien `0600`, Verzeichnisse `0700`, Eigentümer und gezielt nötige
Ausführungsrechte prüfen. Fehlende leere Verzeichnisse gezielt neu anlegen.
Insbesondere das geprüfte, geheimnisfreie `service/init-db.sh` vor Initialisierung
des neuen PG18-Volumes gezielt auf `0755` setzen, wie im Hindsight-Rezept;
`.env` bleibt `0600`. `hermes/hindsight/config.json`, `maker/environment.json`
und `maker/state.json` auf die neue Zielbindung prüfen. Gespeicherte `verified`-
Statuswerte und alte Cron-IDs sind kein Nachweis für den wiederhergestellten Betrieb.

Compose/API-Konfiguration, lokale Dienstdefinitionen, venv und Hermes-Version
über geprüfte Originalquellen wiederherstellen; das Backup ist kein
Betriebssystem-/Dependency-Abbild. Nur die eigene DB restaurieren; produktive
Rollen/ACLs und Extensions ausdrücklich abnehmen. Erst dann eigene Hermes-/
Hindsight-Dienste starten, API-/Session-/Vault-Funktion prüfen, Cronziel und
03:00-Zeitplan auf neue Pfade abstimmen. Bei abweichender Konfiguration neuen
Backup-Namespace wählen, keine alten Besitzmarker umschreiben.

Erst vollständiger Funktionstest erlaubt „Restore erfolgreich“. Offline-, DB-,
API-, Rechte- und Scheduler-Prüfung getrennt berichten; fehlende Freigabe oder
Modellanbindung ist eine konkrete offene Grenze, kein stiller Erfolg.
