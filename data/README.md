# Data

This directory contains the labeled, assignment-designed category data referenced in the paper: 357 questions across 49 students, drawn from Part 1 of the course lab assignment, with true assignment-designed categories (basic, complex, critical, creative) alongside predictions from each classifier discussed in the paper (BERT baseline, LLM skill-only, LLM skill+description).





## Consent and Ethics



Only data from students who provided explicit consent for their course interactions and assignment submissions to be used for research is included, in accordance with Institutional Review Board (IRB)-approved protocols. Non-consenting students' data has been excluded entirely. No personally identifying information (names, emails, student IDs) is included; Uniquekey is an anonymized identifier with no connection to any student-identifying record outside this dataset.



Filename: eaai2027\_AI\_questions\_cogn\_catg\_blooms.csv



## Column dictionary

|Column|Description|
|-|-|
|`Uniquekey`|Anonymized unique identifier for the question.|
|`category`|**Ground truth.** The cognitive category (`basic`, `complex`, `critical`, `creative`) the assignment instructed the student to target when writing this question. Reflects assignment-designed intent, not an independently verified assessment of the question's actual cognitive complexity.|
|`matched\_chat\_text`|The canonical question text used for classification. Extracted questions from student PDF submissions were fuzzy-matched (70% similarity threshold) against the AI coach's interaction logs; this column holds the cleaner, log-derived text used in place of the PDF-extracted version, which is occasionally corrupted by formatting artifacts.|
|`Skill`|The procedural AI/course skill or topic the question concerns (e.g., "Planning," "Case-Based Reasoning," "Version Spaces").|
|`pred\_val\_bert`|Predicted Bloom's Taxonomy level from the fine-tuned BERT baseline (Maiti and Goel 2025).|
|`pred\_val\_llm\_skill`|Predicted Bloom's Taxonomy level from the zero-shot LLM classifier, supplied with the skill name only (no description).|
|`pred\_val\_llm\_skill\_desc`|Predicted Bloom's Taxonomy level from the zero-shot LLM classifier, supplied with both skill name and a short skill description. This is the paper's primary LLM configuration.|
|`subprocess`|The specific cognitive sub-process within the predicted level (e.g., "Critiquing" under Evaluate). Corresponds to the `pred\_val\_llm\_skill\_desc` classification — see note below.|
|`group`|Coarser cognitive-demand tier derived deterministically from the predicted level: `lower\_order` (Remember/Understand), `mid\_order` (Apply/Analyze), or `higher\_order` (Evaluate/Create). Corresponds to `pred\_val\_llm\_skill\_desc` — see note below.|
|`confidence`|The LLM classifier's self-reported confidence (`high`, `medium`, `low`) for its `pred\_val\_llm\_skill\_desc` classification.|
|`reasoning`|One-sentence natural-language justification for the `pred\_val\_llm\_skill\_desc` classification.|

## 

## Bloom's level → assignment category mapping

For reference, RQ1/RQ2 compare the six-level Bloom's Taxonomy predictions above against the four-category assignment scheme (`category` column) as follows:

|Bloom's Taxonomy level|Assignment category|
|-|-|
|Remember, Understand|basic|
|Apply, Analyze|complex|
|Evaluate|critical|
|Create|creative|



This mapping was validated for robustness via a partial-credit sensitivity analysis described in the paper; results differed by less than 0.03 across all classifiers and metrics under the primary mapping reported.



## Known limitations



**Ground truth reflects assignment intent, not verified execution.** A student instructed to write a "critical" question may, in practice,
produce something that reads closer to "complex." See the paper's Methodology ("Ground truth and its scope") and Limitations sections for full discussion.

