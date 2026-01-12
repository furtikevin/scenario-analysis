from dotenv import load_dotenv
load_dotenv()

from scenario_analysis.ingestion.openscenario_xml import OpenScenarioXMLParser
from scenario_analysis.features.basic_stats import BasicStatsExtractor
from scenario_analysis.features.semantic_ai import AISemanticFeatureExtractor
from scenario_analysis.features.feature_vector import FeatureVectorBuilder
from scenario_analysis.llm.openai_client import OpenAIClient


def main():
    parser = OpenScenarioXMLParser()
    scenario = parser.parse(
        "data/raw/openscenario/xml/CloseVehicleCrossing.xosc"
    )

    print("=== SCENARIO INFO ===")
    print("Name:", scenario.name)
    print("Author:", scenario.author)
    print("Date:", scenario.date)

    print("\n=== FEATURE VECTOR ===")

    builder = FeatureVectorBuilder(
        structural_extractor=BasicStatsExtractor(),
        semantic_extractor=AISemanticFeatureExtractor(OpenAIClient()),
    )

    feature_vector = builder.build(scenario)

    for k, v in feature_vector.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
