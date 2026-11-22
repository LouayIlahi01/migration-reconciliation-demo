# migration-reconciliation-demo
Python demo that reconciles a source data extract against a simulated migrated copy, flags injected defects and measures detection rates.
# Migration reconciliation demo: rule-based data validation

A small Python demo of validating a migrated data table without a perfect reference copy, evaluated on a public benchmark with known errors. It is inspired by public descriptions of data migrations in regulatory reporting (moving data from source systems into a new data model). It uses public data only and is not affiliated with or based on any company's data.

## Data
The **Hospital** benchmark from the Raha/Baran data-cleaning project: a dirty table (1,000 rows, 20 columns, 509 wrong cells, 2.54%) and its clean ground truth. The checker only looks at the dirty table. The clean table is used only to score it.

## Checks
- **Format rules:** for example ZIP and provider number are 5 digits, phone is 10 digits, score is a percentage, sample is "N patients".
- **Consistency rules:** values that should be the same for a given key (provider number, measure code) must agree. A cell that differs from the group majority is flagged, and the majority value is proposed as the fix.
- **Shape profiling** (letters to `a`, digits to `9`, flag rare shapes) was tested and left out of the final checker.

## Results
| Checker | Flagged | Real errors found | False alarms | Recall | Precision |
|---|---|---|---|---|---|
| Format rules | 146 | 146 | 0 | 0.29 | 1.000 |
| Consistency rules | 423 | 423 | 0 | 0.83 | 1.000 |
| Shape profiling (not used) | 109 | 100 | 9 | 0.20 | 0.917 |
| **Format + consistency (final)** | **505** | **505** | **0** | **0.992** | **1.000** |

All 423 repairs proposed by the consistency rules restored the correct value. Files: `results.csv`, `flagged_cells.csv`.

## Limitations
- The rules were written after inspecting the errors in this dataset, so the results are optimistic and the rules are specific to this table.
- The benchmark errors are mostly random character substitutions. In this data, the rule "cell contains the letter x" alone finds almost every error (recall 1.0), which is a shortcut of this benchmark and not a realistic check. Real migration defects look different.
- Consistency checks need repeated entities (many rows per provider). They don't help where each entity appears once.
- Score and sample cells are flagged but cannot be repaired, since their values differ from row to row.

## Run
Open `reconciliation_demo.ipynb` in Google Colab and run all cells. The data is cloned from the public Raha repository (`github.com/BigDaMa/raha`).
