# Data directory

Two kinds of file live here:

- `epoch_*.csv` — a **mirror** of Epoch AI's public model CSVs (CC-BY), refreshed by
  `fetch_data.py` on every run and committed so the build still works offline. Not
  hand-edited.
- `additions_*.json` — hand-researched models contributed by the research team. See
  [`SCHEMA.md`](SCHEMA.md).

## Epoch mirrors all three CSVs — do not make that conditional

`fetch_data.py` downloads all three of Epoch's model CSVs from https://epoch.ai/data/
on every run, whether or not the current build reads them:

| File | What it holds |
|---|---|
| `epoch_notable_ai_models.csv` | Epoch's long-running notable-models set (~1,040 rows) |
| `epoch_benchmarked_models.csv` | Model versions with ECI scores + release dates (~722 rows) |
| `epoch_large_scale_ai_models.csv` | Large-scale set (~522 rows); carries 2025 Chinese entries notable lacks |

Until 2026-07-28 the mirror held only the first two. That gap made a research agent
assert "Epoch has published no numeric training-compute estimate for any Baidu model
since 2021" — true of `notable` alone, false across Epoch's data, which has
ERNIE-4.5-300B-A47B at 2.82e24 and ERNIE-4.5-21B-A3B at 1.8e23 (both 2025-06-29,
`Speculative`) in `large_scale`.

### Neither `notable` nor `large_scale` is a superset of the other

The natural assumption — that the large-scale set is the notable set filtered by
training compute — is wrong, and containment fails in **both** directions. Matching
on model name (notable 1,040 unique names; large_scale 521):

| | Count |
|---|---|
| In `large_scale` only | **337** |
| In `notable` only | 856 |
| In both | 184 |

Models central to this project that exist **only** in `large_scale`: DeepSeek-V3.1,
V3.1-Terminus, V3.2, V3.2-Exp (the whole V3.1/V3.2 line), the ERNIE 4.5 family and
ERNIE x1, Doubao / Doubao-lite, MiniMax ABAB, CogVideoX.

So querying one file produces false negatives on model **membership**, not just on
compute figures — you can conclude Epoch doesn't track a model when the other file
has it. DeepSeek-V3.2 held an ECI top-20 slot in 2025 and is absent from `notable`,
so this is not a fringe-model problem. Search all three before writing "Epoch does
not cover X".

### Two other traps in these files

- **`Confidence` and `Training compute (FLOP)` are independent columns.** Rows exist
  with `Confidence = Confident` and an *empty* compute cell (e.g. ERNIE-4.5-VL-424B-A47B,
  2025-03-16). Test the compute cell for emptiness before quoting a confidence level.
- **`Organization` holds comma-joined strings** for joint work
  (`Z.ai (Zhipu AI),Tsinghua University`, `DeepSeek,Peking University`). Exact-match
  counting drops those rows; substring matching folds them in. Neither is wrong — state
  which you used. `fetch_data.py` takes the lead organization (`short_org`).

## Related copies

A dated provenance snapshot of the same three CSVs (fetched 2026-07-28) sits at
`~/research/holy-grail-compute-model/mc-labs/sources/epoch/` with a longer README. That
one is a frozen research snapshot — it is deliberately *not* refreshed by this cron, so
citations against it stay reproducible. This directory is the live build mirror. If the
two disagree, this one is newer.
