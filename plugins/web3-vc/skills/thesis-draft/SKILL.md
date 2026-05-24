---
name: thesis-draft
description: "[Phase 1 stub] Composes sector-scan + unit-economics + onchain-flow outputs into a structured investment thesis document. Human-led — the skill structures and stress-tests; the conviction call belongs to the user. Not yet implemented in Phase 0."
---

# Thesis Draft (Phase 1 — NOT IMPLEMENTED)

## Status: STUB

This skill is scaffolded for design clarity but **not functional in Phase 0**. Invoking it will surface this notice.

## Phase 1 plan

### Design philosophy (read this first)

This skill is **deliberately human-led**. It does NOT generate investment opinions, conviction calls, or recommendations on its own. Its job is to:

1. **Compose** existing skill outputs (sector-scan, unit-economics, onchain-flow) into one coherent document scaffold
2. **Stress-test** the user's draft thesis by surfacing counter-evidence already in the data
3. **Structure** the user's notes into a defensible IC-memo-like format
4. **Track** prior thesis versions so the user can see how their view evolved

The user writes the thesis. The skill prevents the user from cherry-picking data.

### Inputs (planned)
- User-provided thesis statement (1–3 sentences, the core claim)
- Reference to relevant prior scan / fundamentals / onchain outputs (from `./scans/`, `./fundamentals/`, `./onchain/`)
- Optional: user's draft thesis paragraphs

### Workflow (planned)

#### Step 1: Thesis decomposition
Parse the user's thesis into:
- **Claim**: what the user is asserting will happen
- **Mechanism**: why it will happen
- **Time horizon**: when it should be visible
- **Falsifier**: what observation would prove the thesis wrong

If any of these four are missing, ask the user before proceeding. A thesis without a falsifier is not a thesis.

#### Step 2: Evidence aggregation
Pull from local artifact directories:
- `./scans/*` — relevant sector context
- `./fundamentals/*` — target protocol(s) economics
- `./onchain/*` — microstructure evidence

Cite each as a footnote in the output.

#### Step 3: Stress-test (this is the core value-add)
For each claim in the thesis, ask:
- What's the strongest counter-evidence in the aggregated data?
- What's an alternative explanation for the same evidence?
- What would a Paradigm / Variant / Multicoin partner ask?

Surface these explicitly in a "Stress-test" section. Do not soften them. The user's job is to address them or reject them.

#### Step 4: Output format (planned)

```markdown
# Thesis: {Title}
*Version: v{N} — {date}*

## Core claim
{user-provided, structured}

## Mechanism
{user-provided}

## Time horizon
{user-provided}

## Falsifier
{user-provided — what would prove this wrong}

## Evidence
- {claim 1} → supported by [scan-2026-05-20], [fundamentals-hyperliquid-2026-05-21]
- {claim 2} → ...

## Stress-test
- **Counter-evidence A**: {finding from aggregated data}
- **Counter-evidence B**: {finding}
- **Alternative explanation**: {alternative framing of the same evidence}
- **What a Paradigm partner would ask**: {anticipated question}

## Open questions
- {what the user needs to answer before going to conviction}

## Version history
- v1 (date): initial draft
- v2 (date): {what changed}
```

#### Step 5: Save
Write to `./theses/{slug}-v{N}.md`. Keep all versions — version diffs are the most important meta-signal of intellectual honesty.

### What this skill must NOT do
- Generate the original thesis claim
- Soften the stress-test section
- Recommend "buy" / "pass" / position sizing
- Pretend confidence the user hasn't earned

## Triggers

"thesis", "draft thesis", "investment memo", "stress-test thesis", "IC memo"
