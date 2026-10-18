---
name: generic-main-agent-maker
description: "Richte einen persönlichen lokalen Hermes-Hauptagenten ein."
version: 0.1.0
author: Max; Hermes Agent
license: MIT
platforms: [linux]
---

# Generic Main Agent Maker

Ein geführter Einrichtungsablauf für genau eine frische Hermes-Instanz mit bereits eingerichtetem Modell. Feste Defaults, keine Feature-Auswahlrunde. Lade nur die gerade erforderlichen Referenzen. Dieses Paket ist kein autonom startender Installer.

## Wann anwenden

Nur auf ausdrücklichen Startauftrag des Besitzers an seinen Zielagenten. Das Lesen, Reviewen oder Erstellen dieses Repositorys ist **keine** Ausführungsfreigabe. Bei der Paketerstellung niemals diese Schritte ausführen. Keine anderen Profile oder Server verwalten.

## Vor jeder Änderung

1. Stelle fest, ob du Paketautor/Reviewer oder ausdrücklich beauftragter Zielagent bist. Im ersten Fall nur Dateien lesen/bearbeiten und statisch prüfen.
2. Ermittle absoluten Repository-Pfad, Zielbenutzer, effektives `HERMES_HOME` (Fallback nur wenn unset: `~/.hermes`), aktives Profil, Terminal-Backend und reale Dateipfade. Bei Sandbox-Terminal prüfen, welche Pfade wirklich dem Zielhost gehören; nicht in einem vergänglichen Container als angebliche Host-Einrichtung arbeiten.
3. Lies `manifest.json` im ursprünglichen Checkout-Root und [Einrichtung](references/einrichtung.md). Den Checkout-Pfad als `source_checkout` im Journal speichern; bei späterem Aufruf des installierten Makers dort fortsetzen. Liegt das Manifest nicht vor, den vorhandenen Checkout ermitteln/erfragen, keine fehlenden Pakete erfinden. Prüfe Linux, Hermes-Version/Modell, Python, Git, Docker Compose, verfügbare lokale Zugänge und Konflikte. Nutze native Hilfe der Zielversion; keine Kern-Patches oder automatischen Upgrades.
4. Lies bestehendes `<HERMES_HOME>/maker/state.json`, falls vorhanden. Prüfe jeden übernommenen Status am tatsächlichen Ziel nach. Ein Journal ist kein Funktionsnachweis.
5. Erfrage nur Benutzer-/Agentenname, nicht verfügbare Anschlussdaten, echte Konflikte und nötige Freigaben. Zeige einmal den konkreten Änderungsumfang samt persönlicher SOUL und der engen Backup-Rotation. Keine erneute Frage, ob Skills oder Daily Summary gewünscht sind.

## Feste Startbasis

- Ein Nachrichtenkanal über den nativen Hermes-Dialog, nicht zwingend Telegram.
- Vault: vorhandenen erkennen/respektieren, sonst `~/obsidian_vault`; lokale Git-Versionierung, Remote nur auf Wunsch.
- Arbeitsprojekte unter `~/projects`, temporäre Dateien im vorgesehenen Scratchbereich der Zielinstanz.
- Vollständiges Skill-Paket aus `manifest.json`, inklusive sicherer Installationen und PDF-Grundfunktionen.
- Lokale Hindsight-API und lokale PostgreSQL/pgvector in Docker; bereitgestellte externe Modell-APIs, eigene neue Bank.
- Firecrawl über bereitgestellten Router und eigenen Key; Fingerprint manuell an Max.
- Daily Summary: **02:00 lokale Zeit**, abgeschlossener Vortag, nur Zielinstanz.
- Backup: **03:00 lokale Zeit**, `~/backups/<Instanzkennung>`, **30 Tage**; kein LLM, bei Erfolg still, Fehler im eingerichteten Kanal.

## Ablauf und Prüfpunkte

| Phase | Referenz | Fertig erst wenn |
|---|---|---|
| 0. Bestand und Freigabe | [Einrichtung](references/einrichtung.md) | Ziel, Voraussetzungen, Datenwege und genehmigter Umfang dokumentiert |
| 1. Sicherungen/SOUL/Skills | [Einrichtung](references/einrichtung.md), [SOUL-Vorlage](templates/SOUL.md.template) | Persönliche SOUL freigegeben, vorhandene Dateien gesichert, vollständige Pakete auffindbar/ladbar |
| 2. Arbeitsraum/Vault | installierter `obsidian`-Skill | Richtiger Vault, Index/Hubs, Git, keine Geheimnisse |
| 3. Nachrichtenkanal | [Einrichtung](references/einrichtung.md) | Benutzer hat nativen Dialog erledigt, Zugriff begrenzt, echter Austausch geprüft |
| 4. Firecrawl | [Firecrawl](references/firecrawl.md) | Key lokal hinterlegt, echter Fingerprint ausgegeben, Such-/Lesetest; Registrierung separat verifiziert oder offen |
| 5. Hindsight | [Hindsight](references/hindsight.md) | API/DB lokal, eigene Bank, Retain/Recall/Reflect/Konsolidierung/Persistenz geprüft |
| 6. Daily Summary | [Zeitpläne](references/zeitplaene.md), installierter `obsidian-daily-summary` | Aktiver idempotenter Job und erfolgreicher Lauf/korrekt dokumentierter Leertag |
| 7. Backup | [Zeitpläne](references/zeitplaene.md), installierter `local-backup-restore` | Vollständiger Backup-Lauf plus isolierte Wiederherstellungsprobe, aktiver täglicher Job |
| 8. Abschluss | [Abnahme](references/abnahme.md) | Alle Pflichtpunkte verifiziert oder konkrete Blocker ausdrücklich offen |

## Wartepunkte

- **SOUL/Hoständerungen:** erforderliche Freigabe einholen, keine pauschale dauerhafte Befugnis ableiten.
- **Kanal:** Benutzer führt `hermes gateway setup` aus. Auf Rückmeldung warten, dann prüfen.
- **Firecrawl-Key:** sichere lokale Eingabe anweisen, warten, niemals Key im Chat anfordern.
- **Router-Registrierung:** Fingerprint an Benutzer geben; keine Serveränderung. Andere unabhängige Phasen weiterführen.
- **Fehlende Modell-APIs:** Hindsight-Schritt blockieren, keine Ersatzmodelle/Cloudfallback/Tunnel bauen.
- **Aktivierung:** erforderliche Neustarts nicht eigenmächtig durchführen. Falls eine neue Sitzung nötig ist, Zustand sichern und dem Benutzer genaue Fortsetzung nennen.

## Journal und Wiederholung

Vor der ersten Änderung `<HERMES_HOME>/maker/` mit engen Rechten anlegen. [Statusvorlage](templates/state.json.example) als Schema nutzen. Nur aufgelöste Pfade, Versionen, geprüfte Nachweise, Freigaben und Status speichern, keine Secrets oder vollständigen Konfigurationsdumps. Statuswerte `pending`, `waiting_user`, `blocked`, `configured`, `verified` unterscheiden.

Vorhandene Pakete vollständig vergleichen, Jobs nach gespeicherter ID plus Eigentum prüfen, vorhandene eigene Bank wiederverwenden. Bei Namens-/Datenkonflikt nicht überschreiben und nicht neue Dubletten anlegen. Vorherige Sicherungen erhalten. Kein Erfolg allein aufgrund des letzten eigenen Tool-Exitcodes.

## Grenzen

Keine Verwaltung anderer Server, kein Tunnelbau, keine fremden Banken, keine anderen Profile, kein Dev-Team. Office, Präsentationen, E-Mail, Kalender und spezielle Coding-Werkzeuge bleiben außerhalb dieses Pakets. Gateway-Konfiguration für den gewählten Nachrichtenkanal ist davon unabhängig.

Sicherheitsregeln gelten ab dem ersten Installationsschritt: den Skill `fremde-installer-pruefen` aus dem Checkout oder über native Discovery laden. Andere Skills über ihren Namen und tatsächlichen Pfad auflösen, nicht kategoriefreie Geschwisterpfade in der aktiven Installation voraussetzen. Benötigte Abhängigkeiten nur aus überprüfter Quelle und im freigegebenen Bereich. Fehlende Prüfumgebung bedeutet anhalten, nicht unklaren Code auf dem Host ausprobieren.
