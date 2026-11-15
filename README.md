# Qwen Multilingual Prompting Evaluation

### Data, Analysis Code, and Supplementary Materials for the Revised 99-Item Study

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24242462.svg)](https://doi.org/10.5281/zenodo.24242462)

**Archived release:** v1.00 · **DOI:** [10.5281/zenodo.24242462](https://doi.org/10.5281/zenodo.24242462)

This repository supports an evaluation of Qwen under four prompting conditions involving English, Azerbaijani, Persian, and Turkish. The revised analysis distinguishes **human-rated content correctness**, **format compliance**, **joint success**, and **strict exact match**. These measures are not interchangeable.

The retained sample comprises **99 items**, **1,188 execution records**, and **990 unique human-rated responses**. One defective item, Q087, was excluded after a documented post-hoc data-quality audit.

## Contents

- [Study design](#study-design)
- [Evaluation measures](#evaluation-measures)
- [Results](#results)
- [Figures](#figures)
- [Conclusion](#conclusion)
- [Data-quality audit](#data-quality-audit)
- [Reproducibility](#reproducibility)
- [Limitations](#limitations)
- [Citation](#citation)
- [Contact](#contact)
- [License](#license)

## Study design

| Condition | Description |
| --- | --- |
| C1 | English baseline |
| C2 | Target-language prompting |
| C3 | Mixed-language prompting |
| C4 | Reference answer supplied in context |

**Target languages:** Azerbaijani (`az`), Persian (`fa`), and Turkish (`tr`). The English baseline is labeled `en`.

C1 contributes one unique response per item to the human-rated analysis. Each of C2–C4 contributes one response per item and target language.

| Analytical component | Retained sample |
| --- | ---: |
| Items | 99 |
| Execution records | 1,188 |
| Unique human-rated responses | 990 |
| Unique C1 responses | 99 |
| Responses in each of C2, C3, and C4 | 297 |

The execution archive contains C1 records in three source-language branches. These repeated baseline records must not be treated as independent observations.

## Evaluation measures

| Measure | Definition |
| --- | --- |
| Content correctness | Response classified as correct by the human evaluator. Mixed responses are not counted as correct. |
| Format compliance | Response satisfies the requested output format, independently of content correctness. |
| Joint success | The same response is both content-correct and format-compliant. |
| Strict exact match | Direct equality between the stored generated response and reference-answer strings, without additional normalization. |

Human content classifications distinguish **correct**, **incorrect**, **mixed**, and **unintelligible** responses. Human-rated outcomes are descriptive and were assessed by a single evaluator. Inferential comparisons reported here concern strict exact match only.

## Results

### Human-rated outcomes by condition

Cells report **n (%)** using each row's sample size.

| Condition | N | Content correct | Format compliant | Joint success |
| --- | ---: | ---: | ---: | ---: |
| C1: English baseline | 99 | 68 (68.69%) | 45 (45.45%) | 37 (37.37%) |
| C2: Target language | 297 | 24 (8.08%) | 46 (15.49%) | 2 (0.67%) |
| C3: Mixed language | 297 | 104 (35.02%) | 213 (71.72%) | 68 (22.90%) |
| C4: Answer in context | 297 | 125 (42.09%) | 58 (19.53%) | 23 (7.74%) |
| **Overall** | **990** | **321 (32.42%)** | **362 (36.57%)** | **130 (13.13%)** |

C1 had the highest observed content correctness and joint success. C3 had the highest observed format compliance. These are descriptive findings, not estimates of causal effects.

### Content classification and format compliance

| Content classification | Format compliant | Format noncompliant | Total |
| --- | ---: | ---: | ---: |
| Correct | 130 | 191 | 321 |
| Incorrect | 229 | 272 | 501 |
| Mixed | 1 | 64 | 65 |
| Unintelligible | 2 | 101 | 103 |
| **Total** | **362** | **628** | **990** |

Of the 321 content-correct responses, 191 did not satisfy the requested format. Conversely, 232 format-compliant responses were not classified as correct. Format compliance is therefore not a substitute for content correctness.

### Strict exact match by condition and language

Each row contains 99 items. Confidence intervals are **pointwise 95% exact binomial intervals**, not simultaneous or multiplicity-adjusted intervals.

| Condition | Language | Exact matches / N | Exact match | 95% CI |
| --- | --- | ---: | ---: | ---: |
| C1 | English | 33/99 | 33.33% | 24.18–43.52% |
| C2 | Azerbaijani | 0/99 | 0.00% | 0.00–3.66% |
| C2 | Persian | 0/99 | 0.00% | 0.00–3.66% |
| C2 | Turkish | 1/99 | 1.01% | 0.03–5.50% |
| C3 | Azerbaijani | 23/99 | 23.23% | 15.33–32.79% |
| C3 | Persian | 17/99 | 17.17% | 10.33–26.06% |
| C3 | Turkish | 17/99 | 17.17% | 10.33–26.06% |
| C4 | Azerbaijani | 3/99 | 3.03% | 0.63–8.60% |
| C4 | Persian | 4/99 | 4.04% | 1.11–10.02% |
| C4 | Turkish | 11/99 | 11.11% | 5.68–19.01% |

Two overall summaries use different weighting schemes:

- **Execution-weighted:** 175/1,188 = **14.73%**, including the repeated C1 records.
- **C1 counted once per item:** 109/990 = **11.01%**.

These denominators must be stated explicitly when reporting overall exact match.

### Paired statistical comparisons

Two-sided exact McNemar tests used **99 matched items per comparison**. Holm correction was applied across a single family of **18 tests**: nine baseline comparisons and nine within-condition language comparisons.

- All nine baseline comparisons remained significant at the Holm-adjusted 0.05 threshold, with higher strict exact match for C1.
- None of the nine within-condition language comparisons was significant after correction.
- Nonsignificance does **not** establish language equivalence.
- These tests do not provide inferential evidence about the human-rated outcomes.
## Figures

The images below are linked directly from the repository root. Figure numbering follows the existing file names.

| Figure | File |
| --- | --- |
| Figure 1 | [Figure_1_Metric_Comparison.png](./Figure_1_Metric_Comparison.png) |
| Figure 2 | [Figure_2_Content_Distribution.png](./Figure_2_Content_Distribution.png) |
| Figure 3 | [Figure_3_Exact_Match_Confidence_Intervals.png](./Figure_3_Exact_Match_Confidence_Intervals.png) |
| Figure 4 | [Figure_4_Language_Specific_Outcomes.png](./Figure_4_Language_Specific_Outcomes.png) |
| Figure 5 | [Figure_5_Content_by_Format.png](./Figure_5_Content_by_Format.png) |
| Graphical abstract | [Qwen_Graphical_Abstract_99_Items.png](./Qwen_Graphical_Abstract_99_Items.png) |

### Graphical abstract

![Graphical abstract for the revised 99-item Qwen multilingual prompting evaluation](./Qwen_Graphical_Abstract_99_Items.png)

*Overview of the study design and revised analysis. Human-rated outcomes and strict exact match are distinct; findings are subject to single-evaluator and study-design limitations.*

### Figure 1. Content correctness and format compliance

![Manuscript Figure 1: Content correctness and format compliance](./Figure_5_Content_by_Format.png)

### Figure 2. Human-rated content distribution

![Manuscript Figure 2: Human-rated content distribution](./Figure_2_Content_Distribution.png)

### Figure 3. Comparison of evaluation measures

![Manuscript Figure 3: Comparison of evaluation measures](./Figure_1_Metric_Comparison.png)

### Figure 4. Language-specific outcomes

![Manuscript Figure 4: Language-specific outcomes](./Figure_4_Language_Specific_Outcomes.png)

### Figure 5. Strict exact match and confidence intervals

![Manuscript Figure 5: Strict exact-match estimates with confidence intervals](./Figure_3_Exact_Match_Confidence_Intervals.png)

## Conclusion

The revised analysis shows that performance depends on both the prompting condition and the evaluation criterion. The English baseline had the highest observed human-rated content correctness, whereas mixed-language prompting had the highest observed format compliance. Supplying a reference answer in context did not ensure a correct, format-compliant response. Overall joint success was 13.13%.

Strict exact match captured a different and narrower aspect of performance than human judgment. After Holm correction, the English baseline outperformed each target-language condition–language group on strict exact match; within-condition language comparisons did not reach the adjusted significance threshold. These findings do not establish language equivalence, intrinsic language superiority, model bias, or causal mechanisms.

The study supports reporting content correctness and instruction-format adherence separately rather than treating a single score as a complete account of multilingual response quality.

## Data-quality audit

Q087 was excluded from all conditions and languages following a **post-hoc**, non-preregistered audit. Its question asked for the name of Earth's natural satellite, but its stored reference answer was “natural satellite.” The original C4 contexts also contained this defective reference.

| Component | Original | Excluded Q087 | Retained |
| --- | ---: | ---: | ---: |
| Items | 100 | 1 | 99 |
| Execution records | 1,200 | 12 | 1,188 |
| Unique human-rated responses | 1,000 | 10 | 990 |

No other items were excluded. Original reference strings, outputs, and human labels were preserved rather than rewritten. Excluded Q087 records were retained separately for audit. Corrected C4 reruns were not merged into the primary analysis because their prompt protocol differed from the original collection.

## Reproducibility

**Versioned archive:** [Zenodo, v1.00](https://doi.org/10.5281/zenodo.24242462)

**Development repository:** [Pegi1727/Qwen-multilingual-prompting-evaluation](https://github.com/Pegi1727/Qwen-multilingual-prompting-evaluation)

The revised analytical package is named `Qwen_99_Items_Excluding_Q087`. The package's own README and manifest document its file layout. From the directory containing `reproduce_99_item_analysis.py`, install the required analytical libraries and run:

```bash
python -m pip install pandas scipy
python reproduce_99_item_analysis.py
```

The analytical workflow reconstructs results from preserved source records and writes outputs to `analysis_99_items/`. It performs no new model inference or human labeling. Its outputs include retained and excluded records, human-evaluation summaries, strict exact-match estimates, paired tests, and validation results.

Reproducing calculations from stored outputs is different from reproducing model generation. A fresh inference run may depend on the model revision, generation settings, and software environment. Consult preserved metadata for documented generation settings; settings not supported by those records should not be inferred.

For a fixed research reference, cite the Zenodo release rather than the mutable `main` branch. The current repository may contain updates not included in v1.00.

## Limitations

- Human evaluation was conducted by one evaluator; no inter-rater reliability estimate is available.
- Q087 was excluded post hoc, not under a preregistered exclusion rule.
- The results concern this item set, model configuration, and prompting protocol; broad generalization is not warranted.
- Repeated baseline execution records are not independent observations.
- Strict string equality is sensitive to response wording and should not be equated with human-assessed correctness.
- Human-rated comparisons are descriptive; reported inferential tests concern strict exact match only.
- C3 does not isolate a single linguistic feature, and C4 is not an evidence-conflict experiment.
- Nonsignificant language comparisons do not establish equivalence.

## Citation

Please cite the archived research package when using its data, code, or supplementary materials. Use the **Cite as** export on Zenodo for the authoritative creator names, publication date, and citation metadata:

**Qwen Multilingual Prompting Evaluation: Data, Analysis Code, and Supplementary Materials for the Revised 99-Item Study.** Version v1.00. Zenodo. https://doi.org/10.5281/zenodo.24242462

The following minimal BibTeX entry provides the verified title, version, and identifier. Add the creator and year fields from the Zenodo record before using it in a manuscript bibliography.

```bibtex
@misc{qwen_multilingual_99items_v100,
  title     = {Qwen Multilingual Prompting Evaluation: Data, Analysis Code, and Supplementary Materials for the Revised 99-Item Study},
  version   = {v1.00},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.24242462},
  url       = {https://doi.org/10.5281/zenodo.24242462}
}
```

## Contact

**Repository maintainer:** [Pegi1727](https://github.com/Pegi1727)

For questions, corrections, or reproducibility reports, use the repository's [Issues page](https://github.com/Pegi1727/Qwen-multilingual-prompting-evaluation/issues), if enabled. Please identify the release, relevant file, and steps needed to reproduce the issue. Do not include private or sensitive information in public reports.

## License

Consult the license supplied with the repository and the license metadata on the Zenodo record before reusing materials. Public accessibility alone does not establish permission for unrestricted reuse. No additional license is granted by this README.
