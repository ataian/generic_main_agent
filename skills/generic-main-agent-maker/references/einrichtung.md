# Bestand, Freigabe und Grundkonfiguration

Diese Anleitung führt der spätere Zielagent aus, nicht der Paketautor.

## 1. Bestand

- Betriebssystem/Benutzer/Home/Zeitzone und aktive Hermes-Instanz lesen; bei benanntem Profil native `--profile`-Option benutzen. Alle folgenden Befehle meinen ausschließlich dieses Ziel.
- `hermes --version`, `hermes doctor`, `hermes config --help`, `hermes gateway --help`, `hermes skills --help`, `python3 --version`, `git --version`, `docker version`, `docker compose version` prüfen. Keine Version vermuten; CLI kann bei unvollständiger Installation Abhängigkeiten nachziehen: ungeklärte Bootstrap-Wirkungen nicht als reine Statusabfrage ausführen.
- Vorhandene SOUL, Skill-Namen, Vault-Kandidaten, belegte Ports und geplante Dienstnamen gezielt prüfen; niemals ganze `.env`/Auth-Dateien ausgeben.
- Keine Lese-/Schreibtests in fremden Profilen. Zugang zum Docker-Daemon ist mächtig; keine Docker-Socket-Mounts in Testcontainer.
- Fehlende Betriebssystempakete sind ein Blocker mit begrenztem Installationsvorschlag, kein stilles Systemupgrade.

## 2. Startfreigabe

Namen einmal erfragen. Defaults: sachlich-warm, deutsch, duzen, knappe Antworten, Freund/Helfer ohne Partnerrolle, keine Emojis. Vorbereitete SOUL personalisieren; Avatar/Motto nur bei Benutzerwunsch.

Zeige konkret: Ziel-Hermes-Home, zu ändernde vorhandene Dateien, neue Verzeichnisse, lokale Dienste/Ports, Skill-Pakete, zwei Zeitpläne, Datenwege zu Modellen/Router/Kanal und Backup-Rotation. Die Freigabe umfasst diesen Aufbau und nur die eigene alte Backup-Rotation. Sie ist keine allgemeine Lösch- oder Neustartfreigabe. Ein bestehender Konflikt verlangt eine gezielte Entscheidung.

## 3. Vorzustand sichern

Vor jeder Ersetzung ein datiertes Archiv unter `<HERMES_HOME>/maker/rollback/` außerhalb aller Skill-Suchwurzeln anlegen. Dateien und vollständige betroffene Skill-Pakete einschließlich Installationsmetadaten sichern, Rechte schützen und Hashvergleich dokumentieren. Keine anderen Profile sammeln. Konfigurationsbackup kann Geheimnisse enthalten: nicht in Git oder Vault.

## 4. SOUL und Einstellungen

- Vorlage personalisieren und nach Zustimmung an die tatsächlich wirksame SOUL-Stelle schreiben. Keine zusätzliche SOUL im Arbeitsverzeichnis als angeblich globale Identität.
- Konfigurationsänderungen über `hermes config set`, nicht durch freie YAML-Umschreibung. Plugin-eigene JSON-Dateien nach dokumentiertem Schema behandeln.
- Freigabeschutz aktiv lassen; keine YOLO- oder globale Autoapprove-Einstellung. Benötigte Werkzeuggruppen nicht pauschal öffnen.
- Eigene lokale Arbeitsbereiche dokumentieren, aber keine unsichtbare technische Sandbox behaupten.
- Lege `<HERMES_HOME>/maker/environment.json` mit `vault_path`, `projects_path`, `timezone`, `instance_id`, `skills_paths`, `pdf_python` und Dienstpfaden an. Keine Secrets. Instanzkennung stabil als `main`, sofern nicht belegt; bei Konflikt nicht still eine zweite Instanz erzeugen.

## 5. Skill-Paket bereitstellen

1. `manifest.json` im Checkout lesen. Für jedes Paket sämtliche Dateien prüfen; keine Symlinks aus dem Paket heraus akzeptieren.
2. Native Skill-Suche der Zielinstanz lesen. Bereits vorhandene gleichnamige Pakete und Quelle (bundled/Hub/eigen) bestimmen.
3. Identisches vollständiges Paket: unverändert nutzen. Unveränderte Standardfassung: nach der Startfreigabe sichern und durch die Starterfassung im bestehenden tatsächlichen Zielpfad ersetzen. Persönlich veränderte oder fremd verwaltete Fassung: Unterschied erklären, gezielt klären, nie blind überschreiben oder unter demselben Namen zusätzlich installieren.
4. Fehlende Pakete vollständig nach `<HERMES_HOME>/skills/<Name>/` kopieren. Bei verwalteten Paketen zuerst unterstützten Entkopplungsweg der Zielversion prüfen; keine stale Hub-Bindung behalten, die unsere Fassung ungefragt überschreibt. Kein globales `skills reset`, kein `opt-out --remove` und kein `--force` zum Umgehen eines Scans.
5. Jeden erwarteten Namen über native `skills_list`/`skill_view` entdecken und Hauptdatei sowie mindestens jede erforderliche Referenz laden. Dateiexistenz ist nicht Discovery. Eine neue Sitzung kann für einen gecachten Katalog nötig sein; keinen laufenden Gateway ungefragt neu starten.
6. Den Skill `pdf` über native Discovery oder aus dem ursprünglichen Checkout laden und die dortigen Grundabhängigkeiten in einem eigenen venv vorbereiten. Nicht in Hermes' verwaltete Umgebung pip-installieren. Verwendete Versionen und Interpreterpfad dokumentieren.
7. Kurzen Datei-Lese-/Schreibtest ausschließlich im eigenen Arbeitsbereich ausführen; Ergebnis nachlesen.

## 6. Vault

Installierten `obsidian`-Skill samt Regelreferenz lesen. Vorhandenen Vault respektieren; andernfalls `~/obsidian_vault`. Effektiven Pfad in `maker/environment.json` und im Einrichtungsbericht festhalten. Der Skill liest diese Referenz vor einem Fallback. Keine Annahme aus einem nicht existierenden Beispielpfad.

Lokales Git initialisieren, Geheimnisse ausschließen, lokale Identität aus vorhandener Git-Konfiguration verwenden; fehlt sie, repository-lokal einen vom Benutzer bestätigten Namen/Adresse setzen, keine globalen Einstellungen. Einen Git-Remote separat erfragen; eine Ablehnung blockiert den lokalen Vault nicht. Keine automatische Veröffentlichung.

## 7. Nachrichtenkanal

Dem Benutzer ausschließlich diesen nativen Schritt nennen:

```bash
hermes gateway setup
```

Für ein anderes Profil den vorher verifizierten Profilaufruf angeben. Auf „Kanal eingerichtet“ warten. Gespeicherte Credentials, enabled-Status und echte Verbindung unterscheiden. Allowlist/DM-Pairing auf den Besitzer begrenzen. Eine kurze Nachricht hin und zurück sowie nach Möglichkeit eine harmlose Datei testen. Keine Credentials in Chat oder Report.

## 8. Dauerbetrieb

Native Linux-Serviceführung prüfen und nach erteilter Freigabe verwenden:

```bash
hermes gateway install
hermes gateway start
hermes gateway status
hermes cron status
```

Bei bereits laufendem Service nichts doppelt installieren/starten. Falls Start nach Logout/Boot zusätzliche Benutzer-Service-Einstellungen erfordert, Auswirkungen zeigen und nötige Freigabe einholen; keinen Reboot auslösen. Funktionsnachweis durch Servicezustand, Schedulerstatus und echten Joblauf, nicht allein „installiert“. Nachweis nach Host-Neustart nur bei separat genehmigtem Neustart, sonst ausdrücklich offen lassen.

## Quellen

- https://hermes-agent.nousresearch.com/docs/user-guide/messaging
- https://hermes-agent.nousresearch.com/docs/user-guide/features/skills
- https://hermes-agent.nousresearch.com/docs/user-guide/security
- https://hermes-agent.nousresearch.com/docs/user-guide/which-file-does-what
