# Helper-Vertrag und spätere Abnahme

**Statusgrenze:** Diese Anleitung beschreibt erst später freizugebende Tests und Einrichtung. Beim Erstellen des Pakets werden weder Helper noch Maker, Cronjobs oder produktive Datenbankabfragen ausgeführt. Statische Prüfung ist kein Funktionstest.

## 1. Eingaben explizit binden

Der Einrichtungsagent ermittelt den echten Datenpfad **der Zielinstanz**, ihre lokale IANA-Systemzeitzone und den bestehenden Vault. Ein aktives `HERMES_HOME` kann dabei helfen, ersetzt aber nicht die Prüfung der tatsächlichen Instanzzuordnung. Kein Default auf eine andere Instanz, keine Profilschleife, keine Suche nach allen Datenbanken. Die Eingaben in lokaler Konfiguration festhalten, nicht im portablen Paket.

Der Aufruf aus dem Paketverzeichnis lautet später:

```text
python3 -B scripts/list_messages_for_date.py --db "<DB_ABSOLUT>" --date "<YYYY-MM-DD>" --timezone "<IANA_ZONE>"
```

Die drei Platzhalter durch geprüfte Werte ersetzen. `--db` akzeptiert nur einen absoluten bestehenden Dateipfad, kein `~` oder `$VAR`. `--date` ist strikt ISO-Kalenderdatum. `--timezone` ist etwa eine tatsächlich ermittelte IANA-Zone, kein geratenes `CET` und kein fest kodierter Offset. Python 3.9+ muss die Zone über `zoneinfo` finden; sonst Fehler statt stiller UTC-Ausweichwahl.

Das lokale Fenster ist `[00:00 des Tages, 00:00 des Folgetags)`. Beide Mitternachtsgrenzen werden separat in UTC-Epochsekunden umgerechnet. Sommerzeit-Tage können 23 beziehungsweise 25 Stunden haben. Bei historischen Zonen mit nicht existierender Mitternacht bricht der Helper explizit ab; eine mehrdeutige Mitternacht verwendet die erste Ausprägung (`fold=0`).

## 2. Geprüfte Schema-Grundlage

Quellprüfung ohne Öffnen produktiver Sitzungsinhalte: Hermes-Quellstand `d923a5eb487a17c0a68801bba9ef0f56c81040a8`, insbesondere:

- `hermes_state_common.py`: `sessions.id TEXT PRIMARY KEY`; `messages.id INTEGER PRIMARY KEY`, `session_id TEXT`, `role TEXT`, `timestamp REAL NOT NULL`; Inhalts- und Reasoning-Spalten werden **nicht** gelesen.
- `hermes_state_messages.py`: Zeitwerte werden beim Schreiben über `_coerce_timestamp(..., time.time())` normalisiert.
- `hermes_cli/timefmt.py`: Unix-Epochsekunden, plausibler Bereich `0 .. 4200000000`.

Die [öffentliche Quelle](https://github.com/NousResearch/hermes-agent) und [offizielle Sitzungsdokumentation](https://hermes-agent.nousresearch.com/docs/user-guide/sessions) helfen bei späterer Versionsprüfung. Der lokale Quellstand ist Evidenz für diese Implementierung, keine Behauptung über jede zukünftige Hermes-Version.

Bei **jedem** Lauf prüft der Helper das echte Schema mit `PRAGMA table_info` read-only. Unterstützt werden numerische Unixsekunden mit deklarierter `REAL`- oder `INTEGER`-Zeitspalte. SQLite speichert in einer REAL-Spalte üblicherweise auch übergebene Integer als Zahl. Nicht unterstützt: ISO-Text, Millisekunden, Julian-Tage und unbekannte Spaltennamen. Solche Varianten nicht heuristisch umdeuten; Schema/Schreibquelle gezielt prüfen und den Helper erst nach bewusster Anpassung verwenden.

Ein zusätzlicher reiner Metadatencheck prüft die Zeitspalte auf ungültige Speicherwerte in der gewählten DB. Fehler auch außerhalb des angefragten Tages führen konservativ zum Abbruch, weil die Tageszuordnung sonst ungesichert ist. Keine Titel, Inhalte, Tool-Argumente oder anderen Sitzungen entnommenen Texte werden dafür gelesen. Das kann bei einer großen DB einen vollständigen Zeitspaltenscan erfordern; keine Indizes in der Live-DB anlegen.

## 3. Read-only und Snapshot

- `sqlite3.connect(...?mode=ro)` verhindert Datenbankerzeugung und SQL-Schreibzugriffe; zusätzlich `query_only=ON`, `trusted_schema=OFF` und eine Lesetransaktion für einen konsistenten Snapshot.
- Keine Hermes-Module importieren: keine Migration, kein Bootstrap, keine Profilinitialisierung.
- Kein `immutable=1`: damit könnten noch nicht checkpointete WAL-Nachrichten fehlen.
- Für eine WAL-Datenbank müssen `-wal` und `-shm` bereits vorhanden sein. Fehlen sie, bricht der Helper ab statt ihre Erstellung anzufordern. Er erzeugt weder Snapshot noch Sidecars selbst.
- SQLite kann vorhandenen Shared-Memory-Zustand und Lesesperren intern verwenden. „Read-only“ bedeutet hier keine Daten-/Schemaänderung, nicht garantiert bytegleicher SHM-Zustand. Für eine strikt schreibgeschützte Prüfung einen vom Betreiber bereitgestellten konsistenten Snapshot auf schreibgeschütztem Dateisystem verwenden. Keine ungeprüfte Kopie nur der Hauptdatei einer laufenden WAL-Datenbank verwenden.
- Lock-/Berechtigungsfehler melden; keine Reparatur, kein erzwungener Checkpoint, kein Abschalten des laufenden Dienstes. DB-Pfad und andere potenziell sensible Fehlerwerte werden nicht ausgegeben.

## 4. JSON-Vertrag

Erfolg: Exitcode `0`, genau ein JSON-Objekt auf stdout. Enthalten sind:

- `ok: true`, `contract_version: 1`, `date`, `timezone`;
- `window`: lokale Grenzen mit Offset und entsprechende `start_epoch`/`end_epoch`;
- `timestamp_storage: "unix_seconds_numeric"`;
- `available_flags`: tatsächlich vorhandene optionale Markierungen;
- `coverage: "all_stored_message_rows_in_window_not_all_lifetime_activity"`;
- `session_count`, `message_count`, `sessions`;
- je Sitzung `session_id`, `message_count`, `messages`;
- je Nachricht `id`, `role`, `timestamp_epoch`, `timestamp_utc`, `timestamp_local`, `flags`.

`flags` enthält vorhandene Werte von `_compressed_summary`, `active`, `compacted`. Sie dienen der Einordnung, nicht einem pauschalen Ausschluss: kompaktierte Originalnachrichten können gerade die gesuchte Tagesarbeit enthalten. Alle gespeicherten Rollen und Zeilen im Zeitfenster werden aufgezählt, auch System-/Tool-Nachrichten. Kein Filter auf `sessions.started_at`, `last_activity_at` oder aktive Sitzungen. Reihenfolge: Sitzungs-ID, innerhalb einer Sitzung Zeit und Nachrichten-ID.

Fehler: Exitcode `2`, `{"ok":false,"error":{"code":"…","message":"…"}}`, keine Teilerfolgsliste. Auch falsche Argumente erzeugen diesen Fehlervertrag; `--help` ist die normale argparse-Hilfe, kein Datenlauf. Bei einem Prozessabbruch oder ungültigem JSON ebenfalls nicht von Erfolg ausgehen.

Keine Inhalte, Titel, Benutzernamen, Modellangaben, DB-Pfade oder Secrets sind Ausgabefelder. IDs und Zeiten bleiben sensible Metadaten und werden nicht öffentlich veröffentlicht. Es gibt keinen stillen Treffer-Cap. Große Ergebnisse in eine geschützte, aufgabeneigene Arbeitsdatei außerhalb des Vaults umleiten, in kleinen Sitzungsbatches lokal parsen und nur benötigte IDs ans Modell geben. Nicht rohe JSON-Gesamtausgabe als Kontext laden. Der Helper hält die Metadaten des Tages im Speicher; extrem große Tage können Ressourcenlimits erreichen und müssen als Fehler nachbearbeitet werden.

## 5. Inhalt ausschließlich über native Sitzungssuche

Die bei Erstellung geprüfte native `session_search`-Schnittstelle bietet Sitzungsanker (`session_id`, `around_message_id`, `window`) und `role_filter`. Vor Lauf deren aktuelles Schema prüfen. Im Zielprofil ausführen und `profile` weglassen; kein Profilwechsel und kein Fallback. Deckt die native Suche eine angefragte ID nicht ab, ist das eine sichtbare Lücke.

`after`/`before` der Suchfunktion begrenzen nach aktuellem Schema den **Sitzungsbeginn**, nicht einzelne Nachrichtentimestamps. Browse, Suchlimit und Bookends beweisen keine Tagesvollständigkeit. Daher Metadaten-Helper für die vollständige Tagesliste, native Ankerfenster für den Inhalt.

Praktischer Umfang: zunächst höchstens 10 Sitzungen pro Batch, Fenster mit zwei Nachbarn je Seite. Benötigte Nachrichten-IDs und bereits geprüfte IDs lokal als kleine Arbeitsliste führen. Inhaltsfenster können tagefremde Nachbarn enthalten; anhand der Helper-ID-Liste filtern, bevor daraus Tagesereignisse abgeleitet werden. Unnötige Volltranskripte, Reasoning und Tool-Dumps nicht abrufen. Ein einzelner großer Nachrichteninhalt kann trotz kleinem Fenster groß sein: vorhandene native Kürzung/Paginierung nutzen und fehlende Abdeckung kennzeichnen, nicht unbegrenzt nachladen.

Anfang und Ende sind Einstiegspunkte, kein Beleg für die Mitte. Wesentliche Benutzer-/Assistant-Abschnitte und Themenwechsel des Tages über weitere Anker abdecken. Nicht gelesene, nicht verfügbare oder gekürzte Abschnitte ausdrücklich unter „Quellenlage“ als Lücke nennen. Eine vollständige Summary erst behaupten, wenn die relevanten Tagesbereiche tatsächlich geprüft sind. Geklonte Kompressions-/Fortsetzungszeilen anhand gelesener Inhalte zusammenführen, nicht mehrfach als Erfolg zählen. Gespeicherte Zeitstempel belegen den Speicherzeitpunkt, nicht zwingend den realen Zeitpunkt eines erwähnten Ereignisses.

Bei erfolgreicher Nullmenge keinen Inhalt erfinden. Bei vorhandenen ausschließlich technischen/Routine-Nachrichten diese von einer Nullmenge unterscheiden. Bereits gelöschte oder nie gespeicherte Nachrichten lassen sich damit nicht nachweisen.

## 6. Spätere statische und synthetische Prüfung

Vor jeder Installation Hauptskill, Referenzen und Skript vollständig lesen. Zur reinen Syntaxprüfung ohne Ausführung und ohne Bytecode-Dateien eignet sich `ast.parse` auf dem eingelesenen Skript. Keine Imports des Helpers, kein `runpy`, kein Aufruf von `--help` als angeblich statischer Test.

**Erst bei später freigegebenen Funktionstests** in einem eigenen Testverzeichnis eine synthetische SQLite-DB erzeugen, niemals echte Chatdaten kopieren. Minimales Schema:

```sql
CREATE TABLE sessions (id TEXT PRIMARY KEY, started_at REAL NOT NULL);
CREATE TABLE messages (
  id INTEGER PRIMARY KEY,
  session_id TEXT NOT NULL REFERENCES sessions(id),
  role TEXT NOT NULL,
  content TEXT,
  timestamp REAL NOT NULL
);
```

Datum z. B. `2025-01-15`, Zone `Europe/Berlin` nur als synthetischer Test. Grenzen mit `datetime.combine(..., tzinfo=ZoneInfo(...)).timestamp()` für beide lokalen Mitternachten bestimmen. Eine Sitzung bereits vor der Startgrenze beginnen lassen. Nachrichten `1` bis `4` jeweils bei `start-1`, `start`, `end-1`, `end` einfügen; Inhalt nur `SYNTHETISCH`. Erwartet sind **genau IDs 2 und 3** derselben Sitzung. Helper über die oben dokumentierte Schnittstelle ausführen, JSON parsen, IDs und Zähler mit Assertions prüfen; nicht nur visuell nach `ok` suchen.

Weitere Pflichtfälle bei späterer Abnahme:

| Fall | Erwartung |
|---|---|
| Leere gültige DB | Exit 0, beide Zähler 0, `sessions: []` |
| Zwei Sitzungen, eine beginnt vor dem Tag | Alle und nur Nachrichten im Fenster enthalten |
| `Europe/Berlin`, `2025-03-30` / `2025-10-26` | Fenster 23 / 25 Stunden; wiederholte Stunde enthält beide Zeitpunkte |
| Wiederholter identischer Aufruf | Gleiches JSON bei unveränderter DB |
| Fehlende DB oder falsche Pflichtspalte | Exit 2, kein Ergebnis und keine erzeugte DB |
| Text-/Millisekunden-Zeitwerte | Exit 2 statt still leerer Trefferliste |
| Verwaiste Nachricht / unbekannte Rolle | Exit 2, keine unbemerkte Auslassung |
| Optionale Kompressionsflags vorhanden/fehlend | Ausgabe nennt vorhandene Flags; Originalzeilen bleiben enthalten |
| Synthetisches `content` mit vertraulichem Testmarker | Marker niemals im JSON; Inhalt wird nicht selektiert |
| Live-WAL-Fixture mit bereits vorhandenen Sidecars | Nicht checkpointete Tagesnachricht sichtbar; Hauptdaten unverändert |
| WAL-Sidecars fehlen oder DB gesperrt/unlesbar | Ehrlicher Fehler, keine Reparatur und kein Fallback |

Nach Tests Dateien/Hashes der synthetischen Hauptdatenbank und Schemainhalt vergleichen; bei WAL ausdrücklich SQLite-Sperr-/SHM-Verhalten berücksichtigen. Erst solche Ergebnisse belegen Funktion. Dieses Paket enthält keine Behauptung, diese Tests seien bereits ausgeführt.

## 7. Spätere Einrichtung durch Eltern-/Einrichtungsagent

1. Zielinstanz, Vault, lokale IANA-Zeitzone und native Skill-Verfügbarkeit prüfen. Beide Pakete einschließlich Referenzen müssen tatsächlich geladen werden können.
2. Aktuelle offizielle Scheduler-Dokumentation über den [Dokumentationsindex](https://hermes-agent.nousresearch.com/docs/llms.txt) und die native Job-Schnittstelle prüfen; diese Paketdatei erfindet keine Cron-API.
3. Nur Jobs der Zielinstanz lesen. Genau den passenden vorhandenen Daily-Summary-Job anhand Zweck, Instanz und Vault finden. Einen bereits passenden aktiven Job wiederverwenden. Konflikte/mehrere passende Jobs nicht ungefragt löschen.
4. Im freigegebenen Startsetup genau einen aktiven Job einrichten: **täglich 02:00 lokale Systemzeitzone, abgeschlossener Vortag, Skill `obsidian-daily-summary`**; DB, Vault und Zeitzone explizit binden. Kein zusätzliches „ob gewünscht?“, aber nötige Rechte-/Änderungsfreigaben bleiben erforderlich. Keine UTC-Verwechslung. Sommerzeitverhalten des Schedulers für ausgelassene/doppelte 02:00-Läufe prüfen; bei Auslassung den betroffenen Tag nachholen, bei doppeltem Lauf idempotent bleiben.
5. Exakten Job zurücklesen: aktiv, Zeitplan, Zeitzone, Skill und Bindung stimmen. Scheduler-Bereitschaft separat verifizieren. Weder kopierte Dateien noch ein gespeicherter Job beweisen die Ausführung.
6. Einen freigegebenen Lauf für den konkreten Vortag durchführen. Ergebnisnote und Daily-Hub lesen: tatsächliche Inhalte oder ehrliche Leermeldung, ein verwalteter Abschnitt, vorhandene Aufgaben/Logs/Metadaten erhalten. Kein künstliches Vortagsgespräch als echte Tätigkeit ausgeben.
7. Lauf mit demselben Datum wiederholen: keine doppelten Abschnitte oder Jobs, Nutzerinhalt außerhalb des Blocks unverändert. Bestehende unmarkierte Summary sowie fremde Markeränderungen separat als Konfliktfall testen, ohne sie zu überschreiben.
8. Pfad der Tagesnotiz, nachgewiesene Abdeckung, Job-ID, lokalen nächsten Lauf und offene Grenzen knapp dokumentieren. Bei Fehler keinen Aktivierungsabschluss behaupten. Nur notwendige Metadaten, keine DB-/Credential-Dumps.
