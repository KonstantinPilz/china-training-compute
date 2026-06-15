# Additional China models — data schema

Goal: augment Epoch's notable-models data with Chinese training runs (model released **2023-01-01 or later**) that Epoch is **missing** or for which Epoch has **no training-compute estimate**.

The 106 China models (since 2023) already in Epoch are listed in `epoch_china_inventory.txt`. **Do not re-add those** unless you are supplying a training-compute estimate Epoch lacks (note that in `compute_basis`).

Write your findings to `data/additions_<yourname>.json` as a JSON array of objects:

```json
[
  {
    "model": "ERNIE 4.0",
    "organization": "Baidu",
    "publication_date": "2023-10-17",
    "parameters": null,
    "training_compute_flop": 3.0e24,
    "compute_basis": "Estimated: dense ~260B params (rumored) × ~3T tokens × 6 = 4.7e24; rounded down for MoE uncertainty. No official figure.",
    "confidence": 0.3,
    "source_urls": ["https://...primary...", "https://...secondary..."],
    "notes": "Flagship Baidu LLM. Compute is our estimate, not official."
  }
]
```

Field rules:
- `publication_date`: YYYY-MM-DD (use YYYY-MM-01 if only month known; flag in notes).
- `training_compute_flop`: a NUMBER in FLOP (e.g. `3.0e24`), or `null` if no defensible estimate. If you estimate it, show the arithmetic in `compute_basis` (params × tokens × 6 for dense; adjust for MoE active params).
- `compute_basis`: one sentence. State whether it's an official figure, a third-party estimate (link it), or your own back-of-envelope (show the math). Per Konstantin's reasoning-transparency rules, every compute number must be justified.
- `confidence`: 0–1, your confidence in the compute number being within ~3x.
- `source_urls`: at least one. Prefer primary (tech report, paper, official blog). Flag paywalled/second-hand access.
- Only include models you can date and attribute to a China-based organization.

Use FLOP (quantity), never "FLOPs". Lead with sources. When you estimate, label it an estimate.
