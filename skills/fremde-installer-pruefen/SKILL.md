---
name: fremde-installer-pruefen
description: "Prüfe fremde Installer vor einer sicheren Installation."
version: 0.1.0
author: Max; Hermes Agent
license: MIT
platforms: [linux]
---

# Sichere Installationen

## Wann
Vor Installation oder Ausführung heruntergeladenen Codes. Quelle und Ziel unterscheiden: Host-Anwendung, eigenes Agentenwerkzeug oder reine Untersuchung. Eine Untersuchung ist keine Freigabe zur Installation.

## Quelle zuerst
- Herkunft, Maintainer, Paketidentität, Version/Commit, Updatekanal und erforderliche Rechte prüfen.
- Offizielle Distroquelle, etablierter signierter Release oder etabliertes digest-gepinntes Image: Integrität prüfen, kein ritualisierter doppelter Testaufbau.
- Ein Hash allein macht ein PyPI-Paket oder Repository nicht vertrauenswürdig.
- Unklarer Installer, fremdes Skript oder unbekanntes Binary: zuerst statisch lesen; Verhaltensprüfung ausschließlich isoliert. Kein unbesehenes `curl | bash` auf dem Host.

## Lokale Prüfumgebung
Docker muss bereits benutzbar sein. Ein Container ist nicht automatisch sicher. Mount-/Rechte-/Netzwerkumfang prüfen. Keine Host-Homes, `.env`, Credentials, SSH-Schlüssel oder Docker-Sockets hineingeben; kein privileged, kein Hostnetwork, keine zusätzlichen Caps.

[Prüfweg](references/pruefumgebung.md) beschreibt einen lokalen Container ohne vorausgesetztes Prüfprofil. Fehlt geeignete Umgebung oder Freigabe für Imagebeschaffung, anhalten. Keine Remote-Server als stillen Ersatz. Internetzugang kann auch ungeschützte Dienste erreichbar machen; diese Grenze transparent halten.

## Beobachten
1. Skript statisch auf Schreibpfade, sudo, Shellprofile, systemd/cron, Keys, Folgeprogramme und Netzziele lesen.
2. Vorheriges Dateiinventar und Marker im ausschließlich eigenen Testbereich erstellen.
3. Kontrolliert mit ungefährlichen verfügbaren Installerschaltern ausführen, Exitstatus/Logs erfassen, keine Secrets bereitstellen.
4. Nachher Inventar vergleichen; geänderte Dateien, Schreibversuche, Rechte und tatsächlich beobachtete Verbindungen berichten. Quelltext-Domain ist nur ein möglicher Kontakt.
5. Marker allein erkennt keine Löschungen und nicht jede Änderung. Kein vollständiges Sicherheitsurteil aus lückenhaftem Dateiscan.

## Echte Installation
Nur im genehmigten Umfang: Vorzustand sichern, Quelle/Version festhalten, Ziel installieren, Funktion prüfen, Rückweg dokumentieren. Deinstallationsbefehl plus verbleibende User/Dateien/Dienste/Konfigzeilen. Host-Installationen und Paketupgrades brauchen geltende Freigabe. Sandbox-Ergebnis sagt nicht voraus, wie der Host reagiert.

Agentenwerkzeuge nach Möglichkeit dauerhaft in sauberer isolierter Umgebung oder dediziertem venv im eigenen Arbeitsbereich halten, nicht in Hermes' verwalteter Python-Umgebung und nicht unnötig doppelt installieren. Ein venv trennt Pakete, ist aber keine Sicherheits-Sandbox.

## Nach dem Vortest
Eine untersuchte Umgebung kann kompromittiert sein. Nicht unverändert als dauerhafte Werkzeugumgebung nutzen. Nur eigenen Testcontainer und eindeutig eigene entbehrliche Testdaten nach geltender Freigabe entfernen oder geschützt quarantänisieren; keine Profile oder allgemeinen Volumes löschen. Kein `docker system prune`.

## Bericht/Verifikation
Quelle, statische Auffälligkeiten, beobachtete Pfade/Netzziele, Rechte, Ergebnis und Grenzen belegen. **Ein Vortest beweist keine Harmlosigkeit.** Fehlgeschlagener Offline-Download beweist weder Defekt noch Sicherheit. Ein erfolgreicher Lauf ersetzt keine Freigabe.
