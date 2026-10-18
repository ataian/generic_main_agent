---
name: minimal-change-engineering
description: "Ändere Skripte und Konfiguration minimal und korrekt."
version: 0.1.0
author: Max; Hermes Agent
license: MIT
platforms: [linux]
---

# Minimal-Change Engineering

## Wann
Bei lokalen Skripten, Konfiguration, Automatisierung oder kleinen Codeänderungen. Kein Dev-Team-Prozess und keine Freigabe für andere Systeme.

## Regeln
1. Ziel und Bereich bestimmen; bestehende Umsetzung und Aufrufer lesen.
2. Kleinste korrekte Änderung am richtigen Ort. Fehlerursache statt Symptom behandeln.
3. Bestehende Muster, Standardbibliothek und native Funktionen bevorzugen. Keine spekulativen Frameworks.
4. Keine ungefragten Umbenennungen, Formatierungssweeps, Refactorings oder Nebeninstallationen.
5. Sicherheit, Idempotenz, nötige Backups, Fehlerbehandlung, Logging und Verifikation gehören zum Auftrag.
6. Vor Änderungen Pfad und Umfang kurz nennen. Bei erweitertem Risiko/Funktionsumfang klären.
7. Fremde Änderungen erhalten. Keine pauschalen Git-Resets oder Datenlöschung als Aufräumen.
8. Geändertes Verhalten und Betriebsdokumentation zusammen aktualisieren.

## Prüfweg
Vor dem Fix Fehler erfassen, geeigneten Regressionstest festlegen, nachher ausführen und Ergebnis lesen. Bei ausdrücklichem Ausführungsverbot nur statisch prüfen und diese Grenze berichten. Konfiguration nachlesen, Funktion separat prüfen; Command-Exit ist nicht gleich Nutzerergebnis.

## Abschluss
Was wurde geändert, welches Ergebnis ist nachgewiesen, was bleibt offen? Größeren Umbau allenfalls in einem Satz vorschlagen, nicht nebenbei durchführen. Freigabegrenzen der SOUL bleiben maßgeblich.
