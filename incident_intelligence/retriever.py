import csv
from collections import defaultdict
from pathlib import Path
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


REQUIRED_COLUMNS = {
    "incident_id",
    "title",
    "description",
    "category",
    "symptoms",
    "resolution",
}


def load_incidents(csv_path: str | Path) -> list[dict[str, str]]:
    """Load and validate historical incidents from a CSV file."""
    path = Path(csv_path)

    if not path.is_file():
        raise FileNotFoundError(f"Incident dataset not found: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError("Incident dataset is empty or has no header.")

        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")

        incidents = []
        seen_ids = set()

        for row_number, row in enumerate(reader, start=2):
            incident = {
                column: (row.get(column) or "").strip()
                for column in REQUIRED_COLUMNS
            }

            if not all(incident.values()):
                raise ValueError(
                    f"Missing required value in CSV row {row_number}."
                )

            if incident["incident_id"] in seen_ids:
                raise ValueError(
                    f"Duplicate incident ID: {incident['incident_id']}"
                )

            seen_ids.add(incident["incident_id"])
            incidents.append(incident)

    if not incidents:
        raise ValueError("Incident dataset contains no incident records.")

    return incidents


class IncidentRetriever:
    """Retrieve historically similar incidents using TF-IDF and cosine similarity."""

    def __init__(
        self,
        csv_path: str | Path,
        similarity_threshold: float = 0.15,
    ) -> None:
        if not 0.0 <= similarity_threshold <= 1.0:
            raise ValueError("similarity_threshold must be between 0 and 1.")

        self.incidents = load_incidents(csv_path)
        self.similarity_threshold = similarity_threshold

        documents = [
            " ".join(
                [
                    incident["title"],
                    incident["description"],
                    incident["symptoms"],
                    incident["category"],
                ]
            )
            for incident in self.incidents
        ]

        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
            sublinear_tf=True,
        )

        self.incident_matrix = self.vectorizer.fit_transform(documents)

    def search(self, query: str, top_k: int = 3) -> dict[str, Any]:
        """Find similar incidents and return structured resolution guidance."""
        if not isinstance(query, str) or not query.strip():
            raise ValueError("Query must be a non-empty string.")

        if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k < 1:
            raise ValueError("top_k must be a positive integer.")

        query_vector = self.vectorizer.transform([query.strip()])
        scores = cosine_similarity(query_vector, self.incident_matrix)[0]

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda index: (
                -float(scores[index]),
                self.incidents[index]["incident_id"],
            ),
        )

        matches = [
            {
                **self.incidents[index],
                "similarity_score": round(float(scores[index]), 4),
            }
            for index in ranked_indices
            if scores[index] >= self.similarity_threshold
        ][:top_k]

        if not matches:
            return {
                "query": query.strip(),
                "incident_category": "Unknown",
                "similar_incidents": [],
                "resolution_guidance": [
                    "No sufficiently similar historical incident found. "
                    "Investigate manually and document the outcome."
                ],
                "relevance_score": 0.0,
                "confidence": "low",
            }

        category_scores: dict[str, float] = defaultdict(float)
        for match in matches:
            category_scores[match["category"]] += match["similarity_score"]

        predicted_category = sorted(
            category_scores.items(),
            key=lambda item: (-item[1], item[0]),
        )[0][0]

        guidance = list(
            dict.fromkeys(match["resolution"] for match in matches)
        )

        top_score = matches[0]["similarity_score"]

        return {
            "query": query.strip(),
            "incident_category": predicted_category,
            "similar_incidents": [
                {
                    "incident_id": match["incident_id"],
                    "title": match["title"],
                    "category": match["category"],
                    "similarity_score": match["similarity_score"],
                    "resolution": match["resolution"],
                }
                for match in matches
            ],
            "resolution_guidance": guidance,
            "relevance_score": top_score,
            "confidence": (
                "high" if top_score >= 0.5
                else "medium" if top_score >= 0.2
                else "low"
            ),
        }
