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



def main():
    parser = OpenScenarioXMLParser()
    scenario = parser.parse(
        "data/raw/openscenario/xml/SequentialEvents_0-100-0kph_Explicit.xosc"
    )
    

    print("=== SCENARIO INFO ===")
    print("Name:", scenario.name)
    print("Author:", scenario.author)
    print("Date:", scenario.date)

    print("\n=== FEATURE VECTOR ===")

    builder = FeatureVectorBuilder(
    structural_extractor=BasicStatsExtractor(),
    semantic_extractor=AISemanticFeatureExtractor(OpenAIClient()),
    road_graph_extractor=RoadGraphExtractor(),
    road_graph_feature_extractor=RoadGraphFeatureExtractor(),
    xodr_path="data/raw/openscenario/xodr/AB_RQ31_Straight.xodr"
    )

    

    feature_vector = builder.build(scenario)

    for k, v in feature_vector.items():
        print(f"{k}: {v}")

    writer = JSONFeatureWriter(
    output_dir="data/processed/feature_vectors"
    )

    output_path = writer.write(
        feature_vector=feature_vector,
        scenario_name=scenario.name,
        source="esmini"
    )

    print(f"\nFeature vector saved to: {output_path}")

if __name__ == "__main__":
    main()
