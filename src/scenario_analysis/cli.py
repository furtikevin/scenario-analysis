import argparse
import logging
import sys
from dotenv import load_dotenv

load_dotenv()

from scenario_analysis.ingestion.openscenario_xml import OpenScenarioXMLParser
from scenario_analysis.features.basic_stats import BasicStatsExtractor
from scenario_analysis.features.semantic_ai import AISemanticFeatureExtractor
from scenario_analysis.features.feature_vector import FeatureVectorBuilder
from scenario_analysis.llm.openai_client import OpenAIClient
from scenario_analysis.analysis.road_graph import RoadGraphExtractor
from scenario_analysis.features.road_graph_features import RoadGraphFeatureExtractor
from scenario_analysis.output.json_writer import JSONFeatureWriter

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def get_parser():
    parser = argparse.ArgumentParser(description="Scenario Analysis CLI")
    parser.add_argument("--xosc", required=True, help="Pfad zur OpenScenario (.xosc) XML Datei")
    parser.add_argument("--xodr", required=True, help="Pfad zur OpenDrive (.xodr) Datei")
    parser.add_argument("--outdir", default="data/processed/feature_vectors", help="Ausgabeverzeichnis für die JSON")
    return parser

def main():
    args = get_parser().parse_args()

    try:
        logging.info(f"Parsen von Szenario: {args.xosc}")
        parser = OpenScenarioXMLParser()
        scenario = parser.parse(args.xosc)
        
        logging.info(f"Szenario Info - Name: {scenario.name}, Author: {scenario.author}, Date: {scenario.date}")

        logging.info("Erstelle Feature Vector...")
        builder = FeatureVectorBuilder(
            structural_extractor=BasicStatsExtractor(),
            semantic_extractor=AISemanticFeatureExtractor(OpenAIClient()),
            road_graph_extractor=RoadGraphExtractor(),
            road_graph_feature_extractor=RoadGraphFeatureExtractor(),
            xodr_path=args.xodr
        )

        feature_vector = builder.build(scenario)

        for k, v in feature_vector.items():
            logging.info(f"Feature '{k}': {v}")

        writer = JSONFeatureWriter(output_dir=args.outdir)
        output_path = writer.write(
            feature_vector=feature_vector,
            scenario_name=scenario.name,
            source="esmini"
        )

        logging.info(f"Feature vector erfolgreich gespeichert unter: {output_path}")

    except Exception as e:
        logging.error(f"Fehler bei der Ausführung: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
