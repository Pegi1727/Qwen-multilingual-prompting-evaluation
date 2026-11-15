# Notebook guide

Copy `notebooks/` and `requirements-notebooks.txt` into the repository root. Keep the images in `figures/`.

Notebooks 01–04 require the revised analytical CSV files. Extract the `Qwen_99_Items_Excluding_Q087` package into the repository if needed; the notebooks locate its retained analytical dataset recursively. Exactly one copy must be present. Notebook 05 requires only the six image files.

```bash
python -m pip install -r requirements-notebooks.txt
jupyter lab
```

Open the notebooks and run all cells. No model inference or new human annotation is performed. Notebooks 02–04 inspect archived summaries; 03 and 04 additionally recompute intervals and p-values. The package reproduction script remains the full source-data reproduction workflow.

These notebooks are newly prepared companions, not a claim about files already contained in archived v1.00. They are distributed without saved outputs. Their JSON structure and Python syntax were checked during preparation; execute them against the final repository data to validate the complete environment.
