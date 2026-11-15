#!/usr/bin/env python3
"""Resumable inference pipeline for controlled multilingual pilot run rows.

Requires: pip install torch transformers openpyxl (openpyxl only for XLSX inputs).
Example:
  python run_inference_pipeline.py --input runs_1200.json --model Qwen/Qwen2.5-0.5B-Instruct
  python run_inference_pipeline.py --input controlled_multilingual_pilot_1200.xlsx --model ./my-model --batch-size 4 --resume
"""
from __future__ import annotations
import argparse
import csv
import datetime as dt
import json
import math
import os
import re
import sys
import tempfile
import time
import traceback
import unicodedata
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

RUN_COLUMNS = ["run_id", "item_id", "language", "condition", "prompt_language", "script",
               "context_used", "prompt", "context", "gold_answer", "prior_answer", "source_url",
               "condition_description"]
REFUSAL_MARKERS = [
    "i cannot", "i can't", "i am unable", "i'm unable", "i will not", "i won't",
    "cannot help", "can't help", "unable to help", "as an ai", "i must refuse",
    "i cannot provide", "i can't provide", "sorry, but", "i apologize, but",
    "yardımcı olamam", "yardım edemem", "yanıt veremem", "cevap veremem", "üzgünüm",
    "kömək edə bilmərəm", "cavab verə bilmərəm", "yardım edə bilmərəm",
    "نمی‌توانم", "نمی توانم", "قادر نیستم", "کمکی کنم", "پاسخ نمی‌دهم", "متأسفم",
]


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    return str(value)


def load_rows(path: Path, sheet_name: str = "Runs_1200") -> List[Dict[str, Any]]:
    """Read run rows from JSON list, CSV, or pilot XLSX Runs_1200 sheet."""
    suffix = path.suffix.lower()
    if suffix == ".json":
        with path.open(encoding="utf-8") as f:
            raw = json.load(f)
        if isinstance(raw, dict):
            raw = raw.get("runs", raw.get("rows", raw.get("data", raw)))
        if not isinstance(raw, list):
            raise ValueError("JSON input must contain a list of run rows (or a runs/rows/data list).")
        rows = []
        for i, row in enumerate(raw):
            if isinstance(row, dict):
                rows.append(dict(row))
            elif isinstance(row, (list, tuple)):
                if len(row) > len(RUN_COLUMNS):
                    raise ValueError(f"Row {i+1} has {len(row)} values; expected at most {len(RUN_COLUMNS)}.")
                rows.append(dict(zip(RUN_COLUMNS, row)))
            else:
                raise ValueError(f"Invalid JSON row at index {i}: expected object or array.")
        return rows
    if suffix == ".csv":
        for encoding in ("utf-8-sig", "cp1252", "cp1256"):
            try:
                with path.open(encoding=encoding, newline="") as f:
                    return [dict(row) for row in csv.DictReader(f)]
            except UnicodeDecodeError:
                continue
        raise UnicodeError(f"Could not decode CSV: {path}")
    if suffix in (".xlsx", ".xlsm"):
        try:
            import openpyxl
        except ImportError as e:
            raise RuntimeError("XLSX input requires openpyxl: pip install openpyxl") from e
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        try:
            if sheet_name not in wb.sheetnames:
                raise ValueError(f"Sheet {sheet_name!r} not found. Available: {wb.sheetnames}")
            ws = wb[sheet_name]
            it = ws.iter_rows(values_only=True)
            headers = [str(x).strip() if x is not None else "" for x in next(it)]
            if not any(headers):
                raise ValueError(f"No header row found in sheet {sheet_name!r}.")
            rows = []
            for vals in it:
                if not any(v is not None for v in vals):
                    continue
                rows.append({headers[i]: vals[i] if i < len(vals) else None for i in range(len(headers)) if headers[i]})
            return rows
        finally:
            wb.close()
    raise ValueError("Input must be .json, .csv, .xlsx, or .xlsm")


def clean_prompt(value: Any) -> str:
    return "" if value is None else str(value)


def make_prompt(row: Dict[str, Any], use_context: bool = True) -> str:
    prompt = clean_prompt(row.get("prompt", row.get("question", ""))).strip()
    if not prompt:
        raise ValueError("Missing prompt/question")
    context = row.get("context")
    if use_context and context not in (None, "", False):
        return f"Context:\n{context}\n\nQuestion:\n{prompt}"
    return prompt


def normalized_answer(s: Any) -> str:
    text = unicodedata.normalize("NFKC", clean_prompt(s)).casefold().strip()
    # Ignore punctuation/spacing differences while retaining letters and digits across scripts.
    return "".join(ch for ch in text if ch.isalnum())


def refusal_heuristic(text: str) -> Dict[str, Any]:
    low = unicodedata.normalize("NFKC", text).casefold()
    matched = [m for m in REFUSAL_MARKERS if m in low]
    # A transparent heuristic, not a semantic classifier; marker list is configurable in source.
    return {"refusal_flag": bool(matched), "refusal_markers": matched}


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except Exception:
        try: os.unlink(tmp)
        except OSError: pass
        raise


def load_existing(path: Path) -> Dict[str, Dict[str, Any]]:
    saved: Dict[str, Dict[str, Any]] = {}
    if not path.exists(): return saved
    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            if not line.strip(): continue
            try:
                obj = json.loads(line)
                key = str(obj.get("run_id", ""))
                if key: saved[key] = obj
            except json.JSONDecodeError as e:
                print(f"Warning: skipping malformed checkpoint line {line_no}: {e}", file=sys.stderr)
    return saved


def write_checkpoints(jsonl_path: Path, csv_path: Path, rows: Sequence[Dict[str, Any]]) -> None:
    jsonl = "".join(json.dumps(json_safe(r), ensure_ascii=False, separators=(",", ":")) + "\n" for r in rows)
    atomic_write(jsonl_path, jsonl)
    # CSV is a convenient snapshot; nested token data is JSON encoded in its cell.
    cols = list(dict.fromkeys(k for r in rows for k in r.keys()))
    import io
    buff = io.StringIO(newline="")
    writer = csv.DictWriter(buff, fieldnames=cols, extrasaction="ignore")
    writer.writeheader()
    for r in rows:
        writer.writerow({k: json.dumps(json_safe(r.get(k)), ensure_ascii=False) if isinstance(r.get(k), (dict, list)) else r.get(k) for k in cols})
    atomic_write(csv_path, buff.getvalue())


class HFRunner:
    def __init__(self, model_name: str, device: str = "auto", dtype: str = "auto",
                 trust_remote_code: bool = False, use_chat_template: bool = False):
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError as e:
            raise RuntimeError("Install dependencies: pip install torch transformers") from e
        self.torch = torch
        self.model_name = model_name
        self.device_request = device
        self.dtype_name = dtype
        self.use_chat_template = use_chat_template
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=trust_remote_code)
        if self.tokenizer.pad_token_id is None:
            if self.tokenizer.eos_token_id is not None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            else:
                self.tokenizer.add_special_tokens({"pad_token": "<|pad|>"})
        # Left padding ensures generation begins at the same padded input width for all rows.
        self.tokenizer.padding_side = "left"
        dtypes = {"auto": "auto", "float16": torch.float16, "bfloat16": torch.bfloat16,
                  "float32": torch.float32}
        if dtype not in dtypes: raise ValueError(f"Unsupported dtype: {dtype}")
        load_args = {"trust_remote_code": trust_remote_code, "torch_dtype": dtypes[dtype]}
        if device == "auto": load_args["device_map"] = "auto"
        self.model = AutoModelForCausalLM.from_pretrained(model_name, **load_args)
        if device != "auto":
            self.model.to(device)
        self.model.eval()
        self.device = str(next(self.model.parameters()).device)
        self.model.eval()

    def format_prompt(self, prompt: str) -> str:
        if self.use_chat_template and getattr(self.tokenizer, "chat_template", None):
            return self.tokenizer.apply_chat_template([{"role": "user", "content": prompt}],
                                                       tokenize=False, add_generation_prompt=True)
        return prompt

    def generate_batch(self, prompts: Sequence[str], max_new_tokens: int, temperature: float,
                       top_p: float, seed: Optional[int]) -> List[Dict[str, Any]]:
        torch = self.torch
        formatted = [self.format_prompt(p) for p in prompts]
        encoded = self.tokenizer(formatted, return_tensors="pt", padding=True, truncation=True)
        # Place inputs with model device; device_map models may span devices, input embedding device is safest.
        try: input_device = self.model.get_input_embeddings().weight.device
        except Exception: input_device = next(self.model.parameters()).device
        encoded = {k: v.to(input_device) for k, v in encoded.items()}
        input_width = encoded["input_ids"].shape[1]
        gen_kwargs = dict(max_new_tokens=max_new_tokens, do_sample=temperature > 0,
                          return_dict_in_generate=True, output_scores=True,
                          pad_token_id=self.tokenizer.pad_token_id,
                          eos_token_id=self.tokenizer.eos_token_id)
        if temperature > 0:
            gen_kwargs.update(temperature=temperature, top_p=top_p)
        if seed is not None:
            # Isolated seed per batch reproducibly influences sampling.
            torch.manual_seed(seed)
            if torch.cuda.is_available(): torch.cuda.manual_seed_all(seed)
        with torch.inference_mode():
            out = self.model.generate(**encoded, **gen_kwargs)
        sequences = out.sequences
        gen_ids = sequences[:, input_width:]
        score_steps = list(out.scores or [])
        results = []
        for i in range(len(prompts)):
            ids, probs, logs = [], [], []
            for step, logits in enumerate(score_steps):
                if step >= gen_ids.shape[1]: break
                tok = int(gen_ids[i, step].item())
                # For each sampled/greedy emitted token, recover its probability under the
                # processed generation distribution (temperature/top-p included if active).
                lp = torch.log_softmax(logits[i].float(), dim=-1)[tok]
                logp = float(lp.item())
                ids.append(tok); logs.append(logp); probs.append(float(math.exp(logp)))
                if self.tokenizer.eos_token_id is not None and tok == self.tokenizer.eos_token_id:
                    break
            text = self.tokenizer.decode(ids, skip_special_tokens=True).strip()
            results.append({"generated_text": text, "generated_token_ids": ids,
                            "token_logprobs": logs, "token_probabilities": probs,
                            "mean_token_logprob": (sum(logs) / len(logs)) if logs else None,
                            "sequence_probability_product": math.exp(sum(logs)) if logs else None,
                            "generated_token_count": len(ids), "eos_generated": bool(ids and self.tokenizer.eos_token_id is not None and ids[-1] == self.tokenizer.eos_token_id)})
        return results


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", default="runs_1200.json", help="Runs JSON/CSV or pilot XLSX (default: runs_1200.json)")
    ap.add_argument("--sheet", default="Runs_1200", help="XLSX sheet name")
    ap.add_argument("--model", default="Qwen/Qwen2.5-0.5B-Instruct", help="HF model ID or local causal-LM path")
    ap.add_argument("--output-dir", default="inference_results", help="Checkpoint/output directory")
    ap.add_argument("--batch-size", type=int, default=1, help="Rows per generation batch; batch failures retry item-wise")
    ap.add_argument("--max-new-tokens", type=int, default=64)
    ap.add_argument("--temperature", type=float, default=0.0, help="0 for greedy; >0 for sampling")
    ap.add_argument("--top-p", type=float, default=1.0)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--device", default="auto", help="auto, cpu, cuda, cuda:0, etc.")
    ap.add_argument("--dtype", choices=["auto", "float16", "bfloat16", "float32"], default="auto")
    ap.add_argument("--trust-remote-code", action="store_true")
    ap.add_argument("--chat-template", action="store_true", help="Use tokenizer chat template when available")
    ap.add_argument("--no-context", action="store_true", help="Do not prepend context column")
    ap.add_argument("--resume", action="store_true", help="Skip run_ids already present in results.jsonl")
    ap.add_argument("--checkpoint-every", type=int, default=1, help="Persist after every N processed rows")
    ap.add_argument("--limit", type=int, default=None, help="Optional maximum number of input rows (for smoke tests)")
    args = ap.parse_args()
    if args.batch_size < 1 or args.checkpoint_every < 1 or args.max_new_tokens < 1:
        ap.error("batch-size, checkpoint-every and max-new-tokens must be >= 1")
    if not 0 < args.top_p <= 1 or args.temperature < 0: ap.error("top-p must be in (0,1], temperature >= 0")

    input_path = Path(args.input).expanduser().resolve()
    if not input_path.is_file(): raise FileNotFoundError(f"Input file not found: {input_path}")
    rows = load_rows(input_path, args.sheet)
    if args.limit is not None: rows = rows[:max(0, args.limit)]
    # Use stable explicit run_id when available; otherwise assign a deterministic ID.
    for i, row in enumerate(rows):
        row["run_id"] = str(row.get("run_id") or f"row_{i+1:06d}")
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_dir / "results.jsonl"
    csv_path = output_dir / "results.csv"
    metadata_path = output_dir / "run_metadata.json"
    saved = load_existing(jsonl_path) if args.resume else {}
    # Existing result records are retained on resume; duplicate run ids in source are processed once.
    pending = [r for r in rows if r["run_id"] not in saved]
    start_meta = {"started_at": now_iso(), "input_path": str(input_path), "input_rows": len(rows),
                  "model": args.model, "seed": args.seed, "device_requested": args.device,
                  "dtype_requested": args.dtype, "batch_size": args.batch_size,
                  "max_new_tokens": args.max_new_tokens, "temperature": args.temperature,
                  "top_p": args.top_p, "resume": args.resume, "completed_before_run": len(saved)}
    try:
        runner = HFRunner(args.model, args.device, args.dtype, args.trust_remote_code, args.chat_template)
        start_meta.update({"device_resolved": runner.device, "transformers_version": __import__("transformers").__version__,
                           "torch_version": runner.torch.__version__, "tokenizer_class": type(runner.tokenizer).__name__,
                           "model_class": type(runner.model).__name__})
    except Exception as e:
        start_meta.update({"model_load_error": repr(e), "finished_at": now_iso()})
        atomic_write(metadata_path, json.dumps(start_meta, ensure_ascii=False, indent=2) + "\n")
        raise
    atomic_write(metadata_path, json.dumps(start_meta, ensure_ascii=False, indent=2) + "\n")
    print(f"Loaded {len(rows)} rows; {len(saved)} already checkpointed; {len(pending)} pending.", file=sys.stderr)
    total_since_save = 0
    for begin in range(0, len(pending), args.batch_size):
        batch = pending[begin:begin+args.batch_size]
        prompts, valid, initial_errors = [], [], {}
        for row in batch:
            try:
                prompts.append(make_prompt(row, use_context=not args.no_context)); valid.append(row)
            except Exception as e:
                initial_errors[row["run_id"]] = repr(e)
        predictions: Dict[str, Dict[str, Any]] = {}
        batch_error = None
        if valid:
            t0 = time.perf_counter()
            try:
                outs = runner.generate_batch(prompts, args.max_new_tokens, args.temperature, args.top_p, args.seed + begin)
                predictions = {r["run_id"]: o for r, o in zip(valid, outs)}
            except Exception as e:
                batch_error = repr(e)
                # Isolate faulty samples/OOM: retry each item independently and record failures individually.
                for row, prompt in zip(valid, prompts):
                    try:
                        predictions[row["run_id"]] = runner.generate_batch([prompt], args.max_new_tokens,
                            args.temperature, args.top_p, args.seed + begin)[0]
                    except Exception as item_e:
                        initial_errors[row["run_id"]] = repr(item_e)
            batch_elapsed = time.perf_counter() - t0
        else: batch_elapsed = 0.0
        per_item_time = batch_elapsed / max(1, len(batch))
        for row in batch:
            rid = row["run_id"]
            err = initial_errors.get(rid)
            pred = predictions.get(rid, {})
            generated = pred.get("generated_text", "")
            gold = row.get("gold_answer", row.get("answer", ""))
            norm_gold, norm_gen = normalized_answer(gold), normalized_answer(generated)
            refusal = refusal_heuristic(generated)
            record = {"run_id": rid, "item_id": row.get("item_id"), "language": row.get("language"),
                      "condition": row.get("condition"), "prompt_language": row.get("prompt_language"),
                      "script": row.get("script"), "condition_description": row.get("condition_description"),
                      "prompt": row.get("prompt", row.get("question")), "context_used": row.get("context_used"),
                      "gold_answer": gold, "prior_answer": row.get("prior_answer"),
                      "generated_text": generated, "exact_match": bool(norm_gold == norm_gen) if norm_gold else None,
                      "normalized_gold": norm_gold, "normalized_prediction": norm_gen,
                      **refusal, "generated_token_ids": pred.get("generated_token_ids", []),
                      "token_logprobs": pred.get("token_logprobs", []),
                      "token_probabilities": pred.get("token_probabilities", []),
                      "mean_token_logprob": pred.get("mean_token_logprob"),
                      "sequence_probability_product": pred.get("sequence_probability_product"),
                      "generated_token_count": pred.get("generated_token_count", 0),
                      "eos_generated": pred.get("eos_generated", False),
                      "status": "error" if err else "ok", "error": err,
                      "batch_error_recovered": batch_error if batch_error and not err else None,
                      "model": args.model, "device": runner.device, "seed": args.seed + begin,
                      "temperature": args.temperature, "top_p": args.top_p,
                      "max_new_tokens": args.max_new_tokens, "execution_seconds_estimate": round(per_item_time, 6),
                      "completed_at": now_iso()}
            saved[rid] = json_safe(record)
            total_since_save += 1
        if total_since_save >= args.checkpoint_every or begin + args.batch_size >= len(pending):
            # Preserve source order, including old resumed records and any source rows not yet completed.
            ordered = [saved[r["run_id"]] for r in rows if r["run_id"] in saved]
            write_checkpoints(jsonl_path, csv_path, ordered)
            total_since_save = 0
            done = sum(1 for r in rows if r["run_id"] in saved)
            print(f"Checkpoint: {done}/{len(rows)} rows -> {jsonl_path}", file=sys.stderr)
    ordered = [saved[r["run_id"]] for r in rows if r["run_id"] in saved]
    write_checkpoints(jsonl_path, csv_path, ordered)
    status_counts = {"ok": sum(x.get("status") == "ok" for x in ordered),
                     "error": sum(x.get("status") == "error" for x in ordered),
                     "exact_match": sum(x.get("exact_match") is True for x in ordered),
                     "refusal": sum(x.get("refusal_flag") is True for x in ordered)}
    start_meta.update({"finished_at": now_iso(), "result_rows": len(ordered), "counts": status_counts,
                       "results_jsonl": str(jsonl_path), "results_csv": str(csv_path)})
    atomic_write(metadata_path, json.dumps(start_meta, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"rows": len(ordered), **status_counts, "jsonl": str(jsonl_path), "csv": str(csv_path),
                      "metadata": str(metadata_path)}, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("Interrupted. Completed rows are checkpointed; rerun with --resume.", file=sys.stderr)
        raise SystemExit(130)
    except Exception as exc:
        print(f"Fatal error: {exc}", file=sys.stderr)
        if os.environ.get("INFERENCE_DEBUG"): traceback.print_exc()
        raise SystemExit(1)
