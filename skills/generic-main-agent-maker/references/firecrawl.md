# Firecrawl-Router als Client anbinden

Nur der spätere Zielagent führt diesen Ablauf aus. Kein Aufbau des Routers oder eines Tunnels.

## 1. Bereitgestellten Zugang prüfen

Vom Betreiber genannten Endpoint übernehmen und seine Erreichbarkeit mit einer kleinen nicht-sensitiven Anfrage prüfen. Keine lokalen Beispielports als zugesicherte Infrastruktur ausgeben. HTTP nur über einen bereitgestellten geschützten lokalen Zugang; entfernte öffentliche Endpoints benötigen HTTPS.

Die offizielle Hermes-Integration unterstützt `FIRECRAWL_API_URL` als Endpoint-Variable. Den bereitgestellten Wert entsprechend der Dokumentation der installierten Version hinterlegen; diese integrationsspezifische Variable ist kein Geheimnis. Kein Abschalten der Router-Authentifizierung oder Ändern von Servereinstellungen.

## 2. Benutzer hinterlegt den Key

Den tatsächlich aufgelösten `.env`-Pfad der Zielinstanz nennen und sagen:

> Bitte hinterlege jetzt deinen eigenen Firecrawl-API-Key als FIRECRAWL_API_KEY in der .env deiner Hermes-Instanz. Poste den Schlüssel nicht hier. Sag mir Bescheid, wenn du fertig bist; ich warte.

Vorhandene `.env` nicht überschreiben. Benutzer soll genau eine einfache Zuweisung hinzufügen/aktualisieren. Datei nur für ihren Eigentümer lesbar/schreibbar machen. Kein Key in Shell-History, Kommandoargumenten oder Screenshots. Auf Rückmeldung warten.

## 3. Fingerprint für Max

Den mitgelieferten Helfer aus seinem tatsächlich aufgelösten Pfad ausführen:

```bash
python3 /ABSOLUTER/PAKETPFAD/skills/generic-main-agent-maker/scripts/firecrawl_fingerprint.py --env-file /ABSOLUTES/HERMES_HOME/.env
```

Die beiden Beispielpfade zuvor durch ermittelte absolute Pfade ersetzen. Der Helfer wertet kein Shellprogramm aus, akzeptiert genau eine einfache Zuweisung und hasht den getrimmten Key wie der Router. Unterstützt unquotierte oder einfach quotierte Werte ohne Interpolation/Escapes. Bei ungewöhnlichem dotenv-Format oder extern verwalteten Secrets anhalten und den dokumentierten sicheren Parser der Zielinstallation verwenden; niemals einen anderen Wert stillschweigend hashen. Eine bereits vorhandene Prozessvariable kann vom Dateiwert abweichen: den wirksamen Web-Client nach dem Laden separat prüfen.

Nur den wirklich ausgegebenen Hash weitergeben:

> Gib Max bitte folgenden Fingerprint für den Firecrawl-Router:

Darunter den vollständigen berechneten Fingerprint. **Kein Beispielhash**, keine eigene Registrierung, keine automatische Nachricht an Max. Im Journal `router_registration: waiting_user` setzen. Andere Einrichtungsschritte können fortgesetzt werden.

## 4. Native Web-Werkzeuge auf den Router ausrichten

Für das richtige Profil, nach Prüfung der aktuellen Konfigurationsschlüssel:

```bash
hermes config set web.backend firecrawl
hermes config set web.search_backend firecrawl
hermes config set web.extract_backend firecrawl
hermes config set web.keyless_fallback false
hermes config set web.keyless_rescue false
```

Die Endpoint-Variable und den Key aus der Zielinstanz beziehen. Legacy-Konfigurationen mit `web.use_gateway: true` dürfen die direkte Route nicht übersteuern; bei vorhandener Legacy-Einstellung gezielt auf `false` setzen. Keine Einstellungen anderer Toolgruppen verändern. Client-Rettungswege zu anonymen Fremdanbietern deaktivieren; den bewusst vorhandenen **Router-Cloud-Fallback** nicht damit verwechseln.

Bei gecachtem Key/Client den unterstützten Aktivierungsweg ermitteln und vor einem notwendigen Gateway-/Sitzungsneustart Freigabe einholen. Keine Erfolge aus einer alten Sitzung dem neuen Key zuschreiben.

## 5. Prüfen

- `web_search` mit harmloser öffentlicher Suchanfrage, `web_extract` mit unkritischer öffentlicher URL separat ausführen.
- Konfiguration/Endpoint und Ergebnisse belegen. Eine gültige Suchantwort allein beweist weder die Routerroute noch Registrierung oder korrekte Cloud-Abrechnung.
- Max' Bestätigung der Registrierung als Betreiberbestätigung kennzeichnen, nicht als eigenen technischen Test.
- Cloud-Funktion erst bei genehmigtem Test mit möglichem Creditverbrauch bestätigen. Keine absichtliche Auslösung beliebig vieler kostenpflichtiger Requests. Ohne zulässigen Test „Registrierung bestätigt, Cloud-Funktion nicht selbst getestet“ festhalten.
- Lokale Antwort ohne registrierten Key kann funktionieren; kein heimlicher Direktzugriff auf Firecrawl Cloud als vermeintliche Reparatur.

## Quellen

- https://hermes-agent.nousresearch.com/docs/user-guide/features/web-search
- Routervertrag dieses Pakets: lokaler Betrieb vor Cloud-Fallback; Cloudfreigabe über registrierten SHA-256-Key-Fingerprint, eigene Schlüssel je Benutzer. Änderungen dieses Betreibervertrags müssen mit Max abgestimmt werden.
