# generic-main-agent

## Status

Diskussionsprojekt. Auftrag und erste Themen sind festgehalten; die Aufteilung der SOUL-Grundvorlage ist abgestimmt. Weitere Einrichtungsschritte und der Skill sind noch nicht vollständig konzipiert oder umgesetzt.

## Ziel

Für Max' Kollegen eine deutschsprachige HOWTO erarbeiten: vom frischen Linux mit offizieller Hermes-Installation zu einem persönlich eingerichteten Hauptagenten.

Zusätzlich soll ein weitergebbarer Skill entstehen, den ein frisch installierter Hermes mit bereits konfiguriertem Modell nutzen kann, um seinen Benutzer durch die anschließende Einrichtung zu begleiten.

## Einstieg der späteren HOWTO

Der erste Schritt ist der offizielle Linux-Installationsbefehl:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

Quelle: https://hermes-agent.nousresearch.com/docs/getting-started/installation

Der Befehl wurde für dieses Projekt nur aus der offiziellen Dokumentation übernommen, nicht ausgeführt. Die Installations- und Modellkonfigurationsschritte werden nicht nachdokumentiert: Dafür verweist die HOWTO auf den offiziellen Ablauf. Voraussetzung für den begleitenden Skill ist ein funktionierender, rudimentärer Hermes mit konfiguriertem Modell.

## Von Max genannte Themen

Die Liste ist ein Ausgangspunkt, keine abschließend festgelegte Reihenfolge oder vollständige Spezifikation.

1. **SOUL**
2. **Hauptagent definieren** — Chat-Kanal, beispielsweise Telegram.
3. **Obsidian Vault Regel**
4. **Hindsight**

## Geplante Ergebnisse

- Eine kurze, praktisch ausführbare HOWTO für Kollegen.
- Ein dazu passender, portabler Einrichtungs-Skill für den frisch installierten Hermes.
- Verständliche Prüfschritte, mit denen die erfolgreiche Einrichtung nachgewiesen werden kann.

## Festgelegt: SOUL-Grundvorlage

- Eine vorbereitete Grundvorlage, keine vollständige Neuerarbeitung im Einrichtungsdialog.
- Marikos aktuelle `SOUL.md` dient als Vorbild.
- Nur wenige persönliche Angaben sollen angepasst werden müssen: Agentenname, Name und Ansprache des Benutzers, Rolle und gewünschter Umgangston. Außer den Namen erhalten sie brauchbare Standardwerte; Avatar und Motto bleiben optional.
- Die konkrete Vorlage ist noch nicht erstellt; Marikos aktive SOUL bleibt unverändert.

### Abgestimmte Aufteilung

- Gemeinsamer Kern: gewissenhafte und selbständige Arbeitsweise, ehrliche Rückmeldungen, Schutz von Daten, abgestufte Autonomie, Freigabegrenzen, angemessene Verifikation und minimale Änderungen.
- Kleiner persönlicher Bereich: Agentenname, Name und Ansprache des Benutzers, Rolle und gewünschter Umgangston. Avatar und Motto bleiben optional.
- Umgebung getrennt ergänzen: eigene Arbeitsbereiche und konkret geschützte Systeme, soweit vorhanden. Keine Servernamen, persönlichen Beziehungen oder bestehenden Freigaben aus Marikos Umgebung übernehmen.
- Keine vorhandene Sandbox, Zusatzskills, anderen Agenten oder laufenden Dienste voraussetzen. Benötigte Abhängigkeiten müssen mitgeliefert, später ausdrücklich eingerichtet oder durch eigenständig verständliche Regeln ersetzt werden.
- Der Einrichtungs-Skill fragt die wenigen persönlichen Angaben ab und legt die angepasste SOUL vor der Aktivierung zur Zustimmung vor.

## Noch gemeinsam zu klären

- Bedeutung und gewünschter Umfang der vier Themen, insbesondere der Obsidian-Vault-Regel.
- Welche Schritte verbindlicher Standard sind und welche optional bleiben.
- Welche Vorgaben aus Max' Arbeitsweise verallgemeinert werden sollen, ohne Marikos Identität, private Daten oder konkrete Infrastruktur zu übernehmen.
- Welche Schritte der Skill nach Zustimmung ausführt und wo der Benutzer selbst tätig werden muss.
- Bereitstellung des Skills und Erprobung auf einer frischen Installation.

## Abgrenzung

- Jetzt: gemeinsames Besprechen und Festhalten der Anforderungen.
- Noch keine Installation, Änderung einer SOUL, Einrichtung von Chat-Kanälen oder Änderung an Hindsight.
- Kein Klonen von Mariko, keine Übernahme von Zugangsdaten, privaten Erinnerungen oder fremden Profilkonfigurationen.
- Kein automatischer Aufbau eines Multi-Agent-Teams.
