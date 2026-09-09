"""
LLM-based Bloom's Taxonomy classifier for learner questions to an AI coach.

Classifies each question into one of the six levels of the revised Bloom's
Taxonomy (Remember, Understand, Apply, Analyze, Evaluate, Create), using
GPT-5-mini via the OpenAI Responses API.

Expected input CSV columns:
    - A unique identifier column (any name; row order is used internally,
      so this is for your own bookkeeping, not required by this script)
    - Skill        (required)  -- the AI course topic/skill for the question
    - Question     (required)  -- the question text to classify
    - Description  (optional)  -- a short skill description used as extra
                                   context. If this column is absent, the
                                   script prints a warning and proceeds with
                                   skill-name-only classification.

Usage:
    export OPENAI_API_KEY=sk-...
    ./run_classify.sh --input questions.csv --output results.csv

    (or directly: python3 src/classify.py --input ... --output ...)

The prompt sent to the model is stored separately at
prompts/bloom_taxonomy_prompt.txt, not embedded in this script, so it can
be inspected or modified independently of the code.

See README.md for full details.
"""

import argparse
import json
import sys
import time
from pathlib import Path

import pandas as pd
from openai import OpenAI
from tqdm import tqdm

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "bloom_taxonomy_prompt.txt"
QUESTIONS_PLACEHOLDER = "<<<QUESTIONS_JSON>>>"

REQUIRED_COLUMNS = ["Skill", "Question"]
OPTIONAL_COLUMNS = ["Description"]


def load_prompt_template():
    if not PROMPT_PATH.exists():
        print(f"ERROR: prompt file not found at {PROMPT_PATH}", file=sys.stderr)
        sys.exit(1)
    return PROMPT_PATH.read_text()


def check_columns(df):
    """Validates required columns are present and flags absent optional ones.
    This is the explicit version of what the original notebook did silently
    via row.get(..., default) -- same fallback behavior, but now visible to
    the person running it."""
    missing_required = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_required:
        print(f"ERROR: input is missing required column(s): {missing_required}", file=sys.stderr)
        print(f"Required columns: {REQUIRED_COLUMNS}", file=sys.stderr)
        sys.exit(1)

    for col in OPTIONAL_COLUMNS:
        if col not in df.columns:
            print(f"NOTE: optional column '{col}' not found in input. "
                  f"Proceeding with skill-name-only classification "
                  f"(no skill description will be supplied to the model).")


def build_questions_batch(batch_df):
    items = []
    for _, row in batch_df.iterrows():
        item = {
            "id": int(row["_row_id"]),
            "skill": str(row.get("Skill", "Artificial Intelligence")),
            "description": str(row.get("Description", "")),
            "question": str(row["Question"]),
        }
        items.append(item)
    return json.dumps(items, ensure_ascii=False, indent=2)


def classify_batch(client, batch_df, model, prompt_template):
    questions_json = build_questions_batch(batch_df)
    prompt = prompt_template.replace(QUESTIONS_PLACEHOLDER, questions_json)

    response = client.responses.create(model=model, input=prompt)
    text = response.output_text.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)


def run(input_path, output_path, batch_size, model, sleep_seconds):
    prompt_template = load_prompt_template()
    df = pd.read_csv(input_path)
    check_columns(df)

    client = OpenAI()  # reads OPENAI_API_KEY from the environment

    df = df.copy()
    df["_row_id"] = range(len(df))
    all_results = []

    for start in tqdm(range(0, len(df), batch_size), desc="Classifying batches"):
        batch_df = df.iloc[start:start + batch_size]

        try:
            batch_results = classify_batch(client, batch_df, model, prompt_template)
        except Exception as e:
            print(f"WARNING: batch starting at row {start} failed ({e}); "
                  f"recording as null for this batch.", file=sys.stderr)
            batch_results = []
            for _, row in batch_df.iterrows():
                batch_results.append({
                    "id": int(row["_row_id"]),
                    "level": None,
                    "subprocess": None,
                    "group": None,
                    "confidence": None,
                    "reasoning": str(e),
                })

        all_results.extend(batch_results)
        time.sleep(sleep_seconds)

    results_df = pd.DataFrame(all_results)
    result_df = df.merge(results_df, left_on="_row_id", right_on="id", how="left")
    result_df = result_df.drop(columns=["_row_id", "id"], errors="ignore")

    result_df.to_csv(output_path, index=False)
    print(f"\nSaved {len(result_df)} classified questions to {output_path}")

    n_failed = result_df["level"].isna().sum()
    if n_failed > 0:
        print(f"WARNING: {n_failed} questions failed classification (see 'reasoning' column for error details).")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", required=True, help="Path to input CSV")
    ap.add_argument("--output", required=True, help="Path to write output CSV")
    ap.add_argument("--batch-size", type=int, default=50)
    ap.add_argument("--model", default="gpt-5-mini")
    ap.add_argument("--sleep", type=float, default=0.5, help="Seconds to pause between batches (rate-limit courtesy)")
    args = ap.parse_args()

    run(args.input, args.output, args.batch_size, args.model, args.sleep)
