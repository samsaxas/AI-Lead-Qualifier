#!/usr/bin/env python3
"""Evaluate the lead qualifier against the labeled test set.

Two modes (standard library only, no pip install needed):

  # 1) Offline keyword-rule baseline (no n8n, no API key)
  python eval/evaluate.py --baseline

  # 2) The real n8n workflow (n8n running, workflow active, Gemini credential set)
  python eval/evaluate.py --url http://localhost:5678/webhook/lead-intake --delay 4

The workflow is called with ?dry_run=true so no rows are written to Google Sheets and no
emails are sent while evaluating. Results are saved to results/<name>.json and printed
as a Markdown table you can paste into the README.
"""
import argparse
import csv
import json
import pathlib
import statistics
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import baseline_rules  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
LABELS = ["hot", "warm", "cold"]


def call_webhook(url: str, lead: dict, timeout: int):
    payload = json.dumps({k: lead[k] for k in ("lead_id", "name", "email", "source", "message")}).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = json.loads(resp.read().decode())
    return body, (time.perf_counter() - t0) * 1000


def metrics(y_true, y_pred):
    n = len(y_true)
    correct = sum(t == p for t, p in zip(y_true, y_pred))
    per_class, f1s = {}, []
    for c in LABELS:
        tp = sum(t == c and p == c for t, p in zip(y_true, y_pred))
        fp = sum(t != c and p == c for t, p in zip(y_true, y_pred))
        fn = sum(t == c and p != c for t, p in zip(y_true, y_pred))
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        per_class[c] = {"precision": prec, "recall": rec, "f1": f1, "support": tp + fn}
        f1s.append(f1)
    confusion = {t: {p: 0 for p in LABELS} for t in LABELS}
    for t, p in zip(y_true, y_pred):
        if t in confusion and p in confusion[t]:
            confusion[t][p] += 1
    return {"n": n, "accuracy": correct / n if n else 0.0, "macro_f1": sum(f1s) / len(f1s),
            "per_class": per_class, "confusion": confusion}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=str(ROOT / "data" / "leads_labeled.csv"))
    ap.add_argument("--url", help="n8n webhook URL (production URL ends in /webhook/lead-intake)")
    ap.add_argument("--baseline", action="store_true", help="run the offline keyword-rule baseline instead")
    ap.add_argument("--delay", type=float, default=2.0, help="seconds between calls (free API tiers rate-limit)")
    ap.add_argument("--timeout", type=int, default=60)
    ap.add_argument("--name", default=None, help="results file name (default: baseline or llm)")
    args = ap.parse_args()
    if not args.baseline and not args.url:
        ap.error("pass --baseline or --url")

    leads = list(csv.DictReader(open(args.csv, encoding="utf-8")))
    name = args.name or ("baseline" if args.baseline else "llm")
    y_true, y_pred, latencies, review, failures, rows = [], [], [], 0, 0, []

    for i, lead in enumerate(leads, 1):
        if args.baseline:
            out, ms = baseline_rules.classify(lead["message"]), 0.0
        else:
            try:
                sep = "&" if "?" in args.url else "?"
                out, ms = call_webhook(args.url + sep + "dry_run=true", lead, args.timeout)
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
                print(f"[{i}/{len(leads)}] {lead['lead_id']} FAILED: {e}")
                failures += 1
                out, ms = {"intent": "error"}, 0.0
            time.sleep(args.delay)
        pred = str(out.get("intent", "error")).lower()
        if out.get("needs_review"):
            review += 1
        y_true.append(lead["true_intent"])
        y_pred.append(pred)
        if not args.baseline and ms:
            latencies.append(ms)
        rows.append({"lead_id": lead["lead_id"], "true": lead["true_intent"], "pred": pred,
                     "score": out.get("score"), "reason": out.get("reason"), "ms": round(ms)})
        mark = "ok " if pred == lead["true_intent"] else "MISS"
        print(f"[{i:>2}/{len(leads)}] {mark} true={lead['true_intent']:<4} pred={pred:<5} {lead['message'][:60]}")

    m = metrics(y_true, y_pred)
    m.update({"name": name, "failures": failures, "needs_review": review,
              "hot_recall": m["per_class"]["hot"]["recall"]})
    if latencies:
        lat = sorted(latencies)
        m["latency_ms"] = {"median": statistics.median(lat),
                           "p95": lat[min(len(lat) - 1, int(0.95 * len(lat)))]}
    results_dir = ROOT / "results"
    results_dir.mkdir(exist_ok=True)
    (results_dir / f"{name}.json").write_text(json.dumps({"metrics": m, "rows": rows}, indent=2))

    print("\n=== RESULTS:", name, "===")
    print(f"| Method | n | Accuracy | Macro-F1 | Hot recall | Hot precision | Median latency |")
    print(f"|---|---|---|---|---|---|---|")
    lat_txt = f"{m['latency_ms']['median'] / 1000:.1f} s" if "latency_ms" in m else "n/a"
    print(f"| {name} | {m['n']} | {m['accuracy']:.1%} | {m['macro_f1']:.2f} | "
          f"{m['per_class']['hot']['recall']:.1%} | {m['per_class']['hot']['precision']:.1%} | {lat_txt} |")
    print("\nConfusion matrix (rows = true, columns = predicted):")
    print("        " + "  ".join(f"{c:>5}" for c in LABELS))
    for t in LABELS:
        print(f"{t:>6}  " + "  ".join(f"{m['confusion'][t][p]:>5}" for p in LABELS))
    if failures:
        print(f"\nWARNING: {failures} request(s) failed and are counted as wrong.")
    print(f"\nSaved results/{name}.json")


if __name__ == "__main__":
    main()
