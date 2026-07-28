# China AI Training Compute

Interactive scatter plot of notable Chinese AI models since 2023, by release date and
estimated **training compute (FLOP, log scale)**, colored by developer, with per-model
hover details. Rendered with Plotly.js.

**Live site:** https://konstantinpilz.github.io/china-training-compute/

- One point per model from a China-based organization, published 2023-01-01 or later,
  that has a training-compute estimate.
- Color by **developer** or **data source**. Optional running-max **frontier line**.
  Log/linear compute axis toggle.
- Hover shows model name, developer, release date, training compute, parameters,
  **ECI** (Epoch Capabilities Index) with its 90% CI where the model is benchmarked,
  confidence, data source, and the **basis** for the compute estimate. Click a point to
  open its source.
- **Color by ECI** renders capability on a Viridis scale (benchmarked models only;
  others shown gray) — useful for reading capability against compute and time.

## Data

Sources merged by [`fetch_data.py`](fetch_data.py) into `docs/data.json`:

1. **Epoch AI** (primary) — public CC-BY [`notable_ai_models.csv`](https://epoch.ai/data/notable-ai-models),
   filtered to China-org models since 2023 with a training-compute estimate.
2. **Team research** (augmentation) — `data/additions_*.json`, hand-researched models Epoch
   is missing, with compute estimates and shown arithmetic. See [`data/SCHEMA.md`](data/SCHEMA.md).
   These render as white-edged diamonds. Models that duplicate an Epoch entry are dropped.
3. **ECI** — `benchmarked_models.csv` (also Epoch, CC-BY) is joined by model name (nearest
   release date on ambiguity) to attach the Epoch Capabilities Index + 90% CI. ECI exists
   only for benchmarked models, so most points have none; that is expected.

Training-compute values are mostly estimates of varying confidence; each point's basis is
on hover. Most are computed as `6 × params × tokens` (dense) or with active params (MoE).

`fetch_data.py` mirrors **all three** of Epoch's model CSVs into `data/` on every run,
including `large_scale_ai_models.csv`, which the plot does not currently read. That is
deliberate — `notable` and `large_scale` are not nested sets, and a partial mirror yields
false negatives on model *membership*. Read [`data/README.md`](data/README.md) before
querying any one of them for an absence.

Plotting the models Epoch lists only in `large_scale` is opt-in:

```bash
python3 fetch_data.py --include-large-scale --out /tmp/preview.json
```

It adds ~88 China points (many of them size variants such as Qwen3-0.6B … Qwen3-32B) and
supersedes 8 team-research estimates with Epoch figures. Off by default so the daily cron
cannot change the published plot without a decision.

## Update

`fetch_data.py` re-fetches the Epoch CSVs (falling back to the local mirror offline), re-merges
the additions, and rewrites `docs/data.json`. A daily VM cron (`update.sh`) pushes if it changed;
GitHub Pages (serving `/docs` on `main`) redeploys automatically.

```bash
python3 fetch_data.py
cd docs && python3 -m http.server 8021 --bind 127.0.0.1   # local dev
```

Built by a team of Konstantin's Claudes, 2026-06-15.
