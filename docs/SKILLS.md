# Festes Starterpaket

Der Maker installiert diese vollständigen Pakete oder gleicht bereits vorhandene passende Versionen ab. Keine zweite Auswahlrunde. Abweichende bestehende Pakete werden nicht ungefragt überschrieben.

| Name | Zweck |
|---|---|
| `hermes-agent` | Native Bedienung, Diagnose und aktuelle Dokumentation |
| `obsidian` | Vault-Struktur, Hubs, Notizen und lokale Git-Pflege |
| `gedaechtnis-praxis` | Zusammenspiel von Memory, Hindsight, Vault und Skills |
| `grounded-citations` | Recherche mit überprüfbaren Quellen |
| `minimal-change-engineering` | Kleine korrekte Änderungen und Verifikation |
| `fremde-installer-pruefen` | Sichere Quellenprüfung, lokale Isolation und Rückweg |
| `pdf` | Lokale PDF-Grundaufgaben, ohne automatische OCR-Modelle |
| `local-backup-restore` | Deterministische Sicherung und kontrollierte Wiederherstellung |
| `obsidian-daily-summary` | Tageszusammenfassung einschließlich Pflicht-Cron |

Der `generic-main-agent-maker` selbst ist zusätzlich der Einrichtungs-Skill. Nicht nur SKILL.md kopieren: alle Referenzen, Templates und Hilfsdateien des jeweiligen Pakets mitnehmen.

## Abhängigkeiten

- Die Regeln und Anleitungen benötigen keine Zusatzdienste.
- PDF-Grundfunktionen benötigen eine eigene Arbeits-venv mit `pypdf`, `reportlab` und `pdfplumber`, nicht Änderungen an Hermes' verwalteter Python-Umgebung. Der Maker beschafft geprüfte Versionen und dokumentiert den tatsächlichen Stand.
- Sitzungsinventar und Firecrawl-Fingerprint benutzen Python-Standardbibliothek.
- Backups benötigen zusätzlich Docker Compose und die PostgreSQL-Werkzeuge im DB-Container; der Zeitplan benötigt den funktionierenden Hermes-Gateway.
- Hindsight ist eine separat dokumentierte lokale Laufzeit, nicht lediglich ein Skill.

Alle Pakete werden für diese Startbasis eigenständig und schlank bereitgestellt; persönliche Infrastruktur und Autorenfreigaben sind keine Bestandteile.
