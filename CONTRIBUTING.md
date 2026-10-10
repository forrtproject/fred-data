# Contributing to fred-data

**Use [flora-validation](https://github.com/forrtproject/flora-validation) for new FLoRA ingestion and validation work.** Most of that work here is superseded and partially redundant. Please follow the [FORRT Code of Conduct](https://forrt.org/coc/).

This repository retains effect-level FReD processing, shared R helpers, historical FLoRA pipelines, and compatibility/release tooling. Before changing these, open an [issue](https://github.com/forrtproject/fred-data/issues) explaining the problem, affected consumers, and why the change belongs here. Documentation corrections and reproducible reports are welcome. Check existing issues and PRs to avoid duplicating work.

For a data issue, include a public DOI or record identifier, the expected and actual result, and supporting evidence. Keep private source sheets, identifiers, API keys, and unpublished data out of issues and fixtures.

For an agreed change, fork the repository, branch from current `main`, keep the PR focused, and target `main`. Read the relevant pipeline and helpers rather than assuming all instructions in the historical README remain a current deployment recommendation. Preserve effect-level FReD identities and relationships, Unicode, manual overrides, and existing output contracts. R CSV exports should use `write_excel_csv()` where Excel needs a UTF-8 BOM, in line with the repository's [.claude/claude.md](.claude/claude.md) guidance.

Use small synthetic or public fixtures to check changed transformations and describe the results in the PR. Pipeline rendering can download source data, call external services, and rewrite outputs or caches; it is not a routine offline test. Agree any full pipeline, production loader, OSF release, or paid-service run with maintainers first. Do not commit credentials, private data, generated outputs, or unrelated cache changes.

Link the agreed issue, explain the resulting behaviour, list the checks performed and their limitations, and identify any compatibility or migration work. Maintainers review before merging and handle publication and production operations.
