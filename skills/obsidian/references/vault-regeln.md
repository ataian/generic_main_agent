# Vault-Regeln für ein neues oder bestehendes System

Diese portable Ableitung gilt für die jeweils freigegebene lokale Wissensablage. SOUL, Datenschutz und konkrete Freigabegrenzen bleiben maßgeblich. Die Regeln installieren keine Automatisierung.

## 1. Bestehendes respektieren, Neues klein beginnen

Den tatsächlichen Vault und seinen Einstieg zuerst feststellen. Einen geeigneten vorhandenen Einstieg wie `README.md`, `MOC.md` oder `00_Index.md` anhand seines Inhalts prüfen und weiterverwenden; nicht allein wegen dieses Regelwerks umbenennen oder einen zweiten Index erzeugen.

Nur bei frisch bestätigtem fehlendem Vault im freigegebenen Setup `~/obsidian_vault` verwenden. Ein neuer Vault beginnt mit `00_Index.md`; der für die verbindliche Tageszusammenfassung benötigte Bereich kann mit `Daily/Daily Notes.md` hinzukommen. Weitere Ordner erst mit realem Inhalt erzeugen. Keine leeren Themenbäume auf Vorrat.

## 2. Inhalt entscheidet über Ablage

| Bereich | Geeigneter Inhalt |
|---|---|
| `System/` | Dauerhaftes Betriebswissen, Dienste, geprüfte Konfiguration, Runbooks |
| `System/Assistant/` | Betrieb und Automatisierung des eigenen Assistenten |
| `System/Installations/` | Installationsanleitungen |
| `System/Archiv/` | Historische Quellen, ausdrücklich keine aktuelle Betriebsautorität |
| `Projects/` | Projektziele, Pläne und Projektstände |
| `Analyses/` | Fachliche Analysen; Buchanalysen bei Bedarf unter `Analyses/Ebooks/` |
| `Preferences/` | Persönliche Präferenzen und Identitätsreferenzen, keine neue SOUL-Autorität |
| `Trips/` | Reiseplanung |
| `Inbox/` | Noch nicht einsortierte Gedanken |
| `Daily/` | Tagesnotizen |
| `Reports/` | Wiederkehrende Berichte |
| `Briefings/` | Briefings |

Die Tabelle ist eine Konvention, kein Auftrag zur Migration. Sinnvolle vorhandene Bereiche bleiben bestehen. `System/Assistant/` ist kein Sammelordner für jedes Gesprächsthema.

Ein Projekt oder eine Reise beginnt mit einer aussagekräftigen Einzeldatei, etwa `Projects/Projektname.md`. Einen eigenen Unterordner erst bei mehreren wirklich benötigten Dateien anlegen. Dokumente nicht künstlich aufteilen. Bei einer beauftragten späteren Verschiebung Inhalte und betroffene Links erhalten.

## 3. Hubs bis Ordnerebene 2

Ein Hub ist eine Markdown-Übersicht mit echten Links, nicht bloß ein Dateiname.

- `System/` liegt auf Ebene 1, `System/Assistant/` auf Ebene 2, `System/Assistant/logs/` auf Ebene 3.
- Inhaltliche, tatsächlich benutzte Verzeichnisse auf Ebene 1 und 2 benötigen einen Hub. Vorhandene geeignete Übersichten und Projekt-Hauptdokumente wiederverwenden.
- Fehlt ein Hub, standardmäßig `<Ordner>/<Ordnername>.md` anlegen. Sonderkonvention für neue Tagesnotizen: `Daily/Daily Notes.md`.
- Ab Ebene 3 keine künstlichen Hubs erzwingen. Bestehende sinnvolle tiefere Hubs nicht entfernen.
- Keine Hubs für `.git/`, `.obsidian/`, `node_modules/`, reine Code- oder Anhangsordner. Inhaltliche Markdown-Dokumentation ist nicht pauschal technisch.
- Keine Obsidian Bases erzeugen oder einbetten.

## 4. Erreichbarkeit durch tatsächliche Notizlinks

1. Der Einstieg verlinkt pro Hauptbereich dessen Hub, nicht jede einzelne Unterseite.
2. Haupt-Hubs verlinken den Einstieg; Unter-Hubs den übergeordneten Hub.
3. Ein Hub verlinkt seine unmittelbaren Notizen und Unter-Hubs.
4. Jede Inhaltsnotiz verlinkt den zuständigen Hub oder die tatsächliche Themennotiz.
5. Tiefere Notizen ohne eigenen Hub müssen vom Ebene-2-Hub oder der Themennotiz auch vorwärts verlinkt sein.
6. Root-Inhaltsnotizen werden direkt vom Einstieg verlinkt und verweisen zurück.

Jede inhaltliche Notiz muss über existierende Notizlinks vom Einstieg erreichbar sein. Die Anzahl der Linkschritte ist **nicht** auf zwei beschränkt. Ordnerlinks und automatische Backlinks ersetzen keinen Vorwärtslink.

Vault-relative Wikilinks bevorzugen, mit Alias bei Bedarf:

```markdown
[[System/System|System]]
[[System/Assistant/Assistant|Assistant]]
[[Daily/Daily Notes|Daily]]
[[00_Index]]
```

Diese Beispiele nur verwenden, wenn die genannten Dateien tatsächlich existieren. Bei vorhandenen anderen Hub-Namen die tatsächlichen Pfade verwenden. Für unveränderliche Archivquellen genügt ein Vorwärtslink vom Hub; keinen Elternlink in geschützte Originale hineinschreiben.

**Beispiel für Ebene 3:** `00_Index.md` verlinkt `System/System.md`, dieser Hub `System/Assistant/Assistant.md`. Der Assistant-Hub verlinkt unmittelbar `System/Assistant/logs/Diagnose.md`; die Diagnose verlinkt den Assistant-Hub zurück. Ein `logs/logs.md` ist dafür nicht nötig.

## 5. Besondere Notizen

- Inbox: kleine Einzelnotizen, sinnvoller Name, Vorwärtslink aus dem Inbox-Hub und Rücklink. Keine Pflicht-Metadaten, automatische Sortierung oder Entsorgung.
- Neue Tagesnotizen: `Daily/YYYY-MM-DD.md`; neue Briefings: `Briefings/YYYY-MM-DD.md`. Bestehende lokale Ordner- und Namenskonventionen vor einer Änderung prüfen.
- Berichte: Haupt-Hub `Reports/Reports.md`, thematische Ebene-2-Hubs nur bei tatsächlicher Nutzung.
- Die verpflichtende Tageszusammenfassung läuft separat täglich um 02:00 lokale Zeit für den Vortag. Das Ablageregelwerk selbst legt keinen Job an und ändert keine Zeitpläne.

## 6. Daten und bestehende Inhalte schützen

Keine Geheimnisse in Notizen, Anhängen oder Git: auch kein Passwort, Token oder privater Schlüssel in einem privaten Repository. Nur gefahrlos dokumentierbare Einstellungen, Quellen, Prüfstand und Ergebnisse aufnehmen. Rohtranskripte und komplette Konfigurationsdateien sind keine Wissensnotizen.

Keine ungefragte vaultweite Umstrukturierung. Vor größeren beauftragten Änderungen einen gesicherten Ausgangsstand einschließlich uncommitteter Änderungen herstellen. Aktive Leser und Schreiber im genehmigten Umfang berücksichtigen; Zeitpläne, Modelle, Zustellung und pausierte Zustände nicht nebenbei ändern. Kein Hindsight-Sync und keine fremden Memory-Banken als Teil einer Notizkorrektur.

Lokales Git dient der Historie. Remote und Veröffentlichung benötigen eine eigene Benutzerentscheidung. Git ersetzt kein unabhängiges Backup.

## 7. Abschlussprüfung für jede betroffene Notiz

- [ ] Richtiger Vault, sinnvoller Bereich, kein unnötiger Ordner.
- [ ] Bestehender Einstieg und passende Hubs wiederverwendet.
- [ ] Pflicht-Hubs der betroffenen Inhaltsbereiche auf Ebene 1 und 2 vorhanden.
- [ ] Eltern-/Themenlink und expliziter Vorwärtslink zeigen auf existierende Dateien.
- [ ] Vollständige Linkkette vom Einstieg geprüft, auch für tiefe Notizen.
- [ ] Benutzerinhalt und geschützte Originale erhalten, keine Secrets.
- [ ] Bei beauftragter Verschiebung betroffene Verweise repariert.

Nur diesen tatsächlich geprüften Umfang melden. Eine Watchdog-Durchsetzung nicht behaupten, sofern Einrichtung und Prüfumfang nicht separat nachgewiesen sind.
