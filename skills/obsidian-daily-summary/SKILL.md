---
name: obsidian-daily-summary
description: "Fasse den Vortag im eigenen Obsidian-Vault zusammen."
version: 0.1.0
author: 'Max; Hermes Agent'
license: MIT
platforms: [linux]
---

# Tageszusammenfassung der eigenen Instanz

Erstelle täglich um **02:00 in der lokalen Systemzeitzone** eine deutsche Zusammenfassung des abgeschlossenen Vortags. Das gehört verbindlich zur eingerichteten Startbasis, ist kein Auswahlmenü. Die Erstellung dieser Paketdateien installiert oder startet jedoch keinen Job.

## Wann verwenden?

Für den täglichen Lauf, einen ausdrücklich angeforderten Nachholtag und die Funktionsprüfung nach Einrichtung. Keine Sammlung anderer Profile, keine Zusammenfassung beliebiger fremder Sitzungen, kein Volltranskriptexport.

## Voraussetzungen

- Das Paket `obsidian` ist vorhanden; vor jeder Vault-Änderung seinen Skill und seine Regelreferenz laden.
- Konkreter vorhandener Vault, Tagesnotiz-Konvention, Einstieg und Daily-Hub sind bekannt. Für neue Vaults gilt `Daily/YYYY-MM-DD.md`; vorhandene Konventionen respektieren.
- **Genau eine Zielinstanz:** deren aufgelöster absoluter DB-Pfad und die lokale IANA-Zeitzone sind explizit festgelegt. Keine Suche nach `profiles/*`, keine Ausweich-DB. Nur die Zielinstanz darf `session_search` ausführen.
- Python 3.9+ mit Standardbibliothek, SQLite und verfügbarer System-Zeitzonendatenbank. Kein Drittanbieter-Pythonpaket erforderlich.
- Native `session_search`-Schnittstelle vor Verwendung prüfen. Der [Helper-Vertrag](references/helper-und-pruefung.md) dokumentiert das geprüfte Schema und die Grenzen.

## Ablauf

1. **Datum bestimmen.** Aktuelle Zeit mit einem Werkzeug ermitteln. Im festgelegten lokalen Kalender einen Tag zurückgehen, nicht pauschal 24 Stunden abziehen. Ein Wiederholungslauf behält sein ursprüngliches Datum. Niemals still den aktuellen Tag statt des Vortags zusammenfassen.
2. **Ziel und Vorzustand lesen.** Tagesnotiz, Daily-Hub und nötige Linkkette prüfen. Vorhandene Nutzertexte und bestehende Summary-Markierungen vollständig lesen. Auch bei leerem Tag bleibt der ursprüngliche Text geschützt.
3. **Metadaten vollständig erheben.** Den rein lesenden [Python-Helper](scripts/list_messages_for_date.py) nach dem Vertrag ausführen. Er erhält `--db ABS --date YYYY-MM-DD --timezone IANA` und liefert IDs und Zeiten aller im lokalen Tagesfenster gespeicherten Nachrichten, ohne Inhalte oder Sitzungstitel. Nicht nach Sitzungsbeginn filtern: eine vor Mitternacht gestartete Sitzung kann relevante Nachrichten enthalten.
4. **Ergebnis prüfen.** Nur `ok: true` ist verwertbar. Fehlende DB, unbekanntes Schema, unlesbare Zeitstempel und Tool-Ausfälle sind Fehler, kein leerer Tag. Bei Fehler vorhandene Summary unverändert lassen, Ursache knapp melden, keinen Erfolg oder `[SILENT]` ausgeben. Die Metadaten können lokal verarbeitet werden; nicht einen großen JSON-Block in den Modellkontext laden. Im unbeaufsichtigten Cronlauf für die JSON-Auswahl `jq` verwenden (bei Einrichtung mit `command -v jq` prüfen), keine Inline-Python-Befehle oder `execute_code`: Diese benötigen dort eine nicht verfügbare Sicherheitsfreigabe. Sicherheitsregeln nicht lockern; fehlendes `jq` vor Aktivierung als Voraussetzung klären.
5. **Gezielt native Inhalte lesen.** `session_search` über Sitzung und Nachrichtenanker mit kleinen Fenstern verwenden, etwa `session_id`, `around_message_id`, `window: 2`, `role_filter: "user,assistant"`. Zuerst Anfang/Ende und erkennbare Themenwechsel des Tages, anschließend Lücken bei Bedarf prüfen. Tool-Inhalte nur gezielt für Ergebnisbelege. Keine ganze Sitzung allein über `session_id` laden. Die im Vertrag beschriebenen Abdeckungsregeln beachten.
6. **Zeitfenster und Abdeckung erhalten.** Aus Suchfenstern nur IDs des Helper-Ergebnisses in die Tageszusammenfassung übernehmen; Nachbarinhalte außerhalb des Tages nicht als Tagesereignis verwenden. Pro Sitzung relevante Ergebnisse, Entscheidungen und offene Punkte abdecken. Kompressionszusammenfassungen sind keine neuen Tätigkeiten; kopierte/fortgesetzte Inhalte nicht doppelt zählen. Selbst-/Summary-Läufe nur anhand belegter Identität aussparen, nicht nach ungefährer Startzeit. Ausnahmen und nicht lesbare Bereiche explizit nennen. Ein Budgetende ist kein Vollständigkeitsnachweis.
7. **Kompakt formulieren.** Themen statt Nachrichten nacherzählen. Tatsächlich erreichte Ergebnisse von Absichten trennen. Zeiten lokal mit Offset bei Mehrdeutigkeit, Quellen sparsam als Sitzungs-ID/Nachrichten-ID. Keine Secrets, Rohtranskripte, kompletten Logs oder vermuteten Erfolge in den Vault schreiben.
8. **Idempotent aktualisieren** nach dem Abschnitt unten. Hub- und Elternlinks gemäß `obsidian` ergänzen. Eine neue Notiz darf mit `write_file` entstehen; vorhandene Notizen nur gezielt patchen.
9. **Verifizieren.** Genau ein verwalteter Summary-Block, keine zweite `## Daily Summary`-Überschrift, Nutzerinhalt außerhalb des Blocks unverändert, Linkkette vollständig. Bei unverändertem Ergebnis nicht nochmals schreiben. Kurz Zielnotiz, Datum, geprüfte Abdeckung und eventuelle Lücken melden; keine Geheimnisse.

## Ein verwalteter Abschnitt, kein Überschreiben

Den Block nur bei erstmaliger, konfliktfreier Anlage mit folgendem Format erzeugen:

```markdown
<!-- hermes-daily-summary:begin YYYY-MM-DD -->
## Daily Summary

### Ergebnisse
- Belegtes Ergebnis mit kurzer Quelle und optional lokaler Zeit.

### Entscheidungen
- Getroffene Entscheidung oder „Keine dokumentiert.“

### Offene Punkte
- Nächster Schritt oder „Keine dokumentiert.“

### Quellenlage
- Ausgewerteter Tag, Zeitzone, Abdeckung und gegebenenfalls Lücken.
<!-- hermes-daily-summary:end YYYY-MM-DD -->
```

- Platzhalterdatum ersetzen. Erstmalig am Ende der vorhandenen Notiz anhängen, ohne andere Abschnitte zu verschieben; keine fragile Suche nach einer beliebigen letzten Überschrift.
- Bei genau einem passenden Markierungspaar nur diesen Bereich gezielt ersetzen. Vor dem Patch den aktuellen Stand erneut lesen und auf parallele Änderungen prüfen.
- Existiert bereits eine unmarkierte `## Daily Summary`, gibt es doppelte/fehlerhafte Marker oder mehrere Summary-Abschnitte: **anhalten**. Nicht löschen, nicht einen zweiten Block hinzufügen. Einmalige Übernahme mit dem Benutzer abgrenzen und bestätigen; im unbeaufsichtigten Job Konflikt melden.
- Die Marker kennzeichnen nur den agentenverwalteten Bereich. Nutzerergänzungen darin erhalten; bei nicht eindeutig zuordenbarer Änderung anhalten statt ersetzen. Nutzertext außerhalb des Blocks muss bytegetreu unverändert bleiben.
- Bei erfolgreich geprüfter Datenbasis ohne Tagesnachrichten ausdrücklich „Keine gespeicherten Nachrichten im geprüften Tagesfenster der Zielinstanz.“ notieren. Das belegt keine allgemeine Untätigkeit. Gibt es nur Routine-/Summary-/Systemnachrichten, diesen anderen Fall ehrlich benennen.

## Einrichtung und Abnahme sind getrennte Schritte

Der Eltern-/Einrichtungsagent richtet später genau einen aktiven Tagesjob mit Skill-Zuordnung, Zielinstanz, Zielvault und lokaler Zeitzone ein. Er prüft Scheduler, Wiederholung und einen echten Lauf. Keine Befehle oder Cron-API-Felder raten; aktuelle native Schnittstelle und Dokumentation verwenden. Bereits passende Jobs wiederverwenden, fremde Jobs nicht verändern. Keine zusätzlichen Sync- oder Watchdog-Jobs.

Die [Einrichtungs- und Prüfanleitung](references/helper-und-pruefung.md) ist vor Aktivierung vollständig abzuarbeiten. Ein statisch geprüftes Paket belegt weder einen laufenden Scheduler noch eine erfolgreiche Tagesnotiz.

[Herkunft und Lizenz](references/provenienz.md) · [MIT-Lizenz](LICENSE)
