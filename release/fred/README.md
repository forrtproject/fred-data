# FReD releases on Zenodo

FReD has its own Zenodo concept record, [10.5281/zenodo.24461606](https://doi.org/10.5281/zenodo.24461606),
separate from FLoRA's ([10.5281/zenodo.24461022](https://doi.org/10.5281/zenodo.24461022)).
Versions use CalVer `YYYY.MM.N`, like FLoRA, and are defined in `versions.yml`:

| Version | Contents | Published | Record |
| --- | --- | --- | --- |
| 2025.11.1 | SMART competition delivery of 30 November 2025 (phase 1), 2,164 effects | 2026-11-23 | [10.5281/zenodo.24461607](https://doi.org/10.5281/zenodo.24461607) |
| 2026.11.1 | Pipeline build with SCORE effects and statistics-audit corrections (phase 2), 2,175 effects | 2026-11-23 | [10.5281/zenodo.24462293](https://doi.org/10.5281/zenodo.24462293) |

Creators are in `creators.yml`. Each bundle contains the data as CSV (UTF-8 with BOM) and
xlsx, the codebook, README, changelog, citation file, provenance and checksums.

## Make a release

From the repository root, with Python 3 and `openpyxl`, `pyyaml` and `requests`:

```bash
# 1. Build the data (for pipeline versions), then commit the build.
quarto render pipelines/fred/prepare_fred.qmd -P include_score:true

# 2. Assemble offline; review every file in the bundle.
python3 release/fred/zenodo_fred.py assemble 2026.11.1 release-bundles/fred/2026.11.1

# 3. After Lukas approves the bundle: draft (reserves the DOI and writes it into
#    CITATION.cff), inspect the draft on Zenodo, then publish with the same command plus --publish.
python3 release/fred/zenodo_fred.py upload release-bundles/fred/2026.11.1 \
  --previous release-bundles/fred/2025.11.1 --approve-production
```

`--previous` takes the published bundle of the preceding version and creates a new version
of the same concept record; omit it only for the first version. Upload reads `ZENODO_TOKEN`
(or `ZENODO_SANDBOX_TOKEN` with `--sandbox`), saves `zenodo-state.json` in the bundle as soon
as the draft exists, and resumes that draft when re-run. It checks that the remote files
match the bundle before setting metadata or publishing.

Keep each published bundle with its `zenodo-state.json`: the next release needs it.
Published bundles are archived in the maintainer's private storage
(`fred-data/zenodo-releases/`). `release-bundles/` is not tracked.
