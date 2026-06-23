# Replay and redaction fixtures (vision)

This doc defines how **evals and harnesses** should store **replayable fixtures**: transcripts, repo snapshots, and **redacted** artifacts so runs are comparable and safe (pairs with [eval pipeline vision](eval-pipeline-vision.md)).

Evidence norms for any published result: [evidence-first acceptance](evidence-first-acceptance.md). Telemetry shape: [agent telemetry contract](agent-telemetry-contract.md).

## Why fixtures

- **Determinism-ish:** same prompt + pinned policy + frozen model should minimize surprise variance.
- **Safety:** exercises must not embed real keys, customer data, or private URLs.
- **Debugging:** failure triage without reproducing the entire live session.

## Fixture bundle layout (suggested)

```
fixtures/
  <suite>/<case_id>/
    README.md              # intent, expected AC, allowed tools
    user_prompt.md         # redacted natural language request
    policy_sha.txt         # expected commit or bundle hash
    workspace_manifest.json# list of files + hashes (small synthetic tree)
    transcript.jsonl       # optional: ordered tool/model messages (redacted)
    expected/              # optional golden outputs (diffs, reports)
```

Paths are illustrative; repos may nest under `benchmarks/` or `scripts/evals/`.

## Redaction rules

| Class | Action |
| --- | --- |
| API keys / tokens | Replace with `sk-test-FAKE...` style placeholders + catalog in `README.md` |
| Emails / phone / PII | Synthetic substitutions; map in a private table **outside** git if needed |
| Internal hostnames | `internal.example` unless trademark concerns |
| Large tool outputs | Store hash + byte length; truncate body in committed fixtures |
| Binary blobs | Exclude or replace with generated minimal files |

Redaction MUST be **lossy-by-design** for secrets; when in doubt, regenerate the fixture from a sanitized source.

## Replay modes

| Mode | Behavior |
| --- | --- |
| **Full replay** | Re-run model + tools against copied workspace (slow, most faithful) |
| **Tool stub replay** | Inject recorded tool outputs; model still runs (tests policy adherence) |
| **Static replay** | Lint transcript structure only (fast, limited signal) |

Declare which mode a suite uses in the suite manifest so scores are comparable.

## Injection and adversarial cases

Adversarial prompts belong in dedicated cases with labels matching [prompt injection probes](security/prompt-injection-probes.md). Expected behavior is **enumerated** (e.g. `must_refuse`, `must_quarantine`), not vague “should be safe.”

## Governance

- Fixture PRs need **owner review** for new UNTRUSTED_EXTERNAL samples.
- Link each case to a **branch_id** convention if it mirrors multi-agent DAG tests ([DAG and branch dependencies](dag-branch-dependencies.md)).

## CI hook sketch

On PR: verify manifests parse, hashes match extracted workspace tarballs, and **no** high-entropy secret patterns match (regex allowlist for known fakes).
