# Bloom's Taxonomy LLM Classifier for Learner-AI Coach Interactions



Code and data supplement for our EAAI 2027 submission classifying the cognitive demand of learner questions posed to an AI coach, against the revised Bloom's Taxonomy, using a zero-shot LLM classifier.



This repository contains the classification pipeline described in the paper's Methodology section ("LLM Classifier Design").



## Repository structure

```
.
├── run\_classify.sh          # Shell entry point (checks setup, then runs classify.py)
├── src/
│   └── classify.py          # Classification pipeline
├── prompts/
│   └── bloom\_taxonomy\_prompt.txt   # The exact prompt sent to the model (plain text)
├── data/
│   └── README.md            # Description of released data (see below)
├── examples/
│   └── sample\_\*.csv         # Minimal example inputs (synthetic, for format reference only)
├── requirements.txt
└── README.md                # This file
```

## 

## Setup

```bash
pip install -r requirements.txt
export OPENAI\_API\_KEY=sk-...   # your own OpenAI API key
```

## 

## Usage

```bash
./run\_classify.sh --input your\_questions.csv --output results.csv
```

`run\_classify.sh` checks that `OPENAI\_API\_KEY` is set and that required
Python packages are installed (installing them from `requirements.txt`
if not), then runs the classifier. Run `./run\_classify.sh --help` to see
all options, or invoke `python3 src/classify.py` directly if you prefer.

### 

### Input format

Your input CSV must contain:

|Column|Required?|Description|
|-|-|-|
|`Skill`|Yes|The AI course topic/skill the question relates to|
|`Question`|Yes|The question text to classify|
|`Description`|No|A short skill description, used as extra context|



If the `Description` column is absent, the script detects this automatically and prints a warning, then proceeds with skill-name-only classification (equivalent to the paper's "LLM (skill)" condition rather than "LLM (skill+description)"). No manual configuration is needed to switch between the two conditions described in the paper, simply include or omit the `Description` column in your input file. Any additional columns in your input (e.g., a unique ID column) are preserved unchanged in the output.



### Output format

The output CSV contains all original input columns plus:

|Column|Description|
|-|-|
|`level`|Predicted Bloom's Taxonomy level (Remember/Understand/Apply/Analyze/Evaluate/Create)|
|`subprocess`|The specific cognitive sub-process within that level|
|`group`|Coarser tier: `lower\_order`, `mid\_order`, or `higher\_order`|
|`confidence`|Model's self-reported confidence: `high`, `medium`, or `low`|
|`reasoning`|One-sentence natural-language justification for the classification|

If a batch fails (e.g., due to a rate limit or malformed model output), affected rows will have `level` set to null and the error message recorded in `reasoning`; a summary warning is printed at the end of the run.



### Options

```
--batch-size   Number of questions per API call (default: 50)
--model        OpenAI model to use (default: gpt-5-mini)
--sleep        Seconds to pause between batches (default: 0.5)
```

## Data



The `data/` directory is reserved for the labeled, assignment-designed category data referenced in the paper (357 questions across 49 students, with true assignment-designed categories: basic, complex, critical, creative). This allows independent verification of the RQ1/RQ2 results reported in the paper. See `data/README.md` for the data dictionary once uploaded.



All released data has been anonymized in accordance with the IRB-approved protocol described in the paper's Methodology section; no personally identifying information is included.



## Relationship to the paper

* **Prompt design** (verbatim, unchanged from what generated the paper's reported results) is in `prompts/bloom\_taxonomy\_prompt.txt` — kept as
a separate plain-text file rather than embedded in code, so it can be read or modified independently.
* **Skill-only vs. skill+description conditions** (RQ2) correspond directly to running this script with an input CSV that omits vs. includes the `Description` column. The underlying prompt and code path are identical, per the paper's Methodology section.

