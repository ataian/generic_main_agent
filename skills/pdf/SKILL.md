---
name: pdf
description: "Lies, erstelle und bearbeite lokale PDF-Dateien."
version: 0.1.0
author: Max; Hermes Agent
license: MIT
platforms: [linux]
---

# Lokale PDF-Grundaufgaben

## Wann
Text/Metadaten lesen, PDFs erzeugen, Seiten zusammenführen/trennen oder Formularfelder prüfen. Keine Office-/Präsentationssuite, kein automatisches OCR-Modellsetup.

## Voraussetzung
Eigenes venv für Agentenwerkzeuge, nicht Hermes' verwaltete Umgebung. Der Maker bereitet `pypdf`, `reportlab`, `pdfplumber` aus überprüften Quellen vor und hält Interpreterpfad/Versionen im lokalen `maker/environment.json` sowie Einrichtungsbericht fest. Passende vorhandene Umgebung wiederverwenden. Bei fehlenden Paketen gelten `fremde-installer-pruefen` und Freigabegrenzen.

Spätere Einrichtung: `python3 -m venv` im genehmigten Arbeitsbereich, konkret geprüfte Paketversionen über dessen Interpreter installieren, `pip freeze` lokal sichern. Keine fremden Shellinstaller, keine globale `pip install`. Venv ist keine Sicherheits-Sandbox.

## Ablauf
1. Inputpfad, Berechtigung und Output bestimmen. Original erhalten, neue Datei im Projektbereich.
2. Zuerst natives `read_file` zur Textansicht. Gezielte Prüfung im dokumentierten PDF-Interpreter:

```python
from pypdf import PdfReader
reader = PdfReader(input_path)
print(len(reader.pages))
for number, page in enumerate(reader.pages, 1):
    print(number, page.extract_text() or "[keine Textschicht erkannt]")
```

3. Zusammenführen in neue Datei:

```python
from pypdf import PdfWriter
writer = PdfWriter()
for source in input_paths:
    writer.append(source)
with open(output_path, "xb") as target:
    writer.write(target)
```

4. Tabellen mit `pdfplumber` extrahieren; Zeilen/Spalten kontrollieren. Neue PDFs mit `reportlab.platypus`, explizitem Seitenformat und passenden Fonts.
5. Verschlüsselte PDFs nur mit berechtigtem Zugang; Passwörter nicht in Argumenten, Code oder Logs. Leerer Text kann Scan bedeuten, nichts erfinden. OCR separat anbieten, nicht ungefragt herunterladen.
6. Ergebnis erneut öffnen, Seitenzahl und Stichproben vergleichen. Bei Layout vorhandenen Renderer nutzen und Seiten tatsächlich visuell prüfen. Ohne Renderer nur Struktur-/Textprüfung behaupten.

## Einrichtungstest
Mit PDF-Interpreter kleines Dokument mit `reportlab` erzeugen, mit `pypdf` öffnen und bekannten Text sowie Seitenzahl prüfen. Nur eigene Testdatei. Test der späteren Zielinstallation, nicht dieses Repositorys.

## Grenzen und Quellen
Keine PDF/A- oder Barrierefreiheitskonformität behaupten. Formularanzeige kann vom Textwert abweichen; Rendering prüfen. Signierte Dokumente nicht unbemerkt verändern. Original nicht durch fehlgeschlagenen Export überschreiben.

- https://pypdf.readthedocs.io/
- https://www.reportlab.com/docs/reportlab-userguide.pdf
- https://github.com/jsvine/pdfplumber
