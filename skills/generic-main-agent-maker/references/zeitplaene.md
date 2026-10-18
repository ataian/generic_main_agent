# Verbindliche Zeitpläne

Nur der spätere Zielagent führt diese Schritte aus. Vorhandene Jobs zuerst lesen; Eigentum über Einrichtungsjournal und Zielinstanz bestimmen. Namen allein sind nicht eindeutig. Keine fremden Jobs ändern.

## Gemeinsame Voraussetzungen

- Eingerichteter Gateway läuft unabhängig vom Chat-Terminal; `hermes cron status` meldet funktionierenden Scheduler.
- Tatsächliche lokale IANA-Zeitzone lesen und im Journal sowie Summary-Prompt festhalten. Keine Änderung der Systemzeitzone. Hermes verwendet seine wirksame Instanzzeitzone: `HERMES_TIMEZONE`, dann `timezone` aus der Konfiguration, sonst Systemzeit. Sie muss mit dem ermittelten lokalen Kalender übereinstimmen. Fehlende explizite Instanzzuordnung nach Setupfreigabe über `hermes config set timezone <ERMITTELTE-IANA-ZONE>` setzen; widersprechende vorhandene Overrides zuerst klären. Keine erfundene `timezone`-Joboption verwenden. Den tatsächlichen Schedulerkontext und nächsten Lauf mit Offset kontrollieren.
- Aktuelle Schemas von `cronjob_manage` oder `hermes cron create --help` lesen; Zielprofil explizit binden. Zeitplan, aktiven Zustand, Zustellung und Skill-Zuordnung ausdrücklich setzen, nicht auf widersprechende Defaults hoffen. Aktuell erfolgt aktive Anlage mit `paused=false`, nicht mit einem erfundenen `enabled`-Toolparameter.
- Erzeugte IDs im Journal behalten. Bei Fortsetzung über IDs nachlesen; nicht blind neu erstellen. Bestehenden passenden Job aktualisieren, bei ungeklärtem Konflikt fragen.

## Daily Summary — 02:00

Verbindlich installieren und aktivieren: `obsidian-daily-summary`.

Jobname `Main Agent Daily Summary`, Zeitplan `0 2 * * *`, wirksame Instanzzeitzone wie oben, aktiv, Skill `obsidian-daily-summary`, Zustellung `local` (keine tägliche Nachrichtenflut), `failure_deliver` = bestätigtes Benutzerkanalziel. Modellauflösung prüfen: ohne Job-Pin gilt zuerst eine vorhandene `cron.model`-Vorgabe, sonst das Hauptmodell. Bestehende Abweichungen klären; weder Modell-Pins noch profilweite Cron-Defaults nebenbei ändern.

Der vollständige Jobprompt muss konkret enthalten:

> Fasse den abgeschlossenen Vortag in der lokalen Zeitzone [ermittelte IANA-Zone] zusammen. Nutze den Skill obsidian-daily-summary und seine Regeln. Ziel-Vault: [aufgelöster absoluter Vault-Pfad]. Ziel-Sitzungsdatenbank: [aufgelöstes HERMES_HOME]/state.db. Nur diese Instanz, keine anderen Profile; laufende Summary-Sitzung ausschließen. Auch am Vortag aktive ältere Sitzungen berücksichtigen. Vorhandene Tagesnotiz erhalten; eigenen Summary-Abschnitt idempotent ergänzen/aktualisieren und Hubs pflegen. Keine Geheimnisse. Keine Ereignisse erfinden, wenn noch keine Arbeit erfasst wurde. Keine weiteren Jobs anlegen. Bei Erfolg ausschließlich [SILENT]. Bei Fehler oder unvollständiger Pflichtarbeit [CRON_FAILURE] allein auf die erste Antwortzeile setzen und darunter den Fehler konkret und secretfrei melden; vorhandene Summary bei ungesicherter Datenbasis nicht ersetzen.

Die eckig beschriebenen Pfade und Zeitzone im Jobprompt ersetzen, nicht als Platzhalter speichern. Zeitzonen-/Datumsermittlung durch Werkzeug; keine mentale Datumsrechnung. Eine bloße Fehlerbeschreibung ohne `[CRON_FAILURE]` kann als erfolgreicher Agentenlauf verbucht werden. Fehlerziel separat zurücklesen und nach Freigabe harmlos testen.

Nach Erstellung Job readback, aktiven Zustand und nächsten Lauf prüfen. Einen Testlauf starten und bis zum terminalen Ergebnis verfolgen: asynchroner Start allein ist kein Erfolg. Tagesnotiz und Hub-Link nachlesen, Wiederholung auf doppelte Abschnitte prüfen. Bei frischer Installation ohne Vortagsdaten korrekten Leertag statt erfundener Summary dokumentieren.

## Backup — 03:00, ohne LLM

Zuerst den Skill `local-backup-restore` über native Discovery oder aus dem ursprünglichen Checkout laden und seine Konfiguration mit realen absoluten Pfaden anlegen. Script samt erforderlichen Hilfsdateien unter `<HERMES_HOME>/scripts/` bereitstellen. Ein kurzer Shell-Wrapper dort ruft den konkret bestimmten Python-Interpreter, das Backupskript und die Konfigurationsdatei auf; Pfade shell-sicher quotieren. Keine Secrets als Argumente.

Native Cron-Eigenschaften:

- Name `Main Agent Backup`.
- Zeitplan `0 3 * * *`, wirksame Instanzzeitzone wie oben, aktiv.
- `no_agent=true`, `script` = tatsächlicher Wrapper-Dateiname unter `<HERMES_HOME>/scripts/`.
- Keine Modell-/Skill-Inferenz für diesen Job.
- `deliver` = eindeutiges bestätigtes Ziel im eingerichteten Nachrichtenkanal, nicht unbestimmtes `origin` einer lokalen CLI-Sitzung.
- Erfolg: leeres stdout. Fehler: knappe secretfreie Meldung, Exit ungleich null. Zustellung von Fehlern mit einem harmlosen isolierten Testskript/temporären Testjob nach Freigabe prüfen; Produktionsbackup nicht künstlich beschädigen. Testjob anschließend deaktivieren und nach erlaubter Bereinigung entfernen.

Offizielle CLI-Form (konkrete Parameter vorher an Zielversion anpassen):

```bash
hermes cron create "0 3 * * *" --no-agent --script main-agent-backup.sh --deliver <BESTAETIGTES-KANALZIEL> --name "Main Agent Backup"
```

Wirksame Instanzzeitzone, Aktivierung und nächsten Lauf nachlesen. `--script` ist **ein Dateipfad, keine Kommandozeile**; die aufgelöste Datei muss innerhalb `HERMES_HOME/scripts` liegen. Provider-Secrets werden aus Cron-Subprozessen gefiltert; der Backupjob darf nicht auf ihre Vererbung angewiesen sein. Vorhandenes `failure_deliver=local` würde Fehleralarme unterdrücken: für diesen Job ausdrücklich dasselbe bestätigte Kanalziel wie `deliver` setzen.

Ersten vollständigen Lauf und isolierte Restore-Probe ausführen, anschließend Job-ID, nächsten Lauf, letzten Erfolg und Fehlerzustellung prüfen. Kein Erfolg nur anhand von Dateigröße oder `pg_restore --list`.

## Nicht automatisch einrichten

Kein Vault-Hindsight-Sync, kein Index-Watchdog, keine anderen Reports, keine Remote-Spiegelung und keine automatischen Updates.

## Quelle

https://hermes-agent.nousresearch.com/docs/user-guide/features/cron

Zeitzonenauflösung: https://github.com/NousResearch/hermes-agent/blob/main/hermes_time.py und `cron/jobs.py`; bei Einrichtung mit installierter Version abgleichen.
