# Generic Main Agent

Ein geführter Start für einen persönlichen, lokal arbeitenden Hermes-Agenten: HOWTO, Maker-Skill und Alltagsskills. Deutsch, MIT.

## Start

1. [HOWTO](HOWTO.md) öffnen: Sie beginnt mit der offiziellen Hermes-Installation.
2. Hermes und ein Modell einrichten; die bereitgestellten Zugänge aus [Voraussetzungen](docs/VORAUSSETZUNGEN.md) bereithalten.
3. Dieses Repository auschecken oder als ZIP herunterladen und entpacken.
4. Hermes im ausgecheckten Verzeichnis starten und den [Startauftrag](START.md) senden.

Der Checkout führt nichts aus. Der Maker beginnt erst durch deinen ausdrücklichen Auftrag an deinen Agenten.

## Ergebnis

- Persönliche SOUL mit klaren Zuständigkeiten und Sicherheitsregeln.
- Ein selbst gewählter Nachrichtenkanal über den nativen Hermes-Dialog.
- Obsidian-Vault mit Ablageregeln und lokaler Git-Versionierung.
- Lokale Hindsight-API und PostgreSQL/pgvector; Modell-APIs über bereits bereitgestellte Zugänge.
- Firecrawl-Websuche und Seitenlesen über den bereitgestellten Router, mit deinem eigenen Key.
- Vollständiges [Alltagsskill-Paket](docs/SKILLS.md), einschließlich sicherer Installationen.
- Tageszusammenfassung täglich um 02:00 und Backups täglich um 03:00, jeweils lokale Systemzeit.
- Backups unter `~/backups`, 30 Tage Aufbewahrung; Hinweis auf eigenverantwortliche externe Kopie.

Keine zusätzlichen Auswahlfragen für diese Defaults. Namen, Zugangsdaten, echte Konflikte und erforderliche Freigaben bleiben individuelle Angaben.

## Aufbau

| Pfad | Inhalt |
|---|---|
| [HOWTO.md](HOWTO.md) | Kurze Anleitung für Menschen |
| [START.md](START.md) | Kopierbarer Startauftrag an Hermes |
| [skills/generic-main-agent-maker/SKILL.md](skills/generic-main-agent-maker/SKILL.md) | Geführter Einrichtungsablauf |
| [docs/SKILLS.md](docs/SKILLS.md) | Verbindliche Grundausstattung |
| [manifest.json](manifest.json) | Vollständige Skill-Liste und Paketversion |
| [docs/PRUEFUNG.md](docs/PRUEFUNG.md) | Prüfgrenzen und Release-Prüfung |
| [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) | Herkunft und Lizenzabgrenzung |

## Grenzen

Nur die Zielinstanz und lokale Aufgaben. Keine Verwaltung anderer Server, kein Tunnelbau, kein Agententeam, keine Office-/Präsentations-, E-Mail-, Kalender- oder speziellen Coding-Werkzeuge.

Lokale Datenhaltung bedeutet nicht ausschließlich lokale Verarbeitung: das Hauptmodell, die bereitgestellten Hindsight-Modell-APIs, der Nachrichtenkanal und gegebenenfalls Firecrawl Cloud verarbeiten übermittelte Inhalte.

**Prüfstatus:** Das Paket wird statisch geprüft. Der Maker und seine Einrichtung wurden bei der Erstellung ausdrücklich nicht ausgeführt. Es gibt keine behauptete End-to-End-Abnahme. Die Funktionsprüfungen führt dein Zielagent während der späteren Einrichtung durch.

## Lizenz

[MIT](LICENSE). Hinweise für übernommene Konzepte und externe Abhängigkeiten stehen in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
