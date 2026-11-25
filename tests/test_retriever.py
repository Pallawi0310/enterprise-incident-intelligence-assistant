import pytest
from pathlib import Path

from incident_intelligence.retriever import (
    IncidentRetriever,
    load_incidents,
)


DATASET = Path(__file__).resolve().parents[1] / "data" / "incidents.csv"


@pytest.fixture
def retriever():
    return IncidentRetriever(DATASET)


def test_dataset_loads_12_incidents():
    incidents = load_incidents(DATASET)
    assert len(incidents) == 12


def test_login_query_retrieves_correct_incident(retriever):
    result = retriever.search(
        "Users cannot login because authentication is timing out"
    )

    assert result["incident_category"] == "Authentication"
    assert result["similar_incidents"][0]["incident_id"] == "INC-001"


def test_database_query_retrieves_database_incident(retriever):
    result = retriever.search(
        "Database connection pool exhausted and application cannot connect"
    )

    assert result["incident_category"] == "Database"
    assert result["similar_incidents"][0]["incident_id"] == "INC-003"


def test_results_are_sorted_by_similarity(retriever):
    result = retriever.search("VPN connection failure", top_k=3)
    scores = [
        item["similarity_score"]
        for item in result["similar_incidents"]
    ]

    assert scores == sorted(scores, reverse=True)


def test_top_k_limits_results(retriever):
    result = retriever.search("login authentication failure", top_k=2)
    assert len(result["similar_incidents"]) <= 2


def test_empty_query_is_rejected(retriever):
    with pytest.raises(ValueError):
        retriever.search("")


@pytest.mark.parametrize("invalid_top_k", [0, -1, 1.5, True, False, "3"])
def test_invalid_top_k_is_rejected(retriever, invalid_top_k):
    with pytest.raises(ValueError):
        retriever.search("login failure", top_k=invalid_top_k)


def test_unrelated_query_returns_no_match():
    strict_retriever = IncidentRetriever(
        DATASET,
        similarity_threshold=0.99,
    )

    result = strict_retriever.search("quantum spacecraft propulsion")

    assert result["incident_category"] == "Unknown"
    assert result["similar_incidents"] == []
    assert result["relevance_score"] == 0.0


def test_missing_dataset_is_rejected(tmp_path):
    missing_file = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError):
        IncidentRetriever(missing_file)


def test_invalid_similarity_threshold_is_rejected():
    with pytest.raises(ValueError):
        IncidentRetriever(DATASET, similarity_threshold=1.5)


def test_dataset_missing_required_column_is_rejected(tmp_path):
    csv_file = tmp_path / "missing_column.csv"
    csv_file.write_text(
        "incident_id,title,description,category,symptoms\n"
        "INC-100,Test,Description,Test,Symptom\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Missing required columns"):
        load_incidents(csv_file)


def test_empty_dataset_is_rejected(tmp_path):
    csv_file = tmp_path / "empty.csv"
    csv_file.write_text(
        "incident_id,title,description,category,symptoms,resolution\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="no incident records"):
        load_incidents(csv_file)


def test_duplicate_incident_ids_are_rejected(tmp_path):
    csv_file = tmp_path / "duplicates.csv"
    csv_file.write_text(
        "incident_id,title,description,category,symptoms,resolution\n"
        "INC-100,First,Description,Test,Symptom,Resolution\n"
        "INC-100,Second,Description,Test,Symptom,Resolution\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Duplicate incident ID"):
        load_incidents(csv_file)


def test_missing_required_value_is_rejected(tmp_path):
    csv_file = tmp_path / "missing_value.csv"
    csv_file.write_text(
        "incident_id,title,description,category,symptoms,resolution\n"
        "INC-100,Test,Description,Test,,Resolution\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Missing required value"):
        load_incidents(csv_file)


def test_evaluation_cases_retrieve_expected_incidents(retriever):
    import csv

    evaluation_file = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "evaluation_cases.csv"
    )

    with evaluation_file.open("r", encoding="utf-8-sig", newline="") as file:
        cases = list(csv.DictReader(file))

    assert cases, "Evaluation dataset must contain test cases."

    for case in cases:
        result = retriever.search(case["query"], top_k=3)

        assert result["similar_incidents"], case["query"]
        assert (
            result["similar_incidents"][0]["incident_id"]
            == case["expected_incident_id"]
        ), case["query"]
        assert result["incident_category"] == case["expected_category"]
