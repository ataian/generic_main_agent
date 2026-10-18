# Voraussetzungen und Anschlussdaten

## Auf der Zielmaschine

- Linux mit normalem Benutzerkonto, laufendem Hermes und eingerichtetem Modell.
- Python 3.11 oder neuer für die mitgelieferten Helfer; Git; Docker Engine und Compose-Plugin für den Benutzer nutzbar.
- Ein Benutzer-Service-Manager für den nativen Hermes-Gateway-Dauerbetrieb. Bei abweichender Linux-Umgebung vor Änderungen den unterstützten Hermes-Weg klären.
- Ausreichend freier Speicher für Datenbanken, Vault und 30 Tage lokale Sicherungen. Bedarf bei der Einrichtung abschätzen; keine pauschale Größe versprechen.
- Docker-Rechte sind weitreichend und keine Sicherheitsgrenze gegenüber dem Host. Der Maker gibt keine Rechte pauschal neu frei.

## Vom Betreiber bereits bereitgestellt

| Anschluss | Benötigte Angaben |
|---|---|
| Hauptmodell | Bereits in Hermes eingerichtet |
| Hindsight-LLM | Erreichbare OpenAI-kompatible Base-URL, genaue Modell-ID, nötige Authentifizierung, Kontextlimit und strukturierte Ausgabe |
| Embeddings | Bereits bereitgestellter HTTP-Loopback-Zugang mit TEI `/info` und `/embed`, Modell-ID, Dimension und Präfix-/Tokenlimits; im gelieferten Rezept ohne zusätzliche HTTP-Authentifizierung |
| Reranking | Bereits bereitgestellter HTTP-Loopback-Zugang mit TEI `/info` und `/rerank`, Modell-ID und Tokenlimits; im gelieferten Rezept ohne zusätzliche HTTP-Authentifizierung |
| Firecrawl-Router | Vom Betreiber genannter erreichbarer Endpoint, gegebenenfalls vorhandener lokaler Zugang |

Tatsächliche Werte aus der Bereitstellung verwenden. Keine Modellnamen, Ports, Hostnamen oder Schlüssel raten. Zentrale Server und Tunnel werden nicht durch den Maker eingerichtet.

Das konkrete [Hindsight-Rezept](../skills/generic-main-agent-maker/references/hindsight.md) verwendet vorhandene `http://127.0.0.1:PORT`-Zugänge; LLM mit `/v1`. Abweichende Protokolle oder zusätzliche TEI-Authentifizierung sind ein Hindsight-Blocker, kein Auftrag, Authentifizierung abzuschalten oder neue Tunnel/Proxys aufzubauen. Die übrigen Einrichtungsschritte können weitergehen.

## Persönliche Angaben

- Name des Benutzers, gewünschter Agentenname.
- Gewählter Nachrichtenkanal: native Hermes-Einrichtung durch den Benutzer.
- Eigener Firecrawl-API-Key: nur lokal in die geschützte `.env`; danach SHA-256-Fingerprint an Max übermitteln.
- Bestehender Vault nur falls vorhanden. Sonst Default `~/obsidian_vault` nach Bestandsprüfung.

## Datenwege

- Hindsight-Banken: lokale PostgreSQL, getrennt von anderen Instanzen.
- Hindsight-Inferenz: Inhalte werden an die bereitgestellten Modell-APIs übertragen.
- Websuche/Extraktion: Anfragen gehen an den Router; erlaubter Cloud-Fallback kann dein Firecrawl-Kontingent belasten.
- Nachrichten und Hauptmodell: Datenschutz richtet sich zusätzlich nach dem gewählten Anbieter.
- Backups: zunächst lokal. Zugangsdaten separat mit engen Dateirechten; das allein ist keine Verschlüsselung.
