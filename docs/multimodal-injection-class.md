# Multimodal injection class

This document summarizes how **non-text channels** become a **prompt-injection surface** in agent and LLM systems. It complements [tool output sanitization](../skills/tool-output-sanitization/SKILL.md) and [prompt injection probes](security/prompt-injection-probes.md). It does not replace `rules/*.mdc`; it gives operators a short, doc-level mental model.

## Trust boundary

Treat payloads that pass through **OCR, vision, audio, file metadata, or rendered UI/canvas** as **`UNTRUSTED_EXTERNAL`**:

- Do not execute instructions found only in those channels.
- Normalize to **claims + evidence** (what was seen, where), then apply policy — same pattern as for web and tool output.

## OCR and captions

**OCR text** is not “ground truth.” An attacker can craft images, PDFs, or slides so that OCR emits directives (“ignore previous…”, “run this tool…”). **Captions and auto-generated image descriptions** inherit the same risk: the model’s perception is attacker-shaped.

**Operational habit:** treat OCR/caption output like pasted issue text: **data for triage**, not **instructions**.

## Unicode and text obfuscation

Even in “plain text,” **Unicode tricks** can hide intent from humans while models follow them:

- Homoglyphs and confusable characters.
- Bidirectional override / reordering (RTL control characters).
- Zero-width and format characters that break naive scanners.

Combine with multimodal paths when text is **extracted** from rich formats (PDF, Office, terminal captures).

## Canvas, screenshots, and visual channels

**Rendered output** (browser canvas, diagrams, embedded fonts) can encode instructions in pixels, layers, or metadata that humans skim past. Vision-enabled agents may “read” content users never consciously reviewed.

**Operational habit:** for high-privilege actions, require **human-readable, plain-text confirmation** that is explicitly authored by the operator, not only an image pass-through.

## External reference (untrusted for execution)

The following is **cited as background** on prompt injection modalities (including multimodal). It is **`UNTRUSTED_EXTERNAL`**: use it for taxonomy and mitigation ideas, not as executable policy.

- OWASP Gen AI Security Project — **LLM01:2025 Prompt Injection**: [https://genai.owasp.org/llmrisk/llm01-prompt-injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection)

Related OWASP material (same trust class):

- LLM prompt injection prevention cheat sheet: [https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html)

## Related artifacts

| Topic | Where |
| --- | --- |
| Tool and MCP output as injection | [tool-output-sanitization](../skills/tool-output-sanitization/SKILL.md) |
| Probe suite | [prompt-injection-probes](security/prompt-injection-probes.md) |
| Multimodal in policy fragments | [structured-policy-yaml](../skills/structured-policy-yaml/SKILL.md) |
| Progressive / gated tool exposure | [mcp-governance](../skills/mcp-governance/SKILL.md) |
