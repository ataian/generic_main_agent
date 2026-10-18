# Paketprüfung und ehrliche Grenzen

## Bei der Erstellung erlaubt

```bash
python3 tests/check_package.py
python3 skills/local-backup-restore/tests/check_static.py
git diff --check
```

Der Prüfer liest nur Paketdateien und nutzt Standardbibliothek. Er importiert oder startet keinen Maker-Helfer, spricht keine Dienste an und schreibt keine Konfiguration. Er prüft Manifest/Skill-Set, Metadaten, Referenzen, JSON, Python-Syntax und unerwünschte private Bindungen. Syntax ist kein Funktionsbeweis.

Der zusätzliche Backupcheck prüft Allowlist und Container-Authentifizierung über den Python-AST sowie Restore-Beispiele mit `bash -n`. Er startet weder Backup noch Restore. `bash` wird nur zum Parsen benötigt.

## Ergebnis für das erstellte Paket

- Paketcheck und Backup-Vertragscheck bestanden; keine Whitespacefehler im geprüften Diff.
- Skill-Frontmatter und Compose-Vorlage zusätzlich mit vorhandenem YAML-Parser gelesen; Shellsyntax der Initvorlage geprüft. Das ist keine Compose-Laufzeitvalidierung.
- Unabhängiges statisches Gesamt-Review ohne verbleibende priorisierte Findings im geprüften Umfang. Die anschließend integrierte Backup-Korrektur wurde vom Hauptagenten anhand Quelltext, Schnittstellen und statischem Vertragscheck geprüft; keine Behauptung einer unabhängigen Betriebsabnahme.
- Korrigiert: eindeutige Trennung Paketautor/Zielnutzer, tatsächlicher Cron-Zeitzonen- und Fehlervertrag, SCRAM-Backupzugang, vollständige gezielte Betriebsdatei-Allowlist und PG18-Restore-Rezept.

Diese Aussagen gelten für die Paketprüfung, nicht für eine installierte Zielumgebung. Bei späteren Änderungen die obigen Prüfungen erneut durchführen.

## Nicht während der Paketerstellung ausgeführt

- Keine Installation, keine Sandbox-/Containeranlage.
- Kein Fingerprint aus echten Credentials, kein Sitzungsinventar echter Nutzer.
- Kein Backup, keine Rotation, kein Restore, kein Cronjob.
- Keine Hindsight-/Modell-/Router-Funktionsprüfung.
- Keine Aktivierung in einer bestehenden Agenteninstallation.

Der Maker bleibt deshalb **nicht End-to-End-getestet**. Die später notwendigen Laufzeitprüfungen stehen in seiner [Abnahme](../skills/generic-main-agent-maker/references/abnahme.md).

## Vor einer Veröffentlichung

- Nur öffentliche Dateien aus dem Manifest-/Dokumentbaum aufnehmen.
- `.local/`, Root-`references/`, lokale `.env`, Secrets, Dumps und Autorentestdaten ausschließen.
- Nicht nur Arbeitsbaum, auch tatsächlichen Git-Index und bereits vorhandene Historie auf Geheimnisse/interne Bindungen prüfen.
- Lizenz-/Herkunftshinweise erhalten. Keine ungeprüften Installer/Images mitliefern.
- Versionsangabe, relative Links und vollständiges ZIP kontrollieren.
- Reviewergebnis und statische Prüfausgabe getrennt von späteren Installationsnachweisen beschreiben.
