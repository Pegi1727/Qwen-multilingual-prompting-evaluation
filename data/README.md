# Qwen revised reproducibility package — 99 retained items

Status: prepared for review / repository preparation; NOT publicly deposited.

## Authoritative analysis
Use `current_99_item_analysis/analysis_99_items/` for revised manuscript results.
Original collection: 100 items, 1,200 executions, 1,000 human annotations.
Post-hoc exclusion: Q087 across all conditions/languages, because its question requests the name of Earth's moon but its reference is `natural satellite`; C4 contexts contain that mismatched reference.
Retained: 99 items, 1,188 executions, 990 human annotations. Raw records and labels are unchanged.
Strict exact match: 175/1,188 execution-weighted; 109/990 with C1 counted once.
Human content correct: 321/990; format compliant: 362/990; both: 130/990.
Token-limit attainment: 216/1,188, maximum 64 newly generated tokens.
C1 is English; repeated baseline copies are not independent observations.
All nine baseline exact-match comparisons are significant after Holm adjustment across 18 tests; none of nine within-condition language comparisons is significant. Human metrics are descriptive, single-evaluator, with no inter-rater agreement measured.

## Reproduce the current analysis
From this package root:
```bash
python -m pip install -r requirements-analysis.txt
python current_99_item_analysis/reproduce_99_item_analysis.py
```
The code regenerates tables, exact binomial confidence intervals, paired exact McNemar tests, Holm correction, retained/excluded records and validation information. This reproduces analysis of stored outputs, NOT model inference. The exact original model revision and complete inference environment are not established by this package; do not infer missing settings.

## Folder guide
- `current_99_item_analysis/`: current script, original inputs and revised outputs; authoritative for manuscript numbers.
- `original_archive_for_audit/`: complete pre-exclusion package, preserved without editing. Its README, results and reproduction check describe the ORIGINAL 100-item analysis, not the current analysis. Exploratory automated labels are not human gold labels.
- `excluded_corrective_reruns_NOT_ANALYZED/`: three later C4 outputs, excluded because their prompt protocol differs. Never merge with the main sample.
- `checks/`: fresh reproduction log, environment and integrity verification.

Old manuscript PDFs, result graphics and graphical abstract are deliberately omitted from the current presentation: they have not been updated to 99 items. This is a data/code package, not a final typeset manuscript submission.

## Rights and release
No new publication or redistribution license is assigned. Before public GitHub release, the authors must confirm rights/permissions for all included material, select appropriate code/data licenses, and review repository contents and metadata. This archive does not claim public availability or a deposited DOI. It is not certified as anonymized for double-blind review; check journal requirements before submission.

## Integrity
`MANIFEST_SHA256.csv` lists all files except itself, with byte sizes and SHA-256 hashes. `verify_integrity.py` checks the manifest. Original subpackage manifests are retained in their original scope.
