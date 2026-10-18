---
name: hermes-agent
description: "Bediene und prüfe die eigene Hermes-Instanz."
version: 0.1.0
author: Max; Hermes Agent
license: MIT
platforms: [linux]
---

# Eigene Hermes-Instanz

## Wann
Bei Hermes-Bedienung, Konfiguration, Diagnose oder Erweiterung. Kein Auftrag zur Verwaltung anderer Profile oder Server.

## Vorgehen
1. Effektives `HERMES_HOME`, Profil, Version und tatsächliche Runtime bestimmen. Gespeicherte Konfiguration und laufenden Zustand unterscheiden. Nicht automatisch eine neue Runtime bootstrappen, wenn nur Quelltext geprüft werden soll.
2. Aktuelle offizielle Dokumentation über https://hermes-agent.nousresearch.com/docs/llms.txt finden; passende Seite lesen. Lokale `--help` mit der installierten Version vergleichen. Kein erfundener Schalter, kein fehlendes Feature aus Erinnerung behaupten.
3. Ziel und Vorzustand lesen. Änderungen nur am Ziel, vorher betroffene Dateien geschützt sichern. Einstellungen mit `hermes config set`; Zugangsdaten nur über den vorgesehenen lokalen Secretweg. Keine komplette Konfiguration mit Secrets ausgeben.
4. Sicherheitsfreigaben und Paketquellen beachten. Nicht in Hermes' verwaltete Python-Umgebung installieren. Keine Core-Patches als improvisierte Reparatur.
5. Native Diagnose nutzen, z. B. `hermes doctor`, `hermes memory status`, `hermes gateway status`, `hermes cron status`. Zuvor mögliche Bootstrap-Nebenwirkungen der konkreten Installation berücksichtigen.
6. Änderungen nachlesen und tatsächliche Funktion prüfen. Ist eine neue Sitzung oder ein Neustart erforderlich, Freigabe einholen und Fortsetzung sichern. Kein ungefragter Gateway-Neustart.

## Webzugang
Die Zielinstanz nutzt den vom Maker eingerichteten Firecrawl-Router. Endpoint im lokalen Einrichtungsbericht ermitteln. Such-/Extraktionsprovider und Key getrennt prüfen; `web.backend: nous` oder Legacy-Gatewayrouting nicht mit direktem Firecrawl verwechseln. Keine direkte Cloudroute oder anonymen Ersatzanbieter aktivieren. Registrierungsfragen gehen über den Benutzer an den Betreiber; keinen Server administrieren.

## Updates und Wiederherstellung
Vor einem Update vollständige Sicherung und lokalen Wiederherstellungsweg prüfen; benötigte Freigabe einholen. Unterstützten aktuellen Updateweg aus Dokumentation ermitteln, keine Pakete/Core-Dateien manuell überschreiben. Nachher Version, Kanal, Memory und Zeitsteuerung prüfen. Keine automatischen Updates einrichten.

## Verifikation
Berichte was gespeichert, was aktiv und was funktional nachgewiesen ist. Fehler auf die tatsächliche Schicht eingrenzen, keine pauschalen Neuinstallationen. Wissensänderungen anlassbezogen im Vault nach dem `obsidian`-Skill dokumentieren.

## Quellen
- https://hermes-agent.nousresearch.com/docs/
- https://hermes-agent.nousresearch.com/docs/user-guide/features/skills
- https://hermes-agent.nousresearch.com/docs/user-guide/features/web-search
