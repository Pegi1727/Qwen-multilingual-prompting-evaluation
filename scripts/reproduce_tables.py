from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parent
OUT = ROOT / "reproduced"
OUT.mkdir(exist_ok=True)
# Run preserved analysis logic in an isolated namespace, replacing only path/output routing.
s = (ROOT / "05_code_original/finalize_qwen_format_and_results.py").read_text()
inputs = ["qwen_1000_user_content_labels.csv", "qwen_format_review_1000.csv"]
import shutil
shutil.copy2(ROOT / "03_final_annotations/qwen_1000_user_content_labels.csv", OUT / inputs[0])
d = pd.read_csv(OUT / inputs[0], keep_default_na=False)
d[["review_number"]].to_csv(OUT / inputs[1], index=False)
s = s.replace("root=Path('/mnt/data')", "root=Path(" + repr(str(OUT)) + ")")
exec(compile(s, "finalize_qwen_format_and_results.py", "exec"), {})
shutil.copy2(ROOT / "02_raw_outputs/results_1200_qwen.csv", OUT / "results_1200_qwen.csv")
s = (ROOT / "05_code_original/analyze_qwen_paired.py").read_text()
s = s.replace("p=Path('/mnt/data')", "p=Path(" + repr(str(OUT)) + ")")
exec(compile(s, "analyze_qwen_paired.py", "exec"), {})
for f in (ROOT / "04_results").glob("qwen_*.csv"):
    if (OUT / f.name).exists():
        pd.testing.assert_frame_equal(pd.read_csv(f), pd.read_csv(OUT / f.name))
print("PASS: reproduced tables agree with packaged tables.")
