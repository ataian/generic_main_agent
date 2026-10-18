# Herkunft und Lizenz

Eigenständige portable Neufassung für das Projekt `generic-main-agent`, erstellt von Max; Hermes Agent, unter [MIT](../LICENSE). Die bestätigten Anforderungen verlangen den 02:00-Vortagslauf, Zielinstanz-Isolation, ehrliche Leertage und idempotente Notizpflege.

Der vorhandene interne Skill `obsidian-daily-summary` wurde als fachliche Referenz geprüft, nicht kopiert. Seine profilsammelnde Shellhilfe, Filterung nach Sitzungsbeginn, festen Pfade und historischen Behauptungen über Toollimits wurden ausdrücklich nicht übernommen. Der hier enthaltene Python-Helper wurde neu geschrieben und benutzt ausschließlich die Standardbibliothek. Er enthält keinen übernommenen Hermes-Implementierungscode.

Technische Fakten zum SQLite-Schema und zu Unixsekunden stammen aus lesend geprüften Hermes-Quelldateien. Quellstand, Dateinamen und native Schnittstelle sind im [Helper-Vertrag](helper-und-pruefung.md) dokumentiert. Das ist eine statische Quellprüfung, kein produktiver Datenbanktest. Projektquelle: <https://github.com/NousResearch/hermes-agent>; aktuelle offizielle Dokumentation: <https://hermes-agent.nousresearch.com/docs>.

Interne Originalanhänge, private Pfade, Gesprächsinhalte und Profile werden nicht mitgeliefert. Die MIT-Erklärung gilt für die neuen Paketdateien, nicht pauschal für interne Originalmaterialien. Veröffentlichung und Live-Installation bleiben gesonderte Schritte.
