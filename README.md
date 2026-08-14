---
license: cc-by-4.0
language:
- en
size_categories:
- 10K<n<100K
task_categories:
- other
pretty_name: UNITARES Verdict Counterfactual — Paper v6.8 Repro Kit
tags:
- agent-governance
- ai-safety
- time-series
- reproducibility
---

# UNITARES Verdict Counterfactual — Paper v6.8 Reproducibility Kit

Reproducibility artifacts for §11.6 of *UNITARES: Information-Theoretic Governance of Heterogeneous Agent Fleets* (Wang, 2026).

- **Paper**: [cirwel/unitares-paper-v6](https://github.com/cirwel/unitares-paper-v6), tag `paper-v6.9.1`
- **Paper DOI** (concept): [10.5281/zenodo.19647159](https://doi.org/10.5281/zenodo.19647159)
- **Data DOI** (this release, v6.8.1-repro): [10.5281/zenodo.19705151](https://doi.org/10.5281/zenodo.19705151)
- **GitHub**: [cirwel/unitares-repro-v6](https://github.com/cirwel/unitares-repro-v6)
- **Source**: UNITARES production governance database, 30-day rolling window of `core.agent_state`
- **License**: CC-BY-4.0 (same as paper)

## What this is

The paper's §11.6 counterfactual asks: *how many basin assignments would flip if we replaced the legacy fleet-wide tanh coherence with a class-conditional grounded coherence?* On a 13,310-row production slice it reports a 28.9% flip rate, with directional bias into the `low` basin — empirical support for the homogenization-failure thesis.

This dataset publishes two snapshots of that counterfactual:

| File | Window | Rows | Flip rate |
|---|---|---|---|
| `verdict_counterfactual_v6_submission.csv` | 30 days ending **2026-04-18 21:00 MDT** | 13,292 | **28.8%** |
| `verdict_counterfactual_2026-04-23.csv` | 30 days ending **2026-04-23** | 16,879 | **44.3%** |

The submission snapshot is within 18 rows / 0.1pp of the figures in the published paper (exact rerun timing varies by seconds).

The 2026-04-23 snapshot shows a ~15pp increase in overall flip rate over 4 days of window shift, with the Phase 2 calibration constants held frozen at v6.8 submission values. **We do not claim this is a steady-state drift signal** — a 4-day gap with ~87% window overlap is one measurement, not a trend, and the magnitude is within the kind of shift class-conditional calibration drift could absorb in a single re-calibration pass.

Volume checks confirm the shift is not dominated by observer effects (daily row counts over the interval are ~800–1,500, no spikes). The per-class pattern is informative (Sentinel +25.4pp, Vigil +19.6pp, Lumen +15.8pp, default +15.3pp, **Watcher −11.3pp**). We publish both snapshots so others can reproduce §11.6 exactly.

## Columns

Each row is one agent-state observation, already pseudonymized to a class label — no agent UUIDs, session IDs, prompts, or KG content are in this export.

| Column | Type | Meaning |
|---|---|---|
| `class` | str | Agent class: `Lumen`, `Sentinel`, `Vigil`, `Watcher`, or `default` (tag-derived for non-resident agents) |
| `E` | float ∈ [0, 1] | Energy (productive capacity) |
| `I` | float ∈ [0, 1] | Information integrity |
| `S` | float ∈ [0, 1] | Entropy (lower is better) |
| `V` | float ∈ [-1, 1] | Void / accumulated E–I imbalance |
| `risk` | float ∈ [0, 1] | Risk score at time of observation |
| `c_legacy` | float ∈ [0, 1] | Legacy fleet-wide tanh coherence |
| `c_grounded` | float ∈ [0, 1] | Class-conditional grounded coherence |
| `basin_legacy` | str | Basin assignment under legacy coherence: `high`, `boundary`, `low` |
| `basin_grounded` | str | Basin assignment under grounded coherence |
| `flipped` | int | 1 if `basin_legacy != basin_grounded`, else 0 |

Basin thresholds and class-conditional calibration constants are in `scripts/verdict_counterfactual.py`.

## How to reproduce

```bash
pip install pandas matplotlib
python analysis.py  # prints the Table 5 equivalent + drift comparison
```

### ⚠️ Regeneration from the live DB no longer works — the CSVs are the record

`scripts/verdict_counterfactual.py` is kept for provenance, but **do not use it to
check these numbers.** The production database no longer retains either window.
Measured 2026-08-14: `core.agent_state` holds **490 rows** in 2026-03-19 → 2026-04-18,
against the 13,310 the original pull returned. There is no archive table.

```
2025-12  445     2026-04    599
2026-01   33     2026-05 12,630
2026-02  369     2026-06 27,868
2026-03  344     2026-07 16,869
```

The failure is silent: the query returns a small result set and a wrong flip rate
rather than an error. Anyone re-running the command below today gets a number that
looks plausible and is not the published one.

```bash
# PROVENANCE ONLY — returns a fraction of the rows as of 2026-08. Do not cite its output.
python scripts/verdict_counterfactual.py --window-days 30 \
  --end-date "2026-04-18 21:00:00-06:00" \
  --csv --output verdict_counterfactual_v6_submission.csv
```

The committed CSVs in `data/` are therefore the surviving row-level record of both
windows, and `analysis.py` — which reads them and touches no database — is the
reproduction path. A companion implementation that additionally *recomputes* the
grounded coherence and both basin labels from these rows and the published Phase 2
constants (rather than re-reading the stored `flipped` column) is in
[cirwel/digital-proprioception-paper](https://github.com/cirwel/digital-proprioception-paper)
at `analysis/phase-2-2026-04-18/reproduce_basinflip.py`; it returns 28.84% with
26,574 of 26,584 labels reproducing exactly.

## Limitations

- Fleet composition is UNITARES-specific (five resident agents + ephemeral coding assistants + embodied Lumen). The absolute flip rates are not directly transferable to other fleets; the *method* is.
- Paper §12.5 (write-path hygiene) and §11.7 (identity system maturity) describe known caveats in the underlying trajectory data. Read both sections before citing these numbers in derivative work.
- Class-conditional calibration constants in the script are frozen at v6.8 submission. Regenerating the 2026-04-23 snapshot against the *current* production calibration (not frozen) would yield a different number — we deliberately use the frozen constants to isolate fleet drift from calibration drift.

## Citation

Cite the paper for the method, cite the dataset for the data.

```bibtex
@article{wang2026unitares,
  author  = {Wang, Kenny},
  title   = {UNITARES: Information-Theoretic Governance of Heterogeneous Agent Fleets},
  year    = {2026},
  version = {v6.9.1},
  doi     = {10.5281/zenodo.19647159},
  url     = {https://github.com/cirwel/unitares-paper-v6}
}

@dataset{wang2026unitares_repro_v6,
  author    = {Wang, Kenny},
  title     = {UNITARES Verdict Counterfactual — Paper v6.8 Reproducibility Kit},
  year      = {2026},
  version   = {v6.8.1-repro},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.19705151},
  url       = {https://github.com/cirwel/unitares-repro-v6}
}
```
