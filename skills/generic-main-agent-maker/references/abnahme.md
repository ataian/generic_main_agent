# Abschluss der Zielinstallation

Diese Checkliste wird erst bei der späteren bewussten Einrichtung ausgeführt. Paketautoren dürfen sie nicht als bereits bestandene Laufzeitprüfung ausgeben.

| Pflichtpunkt | Nachweis |
|---|---|
| Zielinstanz | Effektives Home/Profil, Benutzer, Zeitzone und Terminal-Backend dokumentiert |
| SOUL | Zustimmung, Vorzustandsicherung, wirksamer personalisierter Inhalt in frischer Sitzung |
| Skills | Manifest vollständig, Pakete samt Referenzen vorhanden, native Discovery/Laden geprüft |
| Arbeitsraum/PDF | Eigener Dateitest; dediziertes PDF-venv und tatsächlicher kleiner PDF-Roundtrip |
| Vault | Tatsächlicher Pfad, sinnvolle Notiz + Hub-Erreichbarkeit, lokale Git-Historie, keine Secrets |
| Kanal | Besitzerzugriff begrenzt, echte Nachricht hin/zurück, Dateiübertragung soweit unterstützt |
| Gateway | Dauerbetrieb und funktionierender Scheduler; ohne erteilten Reboot keine Bootprüfung behaupten |
| Firecrawl | Echte Key-Eingabe lokal, echter Fingerprint, Suche/Extraktion getrennt; Registrierung/Fallback separat |
| Hindsight | Lokale API→lokale DB nachgewiesen, eigene Bank, Retain/Recall/Reflect/Konsolidierung, frische Sitzung und persistente Daten |
| Daily Summary | Genau ein eigener aktiver 02:00-Job, korrekte Zeitzone, eigener Vortag, keine Dubletten |
| Backup | Genau ein eigener aktiver 03:00-no-agent-Job, 30 Tage, geschützte lokale Sicherung, Fehlerziel |
| Wiederherstellung | Isolierte DB-/Datei-Wiederherstellung und Hindsight-Funktionsprobe, Live-Daten unverändert |
| Betriebsnotiz | Versionen, lokale Pfade, Status-/Update-/Restore-Weg, Quellen und offene Grenzen im Vault |

## Abschlussbericht

Nur knappe tatsächliche Ergebnisse: `verifiziert`, `konfiguriert, noch ungeprüft`, `wartet auf Benutzer/Betreiber` oder `blockiert`. Keine Gesamtmeldung „fertig“, solange ein Pflichtpunkt fehlt. Eine ausstehende Router-Registrierung nicht verstecken; unabhängige Teile dürfen fertig sein.

Dokumentiere in `System/Assistant/Einrichtung.md` des Ziel-Vaults:

- Installierte Komponenten/Versionen und Herkunft; tatsächliche Dienst-/Dateipfade.
- Zielprofil, Vault, eigene Bankkennung, lokale Bindings (keine Passwörter oder Schlüssel).
- Native Statusbefehle, Updateweg mit vorgeschalteter Sicherung, Wiederherstellungsreferenz.
- Cron-IDs, Zeitpläne, Zeitzone und Fehlerziel; keine Chat-Tokens.
- Getestete Funktion und explizit nicht durchgeführte Prüfungen.
- Hinweis: gleiches Hostbackup ersetzt keine externe gesicherte Kopie.

## Sicher fortsetzen oder zurücknehmen

Journal lesen, Zustand neu prüfen, nur offene Schritte ausführen. Bei Rücknahme zuerst aktive eigene Jobs deaktivieren und dokumentierte Dienste kontrolliert nach Freigabe stoppen; nicht über fremde Dienste hinweg arbeiten. Gesicherte Dateien erst nach Vergleich zurückspielen. Seit Einrichtung entstandene Nutzerdaten und Memories erhalten; niemals Datenbank-Volumes als „Rollback“ löschen. Destruktive Rücknahme separat freigeben lassen.
