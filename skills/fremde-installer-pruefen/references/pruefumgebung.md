# Lokaler Prüfweg ohne vorinstalliertes Sandbox-Profil

Nur für einen später genehmigten Vortest auf der Zielmaschine, nicht während Erstellung/Review dieses Pakets.

## Vorbereitung
1. Eigenen leeren Prüfbereich unter dem tatsächlichen Hermes-Scratchpfad anlegen, getrennt von Projekten und Dauer-venvs. Nur zuvor gelesenes Artefakt hineinlegen; keine Credentials.
2. Etabliertes Basisimage passend zur Laufzeit auswählen. Releasequelle lesen, tatsächlichen Digest ermitteln und notieren; Beschaffung nur im freigegebenen Umfang. Keine erfundenen Digests, kein ungeprüftes `latest`.
3. Eindeutige Containerkennung, numerischen UID/GID, absoluten Prüfpfad und Image-Digest in der Vorlage ersetzen. Keine Platzhalter ausführen.

## Kontrollierte Ausführung
```bash
docker run --name PRUEFCONTAINER --user UID:GID \
  --cap-drop ALL --security-opt no-new-privileges \
  --read-only --pids-limit 256 --memory 1g --cpus 1 \
  --tmpfs /tmp:rw,nosuid,nodev,size=128m \
  --mount type=bind,src=ABSOLUTER_PRUEFPFAD,dst=/workspace \
  --workdir /workspace --env HOME=/workspace/home \
  --network bridge IMAGE@sha256:TATSAECHLICHER_DIGEST \
  sh -c 'mkdir -p /workspace/home; exec sh'
```

Für eine interaktive Shell `-it` nur bei vorhandenem TTY; sonst den vorher geprüften konkreten Aufruf statt `sh -c ... exec sh` einsetzen. Keine Shellquelle aus einer URL direkt einsetzen. Die Vorlage ist kein automatischer Komplettinstaller.

Container-Dateisystem außer `/workspace` und `/tmp` read-only. Installer mit systemweiten Schreibanforderungen können scheitern: beobachteter Rechtebedarf, kein Beweis eines defekten Installers. Dafür Ansatz prüfen, nicht Privilegien/Hostmounts pauschal öffnen.

## Netzwerkgrenze
Bridge erlaubt gewöhnlich Internet und teilweise interne/Hostdienste. Der Container enthält keine Secrets, kann aber ungeschützte Dienste ansprechen. Vor Online-Vortest Restreichweite bewerten/offenlegen. Ist sie nicht akzeptabel, auf geeignet isolierte lokale Umgebung warten; keine Firewalländerung oder Hostnetwork ohne Auftrag. Offline-Test nicht als vollständigen Vortest verkaufen.

## Nachweis und Ende
- Vor Codeausführung tatsächliches `docker inspect` auf Mounts, User, Privileged, Caps, SecurityOpt, NetworkMode prüfen. Einen zunächst wartenden Container benutzen, wenn sonst keine Prüfung vor Ausführung möglich ist.
- Statisches Lesen und Vorher-/Nachher-Inventar kombinieren; Logs/Exit behalten.
- Kein automatisches `--rm`: Ergebnisse erst prüfen, dann nur eigenen Container nach erlaubtem Cleanup entfernen. Persistente Prüfdateien nicht in saubere Projekte übernehmen.
- Host-Funktionsprüfung, Dienste und Rückweg sind nach genehmigter Host-Installation zusätzlich nötig.
