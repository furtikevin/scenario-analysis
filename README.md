# Scenario Analysis Pipeline

Dieses Repository enthält den Code zu meiner Bachelorarbeit. Das Tool analysiert automatisiert OpenSCENARIO- und OpenDRIVE-Dateien, liest Merkmale wie Kreuzungen, Entitäten und Geschwindigkeiten aus und nutzt dann ein KI-Modell, um das Gefahrenpotenzial des Szenarios zu bewerten.

## Was Sie benötigen

Sie brauchen auf Ihrem System nur eine aktuelle Python-Version (3.8 oder neuer).

## Installation

1. **Python-Pakete installieren:**
   Öffnen Sie Ihr Terminal und installieren Sie die beiden benötigten Bibliotheken:
   ```bash
   pip install lxml openai
   ```

2. **OpenAI API-Key hinterlegen:**
   Damit die semantische Analyse durch das Sprachmodell funktioniert, wird ein API-Key von OpenAI benötigt. Erstellen Sie einfach eine Datei namens `.env` direkt hier im Hauptordner (`scenario-analysis`) und tragen Sie Ihren Key so ein:
   ```env
   OPENAI_API_KEY=sk-IhrKeyHier
   ```
   Denn Key kann ich ihnen auch gerne in einem Meeting oder in einer verschlüsselten Nachricht geben.

## Testlauf

Das Kernstück ist das Command-Line-Skript `cli.py`. Sie müssen dem Skript beim Start nur mitgeben, wo das gewünschte Szenario (`.xosc`) und wo die zugehörige Straßenkarte (`.xodr`) liegt.

Öffnen Sie ein Terminal im Ordner `scenario-analysis`. Setzen Sie den `PYTHONPATH` auf das `src`-Verzeichnis und starten Sie das Skript. Hier ist ein Beispiel für eines der Test-Szenarien:

**Unter Windows (z.B. in der PowerShell):**
```powershell
$env:PYTHONPATH="src"
python src/scenario_analysis/cli.py --xosc data/raw/openscenario/xml/CloseVehicleCrossing.xosc --xodr data/raw/openscenario/xodr/fabriksgatan.xodr
```

**Unter Linux oder macOS:**
```bash
PYTHONPATH=src python3 src/scenario_analysis/cli.py --xosc data/raw/openscenario/xml/CloseVehicleCrossing.xosc --xodr data/raw/openscenario/xodr/fabriksgatan.xodr
```

## Ergebnisse

Sobald das Skript durchgelaufen ist, fasst es alle extrahierten Daten, die berechnete Unfallwahrscheinlichkeit und die textliche Begründung der KI übersichtlich in einer neuen JSON-Datei zusammen. 
Diese Output-Dateien finden Sie dann sofort im Ordner `data/processed/feature_vectors/`.


