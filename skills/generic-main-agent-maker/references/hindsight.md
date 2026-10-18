<!-- SPDX-License-Identifier: MIT -->
# Hindsight: lokale Datenhaltung, bereitgestellte Inferenz

**Status dieses Pakets:** neu verfasstes MIT-Rezept mit statischer Quellenprüfung. Keine Installation, kein Containerstart, kein Registry-Pull und kein Retain-/Recall-Test wurden beim Erstellen ausgeführt. Die folgenden Aktionen sind ausschließlich für eine spätere, ausdrücklich freigegebene Einrichtung beim Kollegen bestimmt.

## 1. Feste Architektur und Grenzen

```text
Hermes auf dem Linux-Host
  └─ HTTP + eigenes Bearer-Token → 127.0.0.1:9177
       Hindsight API-slim im Container (network_mode: host)
       ├─ PostgreSQL → 127.0.0.1:<eigener freier DB-Port>
       │                Docker-Portbindung → db:5432 → eigenes persistentes Volume
       ├─ OpenAI-kompatibles LLM → bereitgestellter Host-Loopback-Endpunkt
       ├─ TEI Embeddings        → bereitgestellter Host-Loopback-Endpunkt
       └─ TEI Reranking         → bereitgestellter Host-Loopback-Endpunkt
```

Es gibt genau zwei Compose-Dienste: `api` und `db`. Keine Web-UI, keinen zusätzlichen MCP-Server, keinen Host-PostgreSQL, kein pg0, keine systemd-Units, lokalen Modelle, neuen Tunnel oder Serveradministration. Die API hat **kein Datenvolume**: ihr Datenbankziel wird ausdrücklich gesetzt. PostgreSQL erhält das eigene Compose-Volume `pgdata`. Docker muss als vorhandener Dienst zuverlässig starten; `restart: unless-stopped` ersetzt weder einen deaktivierten Docker-Daemon noch fehlende externe Tunnel.

**Warum Host-Netzwerk nur für die API?** Ein gewöhnlicher Bridge-Container erreicht mit `127.0.0.1` nur sich selbst; `host.docker.internal` oder eine Gateway-Adresse machen einen ausschließlich an Host-Loopback gebundenen Tunnel nicht automatisch erreichbar. Hier teilt nur die API den Netzwerk-Namespace des Linux-Hosts. Der Startbefehl `hindsight-api --host 127.0.0.1 --port 9177 --workers 1 --no-access-log` ist im ausgewählten Quellstand nachgewiesen und übergibt `args.host` direkt an Uvicorn. Das All-in-one-Startskript wird umgangen. Bei diesem Dienst gibt es keine `ports:`-Sektion. PostgreSQL bleibt im Bridge-Netz mit Veröffentlichung **ausschließlich** auf `127.0.0.1`.

Das ist keine Sicherheits-Sandbox: Host-Netzwerk erlaubt der API grundsätzlich Zugriff auf andere Host-Netzdienste; Docker-Administratoren können Containerumgebung und damit Secrets einsehen. Keine Home-Verzeichnisse, SSH-Schlüssel, Geräte oder Docker-Sockets einbinden; kein `privileged`. API-Token und DB-Passwort sind zusätzlich zu Loopback erforderlich. Andere lokale Benutzer sind ohne Token nicht zum Bankzugriff berechtigt. API-Health kann ohne Token sichtbar bleiben.

**Datenfluss offenlegen:** Datenbank und Erinnerungen liegen lokal, Inhalte und Suchanfragen werden aber zur Extraktion, Einbettung, Neubewertung und Synthese an die bereitgestellten Modell-APIs übertragen. Deren zentrale Verarbeitung, Protokolle und Caches sind außerhalb dieses Makers. Keine Zusage „alle Daten bleiben auf dem Rechner“. Diese Topologie konfiguriert keinen Cloud-Fallback; sie ist keine technische Egress-Firewall gegen beliebigen fehlerhaften Fremdcode.

## 2. Geprüfter Versionsrahmen statt `latest`

Statischer Quellenstand: 18.10.2026; vor späterer Einrichtung aktualisieren, wenn eine andere Version gewählt wird.

| Baustein | Festgelegter Rezeptstand / tatsächliche Grenze |
|---|---|
| Hindsight Server | Release `v1.0.0`, Quellcommit `39c65ffe2f140d0c84cee58566cad8900c5b9908` |
| Image-Kandidat | `ghcr.io/vectorize-io/hindsight-api:1.0.0-slim`; Release-Workflow publiziert API-only mit `INCLUDE_LOCAL_MODELS=false`, `PRELOAD_ML_MODELS=false` |
| PostgreSQL/pgvector | Kandidat `pgvector/pgvector:0.8.7-pg18-bookworm`; offizielle pgvector-Tagliste führt ihn, Hindsight führt PostgreSQL 18 in seinem External-PG-Beispiel |
| PG-Datenmount | PostgreSQL 18: Volume an `/var/lib/postgresql`; nicht ungeprüft den PG17-Pfad verwenden |
| Hermes-Plugin | Katalog beim Quellenabruf: `1.2.3`, Commit `d952b6e655fccab4581ee0722b51c5f103873d12`, verlangt Hermes `>=0.21.4` |
| Plugin-Abhängigkeiten | Am Katalog-Pin `hindsight-client>=0.10.1,<1` und `hindsight-embed>=0.10.1,<1`; durch Hermes verwalten lassen |

**Kein getestetes Kompatibilitätszertifikat:** API-Routen, Konfigurationsschlüssel, CLI-Bindung und Image-Buildweg wurden gelesen. Image-Verfügbarkeit für die konkrete CPU, Signatur, Registry-Digest, migrationsfähige DB, Client/Server-Zusammenspiel und Modelleignung sind später zu belegen. Die Client-Obergrenze `<1` darf nicht eigenmächtig entfernt werden, nur weil der Server `1.0.0` heißt. Die verwendeten HTTP-Verträge bestehen im gewählten Server; die echte Hermes-Prüfung bleibt Pflicht.

Später, nach Quellen-/Installationsfreigabe, mit vorhandenem Registry-Werkzeug die Manifest-Digests aus der **echten Registry** lesen, z.B.:

```bash
docker buildx imagetools inspect ghcr.io/vectorize-io/hindsight-api:1.0.0-slim
docker buildx imagetools inspect pgvector/pgvector:0.8.7-pg18-bookworm
```

Fehlt Buildx, ein bereits vorhandenes passendes Registry-Werkzeug verwenden oder diesen Schritt anhalten; kein automatischer Zusatzinstaller. Manifestplattform gegen die Ziel-CPU prüfen. Imageidentität und, soweit verfügbar, Release-Signatur verifizieren; Hindsight publiziert eine Cosign-Verifikation im Release-Workflow. Einen Hash nicht mit Vertrauenswürdigkeit gleichsetzen.

Die lokalen Werte müssen danach lauten: `repository:konkreter-tag@sha256:<tatsächlich ermittelter Digest>`. Es wird **kein** Digest aus dieser Anleitung übernommen und kein `latest` nachgeladen. Tag, Digest, Plattform, Quellcommit und Prüfmethode ohne Secrets lokal dokumentieren. Ein späterer Versionswechsel erfordert neue Quellprüfung und Restore-/Migrationstest; keine automatische Aktualisierung von Images oder Plugin.

## 3. Voraussetzungen und einmalige Anschlussdaten

Der Maker ermittelt Vorhandenes lesend und fragt nur nicht ermittelbare Anschlussdaten ab:

- Funktionierendes Hermes mit konfiguriertem Hauptmodell, Zielinstanz und tatsächliches `$HERMES_HOME` eindeutig geklärt. Keine andere Instanz verändern.
- Native Linux Docker Engine und Compose v2 vorhanden/nutzbar; Host-Netzwerk teilt nachweislich den benötigten Host-Namespace. Den effektiven Docker-Kontext/Daemon inklusive `DOCKER_HOST`/`DOCKER_CONTEXT` prüfen: ausschließlich der lokale Daemon auf dieser Maschine, kein SSH-/TCP-Remote-Docker. Rootless Docker, Docker Desktop oder ein Docker-Terminalbackend sind **nicht ungeprüft kompatibel**. Hermes muss die Host-API erreichen. Fehlt das, anhalten statt Tunnel zu öffnen oder eine Systeminstallation zu erzwingen.
- Genehmigtes lokales Betriebsverzeichnis außerhalb von Git/Vault, Empfehlung `~/.local/share/generic-main-agent/hindsight`. Eindeutiger Compose-Projektname; keine Übernahme eines bereits existierenden gleichnamigen Projekts/Volumes.
- Freier API-Port `9177` und ein separat gewählter freier DB-Port. Vorher `ss -ltnp` und bestehende Compose-Projekte/Volumes prüfen. Ein vorher freier Port ist keine Reservierung: scheitert der eigentliche Bind, stoppen und Konflikt klären, fremden Listener niemals beenden.
- Eigene neue Bank-ID sowie separate neue Testbank-ID. Nur Kleinbuchstaben, Ziffern, `_` und `-`; keine fremden Banknamen, Benutzeridentitäten oder Erinnerungen kopieren.
- Betreiber liefert drei **bereits funktionierende** HTTP-Loopback-Basis-URLs, Auth-Anforderungen und Modelle. Keine Quellplan-Beispielports übernehmen.

### Protokollvertrag dieses minimalen Rezepts

1. **LLM:** OpenAI Chat Completions unter der gelieferten `/v1`-Base-URL, exakte Modell-ID aus `/models`, JSON-Schema/`strict` für strukturierte Antworten. Kontextfenster, Output-Limit, gegebenenfalls Thinking-Modus, Rate-/Parallelitätsgrenzen bestätigen. Der kleine JSON-Test allein beweist noch keine funktionierenden Hindsight-Extraktionsschemata; Retain, Reflect und Konsolidierung sind die anschließende echte Prüfung. Liefert `/models` keine ID, nicht aus einem Spitznamen ableiten. Ein SDK-Dummy als `LLM_API_KEY` ist nur bei ausdrücklich bestätigtem **authentifizierungsfreiem bereitgestelltem** LLM zulässig, nie als Ersatz für einen fehlenden echten Schlüssel.
2. **Embeddings:** TEI-kompatible Basis mit `GET /info` und `POST /embed`, kein `/v1/embeddings` unter falschem Providernamen. Exakte `model_id`, Dimension, Tokenlimit, Trunkierung, Normalisierung, eventuelle Query-/Passage-Präfixe vom Betreiber dokumentieren. Dimension wird von Hindsight durch eine echte Einbettung erkannt; der Checker vergleicht sie mit dem gelieferten Sollwert. Bestehende Daten nicht durch einen Dimensions-/Modellwechsel „reparieren“: Vektoren gleicher Länge sind bei anderem Modell ebenfalls nicht austauschbar.
3. **Reranker:** TEI-kompatibles `GET /info` und `POST /rerank` mit `query`, `texts`, `return_text`; Antworten als Liste mit `index` und `score`. Relevantes Textlimit und Modell-ID dokumentieren. „OpenAI-kompatibel“ besagt allein nichts über Reranking. Kleine Batchgröße 8 und Parallelität 1 sind lokale Anfangswerte; mit bereitgestellten Limits abgleichen.

**Wichtige Auth-Grenze:** Die geprüften TEI-Clients im Server `v1.0.0` besitzen keinen TEI-API-Key-Konfigurationsparameter und senden für diese Aufrufe kein Bearer-Token. Das Rezept gilt deshalb nur, wenn die vorhandenen TEI-Loopback-Zugänge bereits ohne zusätzliche HTTP-Authentifizierung nutzbar und durch den bestehenden Zugangsweg geschützt sind. Benötigt ein bereitgestellter Endpunkt einen TEI-Key, andere Header, TLS-Client-Zertifikate oder ein anderes Protokoll, ist dieser Schritt blockiert. Keine erfundenen `*_TEI_API_KEY`-Variablen, kein Secret in URL/Userinfo, kein Abschalten entfernter Auth, keine neue Proxy-/Tunnel-Konfiguration. Eine alternative Hindsight-Providerkonfiguration erst nach gezielter offizieller Quellenprüfung und Freigabe ableiten. Keine lokalen Modell-Downloads oder Cloud-Ausweichziele.

Fehlende Inferenzanschlüsse blockieren **nur Hindsight**, nicht die übrigen Onboarding-Schritte.

## 4. Vorlagen sicher materialisieren

Vor Änderungen konkret freigeben: zwei lokale Container, eigenes Volume/DB und Ports, Imagebezug, Plugin mit Abhängigkeiten, Änderungen ausschließlich an der Zielinstanz, synthetische Testbank, Inferenzanfragen sowie späterer kontrollierter Neustart nur dieser neuen Dienste. Installations-Sicherheitsregeln des Maker-Pakets gelten weiterhin.

Vorlagen in [templates/hindsight](../templates/hindsight/) sind **nicht direkt aktiviert**:

- [compose.yaml.example](../templates/hindsight/compose.yaml.example) → `compose.yaml`
- [.env.example](../templates/hindsight/.env.example) → lokale `.env`
- [init-db.sh.example](../templates/hindsight/init-db.sh.example) → `init-db.sh`
- [check.py.example](../templates/hindsight/check.py.example) → `check.py`
- [config.json.example](../templates/hindsight/config.json.example) → später profilbezogene Plugin-Konfiguration

`TEMPLATE_DIR` auf den tatsächlichen absoluten Checkout-Pfad zu `skills/generic-main-agent-maker/templates/hindsight` setzen. `RUN_DIR` ist das genehmigte Betriebsverzeichnis. **Vor** dem Kopieren sicherstellen, dass es neu ist; vorhandene Dateien nicht überschreiben:

```bash
umask 077
# TEMPLATE_DIR und RUN_DIR vorher aufgelöst und bestätigt, keine Secrets in Shellvariablen.
test ! -e "$RUN_DIR" || { printf '%s\n' 'Vorhandenes Ziel: prüfen, nicht überschreiben.'; exit 1; }
mkdir -p "$RUN_DIR"
chmod 700 "$RUN_DIR"
for file in compose.yaml .env init-db.sh check.py; do
  install -m 600 "$TEMPLATE_DIR/$file.example" "$RUN_DIR/$file"
done
# Kein Secret in diesem Skript; der Containerbenutzer postgres muss es lesen/ausführen können.
chmod 755 "$RUN_DIR/init-db.sh"
cd "$RUN_DIR"
```

Das PG-Entrypoint führt die ausführbare Initdatei im DB-Container als eigenen Prozess aus; keine Host-Ausführung des Init-Skripts. Eine hostseitige 600-Datei wäre für den Containerbenutzer `postgres` typischerweise nicht lesbar. Nur das geheimnisfreie Init-Skript erhält 755, `.env` bleibt 600. PG-Initialisierung läuft nur bei leerem **eigenem** Volume. Ein teilweise fehlgeschlagener Initlauf ist nicht durch blindes `up` repariert; erst Zustand und Besitz feststellen, Daten erhalten.

### Secrets und Parameter

`.env` enthält die ausdrücklich benannten Compose-Parameter und Secrets, niemals in Git, Vault, Chat, SOUL, Skill oder Testspeicher. Anders als native Hermes-Konfiguration ist dies die lokale Compose-Eingabedatei; für Hermes bleiben Nicht-Secrets im Konfigurationswerkzeug/Plugin-JSON. Keine `.env` als Shellcode einlesen; kein `set -x`, kein `docker compose config` ohne `--quiet`, kein unredigiertes `docker inspect` oder `env` in Berichten. Compose und Docker-Administratoren können Secrets sehen; lokale Datei 600 ist nicht verschlüsselt.

Drei unabhängige Secrets lokal direkt in die noch leeren Felder der `.env` schreiben, ohne Ausgabe:

```bash
python3 - <<'PY'
from pathlib import Path
import secrets
p = Path('.env')
s = p.read_text()
for key in ('POSTGRES_ADMIN_PASSWORD', 'HINDSIGHT_DB_PASSWORD', 'HINDSIGHT_API_TOKEN'):
    marker = key + '=\n'
    if s.count(marker) != 1:
        raise SystemExit('Feld nicht eindeutig leer; keine Secret-Rotation durchführen')
    s = s.replace(marker, key + '=' + secrets.token_hex(32) + '\n', 1)
p.write_text(s)
p.chmod(0o600)
PY
```

Die feste Hexform verhindert URL-Encoding-Fehler des DB-Passworts. Passwortänderungen in `.env` ändern **nicht** das Passwort einer bereits initialisierten DB. Keine ungefragte Rotation bei Wiederaufnahme.

Der Benutzer trägt den eigenen LLM-Key lokal mit einem sicheren Editor ein. Alle weiteren Pflichtwerte aus dem Betriebsinventar ergänzen. Das Prüfprogramm akzeptiert absichtlich nur eine einfache `.env`-Teilmenge: `KEY=Wert`, Kommentare als eigene Zeile, bei Leerzeichen einfache Anführungszeichen; keine `$`-Interpolation, Backslashes, Inline-Kommentare oder ausführbaren Anweisungen. Ein benötigtes anders formatiertes Secret nicht „normalisieren“; unterstützten sicheren Parser/Transport separat prüfen.

Die API bekommt **nur** die im Compose-File aufgeführten Variablen, nicht das ganze `.env` und nicht Hermes' Prozessumgebung. Keine `env_file`-Durchreichung hinzufügen. Alle vier LLM-Rollen (Retain, Reflect, Consolidation, Mental-Model-Refresh) werden auf dasselbe bereitgestellte Ziel gesetzt; keine Router-, Multi-LLM-, Reranker-Fallback- oder Read-/Migration-DB-Overrides. Hindsight-Bankkonfigurationen können eigene Einstellungen haben: nur neue Banken anlegen, später wirksame Overrides mitprüfen.

```bash
python3 check.py preflight --out preflight.json
docker compose --env-file .env -f compose.yaml config --quiet
```

Diese spätere Prüfung bestätigt Form/Schlüssel, **nicht** Herkunft, freie Ports, Kompatibilität oder Sicherheit des Endpunkts. Die Dateivorlage selbst führt nichts aus. Compose priorisiert exportierte Shellvariablen gegenüber `--env-file`: deshalb bricht `preflight` bei widersprechenden gleichnamigen Umgebungswerten ab. Einen bereinigten Zielkontext verwenden, Secrets dabei nicht ausgeben; vor Compose-Aufrufen in einer neuen Shell oder nach Änderungen den Preflight mit einem neuen Nachweisnamen wiederholen. Alle verkürzten `docker compose`-Befehle unten gelten nur im bestätigten `RUN_DIR` mit dieser `.env`/`compose.yaml` und demselben geprüften lokalen Docker-Kontext.

## 5. Bereitgestellte Modelle prüfen, dann lokale Dienste starten

Zuerst echte kleine synthetische Inferenzaufrufe nach Freigabe:

```bash
timeout 600 python3 check.py inference --out inference.json
```

Der Checker sendet keine Geheimnisse in Argumenten, folgt keinen Redirects und verwendet keine geerbten HTTP-Proxys. Er prüft LLM-ID/JSON-Ausgabe, beide TEI-Modelle, numerische Embeddings mit Soll-Dimension sowie Reranker-Antwortstruktur. `inference.json` lokal lesen: die passende Terminantwort muss höher als der irrelevante Autosatz bewertet werden. Diese fachliche Prüfung und Modelllimits/Normalisierung bleiben gesondert zu dokumentieren. Bei Fehlern nicht auf Cloud oder lokale Modelle wechseln.

Erst danach die digest-gepinnten Container beziehen und die DB allein starten:

```bash
docker compose --env-file .env -f compose.yaml pull
docker compose --env-file .env -f compose.yaml up -d --wait --wait-timeout 180 db
```

`pg_isready` im Healthcheck prüft Bereitschaft, **nicht** erfolgreiche App-Authentifizierung. Deshalb anschließend App-Zugang und Erweiterungen wirklich lesen:

```bash
docker compose exec -T db sh -c 'PGPASSWORD="$HINDSIGHT_DB_PASSWORD" exec psql -h 127.0.0.1 -U hindsight -d hindsight -v ON_ERROR_STOP=1' <<'SQL'
SELECT current_database(), current_user;
SELECT extname, extversion FROM pg_extension WHERE extname IN ('vector','pg_trgm','btree_gin') ORDER BY extname;
SELECT rolname, rolsuper, rolcreatedb, rolcreaterole FROM pg_roles WHERE rolname='hindsight';
SQL
```

Erwartet: DB/User `hindsight`, alle drei Extensions, App-Rolle ohne Superuser/Createdb/Createrole. Das separate `postgres`-Adminpasswort wird der API nicht gegeben. Die App besitzt nur ihre DB/Schema und kann darin die erforderlichen Migrationen ausführen. Kein `POSTGRES_HOST_AUTH_METHOD=trust`; Host- und lokale Socket-Authentifizierung werden mit SCRAM initialisiert.

```bash
docker compose --env-file .env -f compose.yaml up -d --wait --wait-timeout 300 api
docker compose ps
```

Die API läuft im Vordergrund als Container-Hauptprozess, benötigt keine zusätzliche Dienstverwaltung. Health wird als exaktes JSON `status == "healthy"` geprüft, nicht als Textsuche nach `healthy` (würde auch `unhealthy` treffen). `--wait` begrenzt die Bereitschaftsphase. Logs bei Fehlern ausschließlich lokal gezielt prüfen, da Fehlertexte eventuell Inhalte/URLs enthalten. Containerstart/HTTP 200 allein ist noch kein Erfolg.

### Lokale DB-Zuordnung und Bindings belegen

```bash
docker compose port db 5432
ss -ltnp
# DB-Inventar und API-Verbindung aus genau diesem Compose-Container:
docker compose exec -T db sh -c 'PGPASSWORD="$POSTGRES_PASSWORD" exec psql -U postgres -d hindsight -v ON_ERROR_STOP=1' <<'SQL'
SELECT system_identifier FROM pg_control_system();
SHOW data_directory;
SELECT datname, usename, application_name, client_addr FROM pg_stat_activity WHERE usename='hindsight';
SELECT version_num FROM public.alembic_version;
SQL
```

Erwartet: DB veröffentlicht nur `127.0.0.1:<gewählter DB-Port>`, API nur `127.0.0.1:9177`, kein `0.0.0.0`/`[::]`, keine neuen 8888-/9999-/MCP-Listener. Ein fremder vorhandener Listener ist nicht dem neuen Dienst zuzuschreiben. Native Linux-Docker-Version und Loopback-Publishing-Verhalten prüfen; alte Docker-Versionen können zusätzliche L2-Expositionsprobleme haben. Das Rezept ist keine Firewallprüfung von außen.

Nur gezielte Inspect-Felder verwenden: API `NetworkMode=host`, `Path`/`Args` mit explizitem `--host 127.0.0.1`, DB-Portbindings und Mountname/Label. Die effektive `HINDSIGHT_API_DATABASE_URL` **lokal ohne Ausgabe des Passworts** zerlegen: Schema `postgresql`, Host `127.0.0.1`, genau der veröffentlichte DB-Port, DB/User `hindsight`. `READ_DATABASE_URL`/`MIGRATION_DATABASE_URL` dürfen nicht auf andere Ziele zeigen. Der Host-Netz-API ist Docker-DNS `db` nicht als DB-Ziel zugesichert; deshalb nutzt sie bewusst den Host-Loopback-Port.

Volume-ID, Compose-Projektlabels, Postgres-System-ID und Migrationsrevision lokal notieren. Der API-DB-Client kann in PG als Docker-Gatewayadresse erscheinen; das widerlegt die lokale Zielzuordnung nicht. Den später erzeugten **Testbank-Datensatz in dieser konkreten DB** nachweisen: Das ist stärker als eine Bank-ID oder Healthantwort allein.

## 6. Echte Abnahme in eigener synthetischer Testbank

Das beiliegende `check.py` ist nur eine begrenzte Abnahmehilfe (Standardbibliothek), **kein zusätzlicher Hermes-API-Wrapper**, Plugin oder Dienst. Keine produktiven Inhalte einspeisen. Es erstellt bei `seed` ausschließlich `HINDSIGHT_TEST_BANK_ID` und verweigert die Übernahme vorhandener Banken. Die tatsächliche paginierte Bankliste wird gelesen; `GET .../config` allein ist kein Existenznachweis, weil Versionen auch für unbekannte Banken Defaults liefern können. `PUT` ist ein Upsert, deshalb vor Anlage Abwesenheit prüfen; während dieser Einzeleigentümer-Einrichtung keinen zweiten Schreiber parallel zulassen.

```bash
timeout 1800 python3 check.py seed --out memory-before-restart.json
```

Ablauf und Erfolgskriterien:

1. Ohne API-Key muss `GET /v1/default/banks` 401/403 liefern; anschließend mit eigenem Key arbeiten. Ein fehlerhafter `/health`-Auth-Test allein würde keine Bankabsicherung beweisen.
2. Neue Testbank anlegen, Bankliste und leere Stats zurücklesen.
3. Asynchron Retain eines ausdrücklich fiktiven deutschen Sachverhalts: **Projekt Kupferfink, Dienstag, Raum Birke, nicht Montag**. Sämtliche gelieferten Retain-Operations-IDs bis `completed` verfolgen. `pending`/`processing` sind kein Erfolg; `failed`/`cancelled` oder Timeout brechen ab.
4. `POST /v1/default/banks/{bank_id}/consolidate` mit `{}` anstoßen, gelieferte ID über den **bankqualifizierten** Operationspfad pollen. Kein erfundenes CLI-Kommando, kein beliebiges Schlafen und kein erneutes Retain als Ersatz für Konsolidierung. Automatische Konsolidierung ist ebenfalls aktiviert; der Trigger darf einen laufenden Vorgang deduplizieren.
5. Stats müssen tatsächliche Fakten **und** Beobachtungen, keine fehlgeschlagenen oder noch offenen Operations/Konsolidierungen melden. Zusätzlich echte `type=observation`-Einträge lesen, Recall ausführen, Reflect ausführen.
6. **Mensch/Maker bewertet den gespeicherten Inhalt:** Dienstag und Raum Birke stimmen, Montag wird negiert; kein erfundener persönlicher Fakt, keine aufgelöste Negation. Beobachtungen beziehen sich auf die gespeicherten Quellen. Eine nichtleere Reflect-Antwort, `completed` oder positive Zähler allein beweisen das nicht. `semantic_acceptance` bleibt im JSON deshalb ausdrücklich offen.

Dann direkt aus der lokalen DB lesen (die Bank-ID in dieser psql-Variablen ist der zuvor bestätigte **nicht geheime** Testwert):

```bash
# TEST_BANK_ID vorher exakt aus dem nicht geheimen Inventar setzen.
docker compose exec -T db sh -c 'PGPASSWORD="$HINDSIGHT_DB_PASSWORD" exec psql -h 127.0.0.1 -U hindsight -d hindsight -v ON_ERROR_STOP=1 --set=bank="$1"' sh "$TEST_BANK_ID" <<'SQL'
SELECT bank_id, fact_type, count(*) FROM public.memory_units WHERE bank_id=:'bank' GROUP BY bank_id,fact_type ORDER BY fact_type;
SQL
```

Bei Versionsabweichung Tabellenschema zuerst gegen Migrationen prüfen, keine Abfragen auf Verdacht reparieren. Bank-ID und Fakten in diesem Compose-DB-Container zusammen mit effektiver API-DSN und System-ID belegen die lokale Datenhaltung. Auch vorhandene Quelldokumente/Beobachtungen prüfen, nicht lediglich eine Gesamtzahl akzeptieren.

**Wiederaufnahme:** Die Hilfsprüfung ist absichtlich kein blind idempotenter Upsert. Bei Abbruch nach Bankanlage bleibt die Testbank erhalten; `seed` erneut auszuführen verweigert ihre Übernahme. Bankliste, Stats und `/operations` mit authentifiziertem, lokalem Zugriff anhand des gespeicherten OpenAPI-Vertrags untersuchen, Operationen bis Terminalstatus verfolgen. Danach `read` mit einem neuen Nachweisnamen. Unklare Testbank nicht löschen oder durch eine neue ID verstecken. `read` verlangt im isolierten Test keine offene Arbeit; konkurrierende automatische Retains erst regulär auslaufen lassen. Fehlende/gescheiterte Konsolidierung ist ein eigener Fehler und kein Anlass, Beobachtungsprüfungen abzuschalten.

## 7. Persistenz und Wiederanlauf

Erst wenn die Testbank fachlich stimmt und nur die **neu eingerichteten** Dienste zum Neustart freigegeben sind:

```bash
docker compose stop api
docker compose restart db
docker compose up -d --wait --wait-timeout 300 db api
timeout 600 python3 check.py read --out memory-after-restart.json
```

Vorherige und neue Nachweise vergleichen: gleiche Bank, gleiche persistierte Dokument-/Fakten-/Beobachtungsidentitäten, gleiche PG-System-ID und Volume-ID, erfolgreiche Recall-/Reflect-Ergebnisse und keine neuen Fehler. Nicht nur „Container healthy“. `read` erzeugt keine neuen Retain-Daten; eine frische Synthese kann sprachlich anders ausfallen. Im Testzeitraum keine Hermes-Schreiber parallel laufen lassen.

`restart: unless-stopped` und bestehende Docker-Autostartfähigkeit dokumentieren. Ein erfolgreiches Dienstneustart-Experiment beweist keinen getesteten Host-Boot; dieser wird nicht verlangt. Keine fremden Tunnel unterbrechen, kein Host-Reboot, kein Gateway-Neustart. Ausfall-/Recoverytests externer Inferenz nur mit eigener gesonderter Freigabe, nicht durch Abschalten geteilter Infrastruktur.

Zusätzlich Konfiguration, laufende Prozesse und gegebenenfalls vorhandene Hardwarebeobachtung prüfen: keine lokalen Embedding-/Reranking-Modelle, keine Modellgewichte im API-Container, kein GPU-Passthrough. `slim` plus explizite `tei`-Provider und `HF_HUB_OFFLINE`/`TRANSFORMERS_OFFLINE` verhindern beabsichtigte lokale Modellladung; sie sind kein Nachweis für alle möglichen Netzwerkzugriffe. Inhaltlich erfolgreiche Inferenz plus tatsächliche Konfiguration/Providerpfade getrennt von einem nicht durchgeführten Netzwerk-Mitschnitt ausweisen.

## 8. Hermes über aktuellen Katalog anbinden

Zielinstanz und `$HERMES_HOME` zuerst auflösen; Befehle nur in deren bereits festgelegtem Kontext ausführen. Vorzustand (Provider, Pluginversion, Plugin-JSON) sichern. Ein anderer aktiver Memory-Provider ist ein Konflikt: nur einen externen Provider aktivieren, keinen bestehenden still ersetzen. Das eingebaute MEMORY/USER bleibt zusätzlich aktiv.

```bash
hermes plugins list
# Nur falls nicht bereits kompatibel vorhanden, nach Abhängigkeitsfreigabe:
hermes plugins install hindsight
```

Aktuelle Katalogherkunft/Pin und tatsächlich installierte Version notieren. Kein `pip install hindsight-hermes` (veralteter Integrationsweg), kein Serverpaket in Hermes, keine geratenen venv-Pfade. Katalogabhängigkeiten können gemeinsam verwalteten Hermes-Paketstand beeinflussen; bei mehreren Profilen diese Wirkung separat abklären. Bei fehlender Abhängigkeitsfreigabe anhalten statt Lazy-Install-/PM-Sperren zu umgehen. `plugins enable` allein aktiviert einen exklusiven Memory-Provider **nicht**.

### Konfiguration und eigener API-Key

`$HERMES_HOME/hindsight/config.json` ist **plugin-eigenes JSON** und darf gezielt aus der Vorlage erzeugt werden; die allgemeine `config.yaml` niemals von Hand bearbeiten. Vorlage vollständig verwenden. `api_key` wird bewusst nicht in JSON aufgenommen. In der geschützten `.env` **dieser Hermes-Instanz** lokal `HINDSIGHT_API_KEY` auf das eigene `HINDSIGHT_API_TOKEN` aus dem lokalen Dienst setzen, ohne den Wert in Chat/Kommandoargumente zu kopieren. Bestehende `.env` sicher zusammenführen, keine Datei überschreiben oder als Shellcode laden.

Keine geerbten `HINDSIGHT_BANK_ID`, URL-/Modus-Overrides oder geteilte `~/.hindsight/config.json` unbemerkt übernehmen. Am geprüften Plugin-Pin hat ein vorhandenes `HINDSIGHT_BANK_ID` sogar Vorrang vor dem JSON-Bankwert. Einen Konflikt im Zielkontext bewusst korrigieren, nichts in anderen Profilen ändern. Projektbank-Templates, Zusatzbanken, Spiegelung und vertrauenswürdige Projektordner bleiben leer/deaktiviert.

Zunächst `bank_id` für die kontrollierte Hermes-Abnahme auf die eigene **Testbank** setzen. Native Aktivierung:

```bash
hermes config set memory.provider hindsight
hermes memory status
```

Die Kernwerte sind `local_external`, `http://127.0.0.1:9177`, Recall `mid`, `auto_recall=true`, `auto_retain=true`, `retain_every_n_turns=2`, `memory_mode=hybrid`. `local_external` bedeutet außerhalb des Hermes-Prozesses, hier auf demselben Host. Die Vorlage setzt zusätzlich `recall_types=[observation,world,experience]`: beim geprüften Katalog-Pin ist der Default inzwischen nur `observation`; Rohfakten sollen im Starter nicht bis zur Konsolidierung unsichtbar sein. Das ersetzt **nicht** die separate Beobachtungsprüfung.

### Frische Sitzung wirklich prüfen

Neue Hermes-Sitzung im richtigen Instanzkontext starten; Provider-Status `hindsight`/verfügbar und Tools `hindsight_retain`, `hindsight_recall`, `hindsight_reflect` tatsächlich prüfen. Alte laufende Sitzungen/Gateways können Providerzustand cachen; kein ungefragter zentraler Neustart.

- In einer frischen Sitzung nach dem gespeicherten fiktiven Kupferfink-Termin fragen, ohne die Antwort mitzuliefern. Explizites `hindsight_recall` muss die Testbank treffen; Reflect separat prüfen.
- In dieser Testbank ein weiteres klar markiertes synthetisches Faktum über `hindsight_retain` speichern; Verarbeitung über API/DB nachweisen und in einer **weiteren frischen Sitzung** ohne Hinweis auf den Faktwert wiederfinden.
- Für `auto_retain` mindestens zwei vollständige Benutzer-/Assistenten-Turns mit synthetischem Inhalt führen, regulär abschließen und tatsächliche neue Speicherung in Testbank/API/DB nachweisen. Zwei Toolaufrufe innerhalb eines einzigen Turns genügen nicht. Ein erfolgreicher expliziter Retain beweist automatische Retains nicht.
- Automatischen Recall getrennt beobachten. Bei asynchronem Prefetch kann Kontext erst im nächsten Turn erscheinen; bloßer Status/JSON und eine passende Vermutung des Hauptmodells zählen nicht als Recall-Nachweis.

Danach neue **eigene produktive Bank** anlegen, ohne Starter-Template/Altdatenimport:

```bash
python3 check.py create-own --out own-bank-created.json
```

Bank-ID in Plugin-JSON von Testbank auf `HINDSIGHT_BANK_ID` ändern, native Providerstellung erneut lesen und noch eine frische Ziel-Sitzung starten. Effektive URL/Bank und leere Bankstats bestätigen; keine Testfakten in die produktive Bank kopieren. In produktiver Bank keinen absichtlich falschen Testfakt hinterlassen. Testbank erhalten und als synthetische Abnahmebank kennzeichnen; Löschung nur nach gesonderter Zustimmung und eindeutiger Eigentumsprüfung.

## 9. Übergabe an Backup/Restore und Rückweg

Backup bleibt ein eigener Maker-Schritt: `~/backups`, täglich 03:00 lokale erkannte Zeitzone, 30 Tage, Schutz/Rotation wie im Hauptpaket freigegeben. Hier keine zusätzlichen Cronjobs, Syncs oder Watchdogs installieren.

Für die Sicherung übergeben:

- Absoluter Betriebsverzeichnispfad, Compose-Projekt/Volume, PG-System-ID, DB/User `hindsight`, alle Bank-IDs dieser **eigenen** Instanz.
- Digest-/Versionsinventar, Migrationsrevision, Modellidentität/Dimension/Präfixe, `compose.yaml`, `init-db.sh`, Plugin-JSON und native Providerstellung.
- Notwendige Secrets aus den lokalen `.env` separat geschützt, nicht in Git. Ohne benötigte Credentials und Betriebskonfiguration ist der Dump allein kein vollständiger Wiederanlaufplan.

Konsistenter DB-Dump später innerhalb eines neu angelegten geschützten Backup-Satzes (`BACKUP_SET` ist dessen bestätigter absoluter Pfad, nicht ein bestehendes erfolgreiches Set):

```bash
(
  set -euo pipefail
  umask 077
  test -d "$BACKUP_SET"
  test ! -e "$BACKUP_SET/hindsight.dump"
  test ! -e "$BACKUP_SET/hindsight.dump.partial"
  docker compose exec -T db sh -c 'PGPASSWORD="$POSTGRES_PASSWORD" exec pg_dump -U postgres -d hindsight -Fc --no-owner --no-acl' > "$BACKUP_SET/hindsight.dump.partial"
  docker compose exec -T db pg_restore --list < "$BACKUP_SET/hindsight.dump.partial" > /dev/null
  mv "$BACKUP_SET/hindsight.dump.partial" "$BACKUP_SET/hindsight.dump"
)
```

`pg_dump -Fc` liefert einen konsistenten DB-Snapshot; laufende PG-Datendateien nicht kopieren. Ein lesbares Inhaltsverzeichnis ist **noch kein Restore-Test**. Der Dump enthält Daten/Schema, nicht automatisch Cluster-Rollen: diese über die geprüfte Initvorlage und geschützte Credentials wiederherstellen.

**Isolierter Restore-Auftrag an den Backup-Schritt:** eigenes eindeutig gelabeltes Compose-Projekt, neues Volume, neuer Loopback-DB-Port; gleiche geprüfte PG-/Hindsight-Version zuerst. DB/Rolle/Extensions initialisieren und Dump mit `pg_restore --exit-on-error --no-owner --no-acl --role=hindsight` in diese getrennte `hindsight`-DB laden. Eigentums-/Extensionfragen und alle Restorefehler prüfen, nicht pauschal ignorieren. Eine separate API muss eine **andere freie Loopback-API-Portnummer** und die **Restore-DB-DSN** erhalten; alle Command-/Healthcheck-/Client-URLs konsistent anpassen. Vor ihrem Start effektive DSN, Port und Volume gegen Live-Inventar vergleichen. Restore-API erst freigeben, wenn sie keinesfalls auf die Live-DB zeigen kann.

`check.py` ist absichtlich auf `127.0.0.1:9177` festgelegt und darf **nicht unverändert** als Restore-Check benutzt werden: das würde die Live-API prüfen! Im isolierten Restore die tatsächlich geänderte API-URL benutzen und Bankinventar, Dokument-/Fakten-/Beobachtungszahlen und bekannte synthetische Recall-Fakten aus dem gesicherten Stand vergleichen. Recall/Reflect mit wiederhergestellter API erst nach Freigabe der dabei ausgelösten Inferenz und klar getrennt von einer reinen Offline-DB-Restoreprüfung. Kein Umschalten des produktiven Hermes für den Test. Kein Live-Volume überschreiben; keine `down -v`-/Prune-Befehle als Testcleanup. Nur nach Eigentums-/Labelprüfung und Freigabe ausschließlich eigene Restore-Ressourcen entfernen.

Bank-`/export`/`/import` ist **kein vollständiger Datenbankbackup**: diese API dient Bank-Templates/Konfiguration/Mental Models/Directives. Dokumenttransfer ist ein gesonderter versionsabhängiger Weg; keine Migration in diesem Maker. Der PostgreSQL-Dump ist hier die Wiederherstellungsbasis.

**Rückweg:** bei Problemen ausschließlich die neu angelegten Compose-Dienste stoppen, Volume behalten; Zielinstanz auf gesicherten vorherigen Provider/Plugin-JSON zurücksetzen (native Werte über `hermes config set`, nicht YAML-Edit). Bei zuvor deaktiviertem externem Provider `hermes memory off`. Keine automatische Plugin-Deinstallation mit möglichen gemeinsamen Paketfolgen und kein automatischer Löschbefehl. Nach realen produktiven Schreibvorgängen ist ein Rücksetzen auf ein älteres Backup mit Datenverlust verbunden und bedarf einer ausdrücklichen Entscheidung. Lokale Backups schützen nicht vor Maschinenverlust; Remote-Spiegelung bleibt Benutzeraufgabe.

## 10. Abnahmeprotokoll: kein grüner Sammelstatus ohne Belege

Für jeden Punkt `bestanden / fehlgeschlagen / nicht ausgeführt / blockiert` und konkrete lokale Belegdatei notieren:

| Prüfung | Erforderlicher Nachweis |
|---|---|
| Quellen/Versionen | Tatsächliche Registry-Digests, Plattform, Katalog-/Client-Version, geprüfte Herkunft |
| Bindings/Auth | API und DB nur Loopback; keine zusätzlichen Listener; Bankdaten ohne Token verweigert |
| Lokale DB | Effektive DSN ohne Secretausgabe, konkrete Compose-Port-/Volumezuordnung, System-ID, Migration, Testbank in dieser DB |
| Modellpfade | Drei gelieferte Protokolle/IDs, Dimension/Modellparameter, echte kleine Requests, keine abweichenden Rollen/Fallbacks |
| Retain | Tatsächliche Extraktion, alle Operationen terminal erfolgreich, Fakten fachlich korrekt |
| Konsolidierung | Beobachtungen mit Quellen, erfolgreiche Operation, keine offenen/fehlgeschlagenen Konsolidierungen |
| Recall/Reflect | Inhaltlich richtiger deutscher Fall einschließlich Negation; nicht bloß nichtleer |
| Persistenz | Gleiche Daten/Volume/System-ID nach genehmigtem Dienstneustart |
| Hermes | Frische Sitzungen, effektive Testbank, drei Tools, expliziter und automatischer Speicher-/Abrufpfad separat |
| Finale Bank | Eigene neue Bank, endgültige Zielbindung in frischer Sitzung, keine Testdaten übernommen |
| Backup/Restore | Eigener nachgelagerter Schritt; Dump und isolierter Restore separat belegt, sonst ausdrücklich offen |

**Prüfgrenze dieses Autors:** Quellenvergleich, Python-AST, `bash -n`, JSON-Parsing, YAML-Parsing mit `ruamel.yaml`, relative Dateilinks und Abgleich der Compose-ENV-Schlüssel/Prüfpayloads gegen den gewählten Quell-/OpenAPI-Stand wurden statisch geprüft. Das sind keine Ausführung des Makers, kein `docker compose config` und keine Laufzeitprüfung. Alle Laufzeit-Abnahmepunkte dieser Tabelle bleiben bis zur späteren Kollegen-Einrichtung offen.

## 11. Offizielle Quellen und genaue Nachprüfstellen

Diese Dokumentation und Vorlagen sind neu geschrieben (MIT), keine Kopie persönlicher Skills oder Infrastrukturkonfiguration. Upstream-Quellen bleiben unter ihrer jeweiligen Lizenz. Links auf bewegliche Dokumentation ersetzen keinen zum ausgewählten Image passenden Quellstand.

- [Hermes Memory Providers](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory-providers): Kataloginstallation, exklusiver Provider, zusätzliches Built-in Memory.
- [Offizielle Hindsight-Hermes-Integration](https://hindsight.vectorize.io/sdks/integrations/hermes): `local_external`, Konfigurationssuche, Geheimnisfallback, Tools und Provideraktivierung.
- [Hermes-Katalogeintrag](https://github.com/NousResearch/hermes-agent/blob/main/plugin-catalog/hindsight.yaml): bei Installation aktuell auflösen.
- [Geprüfter Plugin-Pin](https://github.com/vectorize-io/hindsight/tree/d952b6e655fccab4581ee0722b51c5f103873d12/hindsight-integrations/hermes): `__init__.py` (JSON/ENV-Bankvorrang, Recalltypen/Tools), `pyproject.toml` (Abhängigkeiten).
- [Hindsight Konfiguration](https://hindsight.vectorize.io/developer/configuration): öffentliche aktuelle Referenz; Server/DB, Per-operation LLM, Embeddings, Reranking, Auth, Observations und Worker.
- [Release v1.0.0](https://github.com/vectorize-io/hindsight/releases/tag/v1.0.0), [Release-Workflow](https://github.com/vectorize-io/hindsight/blob/39c65ffe2f140d0c84cee58566cad8900c5b9908/.github/workflows/release.yml): API-slim-Imagequelle, Tagbildung, Plattformen/Signaturweg.
- [Dockerfile](https://github.com/vectorize-io/hindsight/blob/39c65ffe2f140d0c84cee58566cad8900c5b9908/docker/standalone/Dockerfile): API-only, CLI im PATH, unprivilegierter Benutzer, Ausschluss lokaler ML-Pakete bei slim.
- [CLI](https://github.com/vectorize-io/hindsight/blob/39c65ffe2f140d0c84cee58566cad8900c5b9908/hindsight-api-slim/hindsight_api/main.py): `--host`, `--port`, `--workers`, `--no-access-log` und `uvicorn.run`.
- [Server-Konfigurationsschlüssel](https://github.com/vectorize-io/hindsight/blob/39c65ffe2f140d0c84cee58566cad8900c5b9908/hindsight-api-slim/hindsight_api/config.py): alle im Compose-File verwendeten `HINDSIGHT_API_*`-Schlüssel, Rollen-Fallbacks, Worker/Auto-Konsolidierung.
- [API-Key-Tenant](https://github.com/vectorize-io/hindsight/blob/39c65ffe2f140d0c84cee58566cad8900c5b9908/hindsight-api-slim/hindsight_api/extensions/builtin/tenant.py): `TENANT_EXTENSION`, `TENANT_API_KEY`, Ablehnung ohne passenden Key.
- [TEI-Embeddings](https://github.com/vectorize-io/hindsight/blob/39c65ffe2f140d0c84cee58566cad8900c5b9908/hindsight-api-slim/hindsight_api/engine/embeddings.py), [TEI-Reranker](https://github.com/vectorize-io/hindsight/blob/39c65ffe2f140d0c84cee58566cad8900c5b9908/hindsight-api-slim/hindsight_api/engine/cross_encoder.py): `RemoteTEIEmbeddings`/`RemoteTEICrossEncoder`, `/info`, `/embed`, `/rerank`, Dimensionserkennung, keine TEI-Key-Parameter.
- [OpenAPI des ausgewählten Releases](https://github.com/vectorize-io/hindsight/blob/39c65ffe2f140d0c84cee58566cad8900c5b9908/hindsight-docs/static/openapi.json): Bank-Upsert und paginierte Liste, Retain/Recall/Reflect, `/consolidate`, bankqualifizierte `/operations/{operation_id}`, Stats und Memory-Listen. Später gegen die gestartete eigene `/openapi.json` abgleichen.
- [Migrationen](https://github.com/vectorize-io/hindsight/tree/39c65ffe2f140d0c84cee58566cad8900c5b9908/hindsight-api-slim/hindsight_api/alembic/versions): initiale pgvector-Tabelle; `pg_trgm` und `btree_gin` in Folgemigrationen.
- [External-PG-Beispiel](https://github.com/vectorize-io/hindsight/blob/39c65ffe2f140d0c84cee58566cad8900c5b9908/docker/docker-compose/external-pg/docker-compose.yaml), [pgvector Docker/Tags](https://github.com/pgvector/pgvector#docker), [offizielles Postgres-Image](https://hub.docker.com/_/postgres): unterstützte Imagefamilie und PG18-Mount-/Init-Verhalten. Deren offene Beispielports/`latest` werden hier bewusst nicht übernommen.
- [Docker Host Networking](https://docs.docker.com/engine/network/drivers/host/), [Port Publishing](https://docs.docker.com/engine/network/port-publishing/): geteilter Namespace, keine Portmapping-Isolation, Loopback-Publishing-Grenzen.
