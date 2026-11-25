# Enterprise Incident Intelligence Assistant

A Python-based incident retrieval prototype that identifies historically similar IT incidents using TF-IDF vectorization and cosine similarity.

The application returns ranked historical incidents, their categories, relevance scores, and resolution guidance. It is designed as a foundation for future evaluation, semantic retrieval, and LLM/RAG extensions.

## Features

- Load and validate historical incidents from CSV.
- Convert incident descriptions into TF-IDF vectors.
- Rank similar incidents using cosine similarity.
- Return configurable top-k results.
- Suggest a category and historical resolution guidance.
- Provide structured JSON output through a command-line interface.
- Run automated tests with pytest.
- Run CI tests through GitHub Actions.

## Architecture

```text
User query
    |
    v
Command-line interface
    |
    v
Incident Retriever
    |
    +--> TF-IDF vectorization
    |
    +--> Cosine similarity
    |
    +--> Ranked historical incidents
    |
    v
Structured JSON response
```

## Project structure

```text
enterprise-incident-intelligence-assistant/
├── .github/
│   └── workflows/
│       └── tests.yml
├── data/
│   ├── incidents.csv
│   └── evaluation_cases.csv
├── docs/
│   └── MLOPS_ROADMAP.md
├── incident_intelligence/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   └── retriever.py
├── tests/
│   └── test_retriever.py
├── .gitignore
├── LICENSE
├── pyproject.toml
├── README.md
└── requirements.txt
```

## Requirements

- Python 3.10 or later
- pip

## Setup

Create and activate a virtual environment.

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the project and development dependencies:

```powershell
python -m pip install -e ".[dev]"
```

## Run the application

From the project root:

```powershell
python -m incident_intelligence "Users are unable to login because authentication is timing out"
```

Retrieve a different number of results:

```powershell
python -m incident_intelligence "Database connection pool exhausted" --top-k 5
```

The application prints a JSON response containing:

- Incident category
- Similar historical incidents
- Similarity scores
- Resolution guidance
- Relevance score
- Heuristic confidence label

## Run automated tests

```powershell
python -m pytest -v
```

The GitHub Actions workflow runs the test suite on pushes and pull requests for Python 3.10, 3.11, and 3.12.

## Evaluation dataset

`data/evaluation_cases.csv` contains example queries and expected incident identifiers and categories. These cases are used by the automated tests as a small retrieval evaluation set.

This is a small prototype dataset, not a production benchmark.

## Important limitations

- TF-IDF is lexical retrieval; it does not understand meaning in the same way as semantic embeddings.
- Similarity scores are not probabilities.
- Confidence labels are heuristic thresholds, not calibrated confidence estimates.
- Results depend on the quality and coverage of historical incident records.
- Suggested resolutions must be reviewed by an appropriate human before operational use.
- The current application does not use an LLM, vector database, or cloud deployment.

## MLOps roadmap

See [docs/MLOPS_ROADMAP.md](docs/MLOPS_ROADMAP.md) for proposed evaluation, monitoring, semantic retrieval, LLM/RAG, and Azure deployment extensions.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
