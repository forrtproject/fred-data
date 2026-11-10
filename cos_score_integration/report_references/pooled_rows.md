# Exclude seven superseded SCORE aggregates

The seven rows in `holds.csv` are COS posthoc fixed-effect aggregations of two attempts each. Their fourteen individual attempts have completed reports and separate validated FReD entry-sheet rows (`COS coding`, rows 5484–5497). Shipping the pooled rows alongside those attempts would count their participants twice; these pooled rows are permanently superseded.

The manifest records the published claim/report IDs, aggregate projects, aggregation scripts, component attempt IDs, project links and individual report links. The scripts and COS source data were checked on 10 November 2026; the imported sample sizes, p-values and converted correlations matched all seven aggregates. The [full investigation and source hashes](https://github.com/forrtproject/fred-data/tree/a3d0f8f3e/cos_score_integration/report_references) remain available in git history.

The filter excludes these seven identities when optional SCORE integration runs, leaving the archived source files and every retained value unchanged. This reduces the imported source from 132 to 125 rows. Citation corrections are separate in [PR #167](https://github.com/forrtproject/fred-data/pull/167).

One-off verification checked both real source files and executed the notebook’s integration chunk, comparing every retained field exactly. No generated exports or entry-sheet values are edited.
