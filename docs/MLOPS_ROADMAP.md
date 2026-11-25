# MLOps Roadmap

## Project status

This repository currently implements a local Python incident retrieval prototype
using TF-IDF vectorization and cosine similarity.

GitHub Actions automated testing is configured in this repository.
The capabilities below are proposed extensions, not completed features.

## Current implementation

- Historical incident records stored in CSV.
- Dataset validation during loading.
- TF-IDF feature extraction.
- Cosine similarity ranking.
- Configurable top-k retrieval and similarity threshold.
- Structured resolution guidance.
- Command-line interface.
- Automated tests using pytest.
- GitHub Actions CI workflow.

## Proposed improvements

### 1. Evaluation and data quality

- Expand the evaluation dataset with representative incident queries.
- Track Precision@K, Recall@K, Mean Reciprocal Rank (MRR), and category accuracy.
- Review incorrect matches and low-relevance results.
- Version evaluation datasets and document changes.
- Remove sensitive information from incident records before use.

### 2. Retrieval improvements

- Compare TF-IDF retrieval with semantic embeddings.
- Evaluate hybrid lexical and semantic retrieval.
- Introduce a governed knowledge base for approved resolutions.
- Require human review before applying suggested remediation.

### 3. LLM and RAG extension

- Add an LLM only after retrieval quality has been evaluated.
- Ground generated answers in retrieved incident records.
- Include source incident identifiers in responses.
- Evaluate hallucination risk and answer relevance.
- Keep human approval for operational changes.

### 4. Azure deployment proposal

A possible future architecture:

- Azure Container Registry for container images.
- Azure Container Apps or Azure App Service for deployment.
- Azure Key Vault for secrets.
- Managed Identity for service authentication.
- Azure Monitor and Application Insights for telemetry.

No Azure deployment is currently implemented.

### 5. Monitoring and governance

Future monitoring should include:

- Retrieval relevance and ranking quality.
- Query volume and response latency.
- No-match rate and low-confidence rate.
- Dataset freshness and data quality.
- Model and dependency versions.
- Access controls, privacy, and auditability.

## Delivery approach

1. Establish a reliable offline evaluation baseline.
2. Improve retrieval using measured results.
3. Add semantic or hybrid retrieval if justified.
4. Introduce LLM-based generation with source grounding.
5. Containerize and deploy after security and evaluation checks.
6. Monitor production quality and periodically review the dataset.
