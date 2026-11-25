import argparse
import json
from pathlib import Path

from incident_intelligence.retriever import IncidentRetriever


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Enterprise Incident Intelligence Assistant"
    )
    parser.add_argument(
        "query",
        help="Describe the incident you want to investigate.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Number of similar incidents to retrieve (default: 3).",
    )

    args = parser.parse_args()

    dataset_path = Path(__file__).resolve().parent.parent / "data" / "incidents.csv"
    retriever = IncidentRetriever(dataset_path)

    result = retriever.search(args.query, top_k=args.top_k)
    print(json.dumps(result, indent=4))


if __name__ == "__main__":
    main()
