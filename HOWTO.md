# HOWTO: Dein persönlicher Hermes

## 1. Hermes auf Linux installieren

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

Dem offiziellen [Installationsablauf](https://hermes-agent.nousresearch.com/docs/getting-started/installation) folgen und ein Modell konfigurieren. Die Dialoge werden hier nicht nachgebaut.

Der Befehl lädt und führt das offizielle Installationsskript aus. Prüfe die Quelle vor dem Start. Dieser manuelle Bootstrap findet vor unserem Maker statt; er ist kein von einem bereits laufenden Agenten geprüfter Installer.

## 2. Voraussetzungen bereithalten

[Voraussetzungen](docs/VORAUSSETZUNGEN.md) prüfen: Linux, funktionierender Hermes mit Modell, nutzbares Docker Compose, bereitgestellte Modell- und Router-Zugänge. Keine Tunnel oder fremden Server selbst einrichten.

## 3. Paket holen

Nach Veröffentlichung im GitHub-Repository **Code → HTTPS → URL kopieren**. Die kopierte URL einsetzen:

```bash
mkdir -p ~/projects
cd ~/projects
git clone <KOPIERTE-REPOSITORY-URL> generic-main-agent
cd generic-main-agent
```

Alternativ **Code → Download ZIP**, entpacken und in den entpackten Ordner wechseln. Die URL ist absichtlich keine erfundene Veröffentlichungsadresse.

## 4. Agent starten

```bash
hermes
```

Den vollständigen Text aus [START.md](START.md) senden. Hermes soll zuerst den lokalen Maker-Skill lesen, nicht sofort beliebige Befehle ausführen. Außerhalb des Paketordners den vollständigen lokalen Pfad zur Datei nennen.

## 5. Geführt einrichten

| Schritt | Was du beiträgst | Was der Agent erledigt |
|---|---|---|
| Bestandsaufnahme | Deinen Namen und den Agentennamen nennen | Zielinstanz, Abhängigkeiten, Konflikte und Änderungsumfang prüfen |
| Startfreigabe | Vorgesehenen Umfang samt SOUL und enger Backup-Rotation bestätigen | Vorzustand sichern, Starter-Skills installieren, Arbeitsbereiche vorbereiten |
| Nachrichtenkanal | `hermes gateway setup` selbst ausführen; gewählten Kanal melden | Verbindung, Benutzerbeschränkung und Nachrichtenaustausch prüfen |
| Firecrawl | Eigenen Key in der genannten lokalen `.env` hinterlegen | Warten; Fingerprint berechnen und zur Weitergabe an Max ausgeben |
| Wissensbasis | Nur fehlende Anschlussdaten liefern | Vault, Git, lokale Hindsight-API/DB und eigene Bank einrichten |
| Alltag | Keine erneute Skill-Auswahl | Tageszusammenfassung und Backups tatsächlich einrichten und prüfen |
| Abschluss | Bei nötiger neuer Sitzung mitwirken | Nachweise, offene externe Freischaltungen und Wiederherstellungsweg dokumentieren |

Keinen Schlüssel in den Chat posten. Den Firecrawl-Fingerprint selbst an Max weitergeben; der Agent kann die Router-Registrierung nicht vornehmen.

## 6. Nach einer Unterbrechung fortsetzen

Demselben Zielagenten erneut den Startauftrag geben und „Einrichtung fortsetzen“ ergänzen. Er liest sein lokales Einrichtungsjournal, überprüft den Zustand und macht beim ersten offenen Schritt weiter. Keine doppelten Skills, Cronjobs, Banken oder Summary-Abschnitte.

## 7. Danach

- Tagesnotizen findest du im eingerichteten Vault unter `Daily/`.
- Backups findest du unter `~/backups` im Unterordner deiner Instanz.
- Lokale Backups schützen nicht vor Verlust der Maschine. Eine geschützte Kopie auf ein unabhängiges Ziel organisierst du selbst.
- Der Agent dokumentiert die konkreten lokalen Pfade, Dienste und Prüfbefehle in deinem Vault unter `System/Assistant/`.
- Die [Abschlusscheckliste](skills/generic-main-agent-maker/references/abnahme.md) trennt „vorbereitet“, „eingerichtet“ und „funktional geprüft“.
