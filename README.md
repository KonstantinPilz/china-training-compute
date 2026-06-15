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
  confidence, data source, and the **basis** for the compute estimate. Click a point to
  open its source.

## Data

Two sources, merged by [`fetch_data.py`](fetch_data.py) into `docs/data.json`:

1. **Epoch AI** (primary) — public CC-BY [`notable_ai_models.csv`](https://epoch.ai/data/notable-ai-models),
   filtered to China-org models since 2023 with a training-compute estimate.
2. **Team research** (augmentation) — `data/additions_*.json`, hand-researched models Epoch
   is missing, with compute estimates and shown arithmetic. See [`data/SCHEMA.md`](data/SCHEMA.md).
   These render as white-edged diamonds. Models that duplicate an Epoch entry are dropped.

Training-compute values are mostly estimates of varying confidence; each point's basis is
on hover. Most are computed as `6 × params × tokens` (dense) or with active params (MoE).

## Update

`fetch_data.py` re-fetches the Epoch CSV (falling back to the local cache offline), re-merges
the additions, and rewrites `docs/data.json`. A daily VM cron (`update.sh`) pushes if it changed;
GitHub Pages (serving `/docs` on `main`) redeploys automatically.

```bash
python3 fetch_data.py
cd docs && python3 -m http.server 8021 --bind 127.0.0.1   # local dev
```

Built by a team of Konstantin's Claudes, 2026-06-15.
