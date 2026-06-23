---
name: prompt-creator
description: Create and optimize LLM prompts (system prompts, user prompts, agent instructions, few-shot pipelines). Use when writing prompts for Claude, GPT, Gemini, or any LLM — especially when output quality matters, prompts will run at scale, or the user is building an AI product. Covers prompt architecture, technique selection, model-specific tuning, and failure diagnosis.
---

## Mindset

Before writing a single word, ask yourself:

1. **What is the ONE job?** Every prompt should have exactly one clear objective. Two jobs = two prompts.
2. **Who consumes the output?** Human (optimize readability) vs LLM (optimize parseability with XML/JSON) vs API (optimize structure).
3. **What does failure look like?** Design the prompt to make the most common failure mode impossible.

## Technique Selection — Decision Tree

Don't pick techniques by habit. Pick by task characteristics:

| Task signal | Technique | Why |
|-------------|-----------|-----|
| Output format is critical | Few-shot examples (2-3 pairs) | Examples communicate format better than 100 words of description |
| Multiple valid approaches exist | Extended thinking / CoT | Forces evaluation before commitment |
| Output must be exactly X format | Prefill (Claude) or JSON mode (GPT) | Eliminates preamble, forces structure |
| Task has subtle edge cases | Boundary examples in few-shot | Show the tricky cases, not the obvious ones |
| Complex multi-step reasoning | Decompose into sequential prompts | One complex prompt < two simple prompts chained |
| Output quality varies wildly | Add rubric / evaluation criteria | Model self-calibrates against explicit standards |
| Model keeps ignoring instructions | Move constraint to system prompt + repeat in user | Dual-placement beats single placement |

## Prompt Architecture — What Goes Where

This is the #1 thing people get wrong. Placement matters more than wording:

```
SYSTEM PROMPT (persistent identity layer)
├── Role + expertise domain (1-2 sentences max)
├── Hard constraints (NEVER / ALWAYS rules)
├── Output format defaults
└── Tone / style baseline
    ↕ DO NOT put task-specific instructions here

USER MESSAGE (task layer)
├── Context the model needs for THIS task
├── The specific objective
├── Input data / content to process
├── Output format if different from default
└── Edge cases specific to this input

ASSISTANT PREFILL (output steering — Claude only)
├── Force JSON: `{"result":`
├── Force list: `1.`
└── Force language: Start with target language text
```

**Critical rule**: System prompts should be STABLE across conversations. If you're changing it per request, you're putting task instructions in the wrong layer.

## Model-Specific Differences That Actually Matter

| Dimension | Claude | GPT | Gemini |
|-----------|--------|-----|--------|
| Structure | XML tags (`<context>`, `<task>`) — trained on them | Markdown headers + numbered lists | Markdown, tolerates XML |
| Constraint framing | Positive framing works better ("Write in plain language" > "Don't use jargon") | Negative constraints work fine | Either works |
| Format enforcement | Prefill the assistant response | `response_format: { type: "json_object" }` | System instruction + example |
| Long instructions | Handles very long system prompts well (200K context) | Degrades past ~4K system prompt | Good with long context |
| Extended thinking | `thinking` blocks, trigger with "Thoroughly analyze..." | Not available natively | "Think step by step" in prompt |
| Tool calling | `inputSchema`/`outputSchema` (MCP-aligned) | `parameters` (JSON Schema) | `function_declarations` |

## NEVER

- **NEVER** put role-play AND constraints AND format AND examples AND CoT all in one prompt — pick 2-3 techniques max. Kitchen-sink prompts confuse the model.
- **NEVER** describe format in words when you can show an example. "Output a JSON object with keys name, age, and score" < showing `{"name": "Alice", "age": 30, "score": 95}`.
- **NEVER** use vague hedging: "try to", "maybe", "generally", "if possible". These give the model permission to skip the instruction.
- **NEVER** add a role that contradicts the task. "You are a friendly assistant" + "Respond with only JSON, no prose" = conflict.
- **NEVER** ask the model to "not think about X" — it focuses attention on X. Reframe positively.
- **NEVER** use examples that all look the same — include edge cases. If all 3 examples are happy-path, the model only learns the happy path.
- **NEVER** change prompt AND model AND temperature simultaneously when debugging — change one variable at a time.

## Prompt Failure Diagnosis

When a prompt produces bad output, diagnose before rewriting:

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| Model ignores an instruction | Instruction buried in long text | Move to system prompt or add "CRITICAL:" prefix |
| Output format is wrong | No example of desired format | Add 1-2 concrete examples |
| Model hallucinates facts | No grounding data provided | Add `<context>` with source material |
| Output too verbose | No length constraint | Add "Maximum N sentences/lines/tokens" |
| Model hedges ("I think maybe...") | Role is too passive | Set confident role: "You are an expert who gives direct answers" |
| Inconsistent quality across runs | Temperature too high or prompt is ambiguous | Lower temperature AND add specificity |
| Model adds unsolicited caveats | No instruction about caveats | Add "Do not add disclaimers or caveats" |
| Wrong level of detail | No audience specified | Add "Write for [audience]" |

## Workflow

1. **Ask** (use AskUserQuestion): purpose, target model, output consumer, failure tolerance
2. **Architect**: decide system vs user split, select 2-3 techniques from decision tree
3. **Draft**: write the prompt, starting with output format example
4. **NEVER test**: review against the NEVER list above
5. **Edge-case**: add 1-2 boundary examples that show tricky cases
6. **Ship**: deliver the prompt with a test suggestion ("Try it with this input: ...")

## References

**MANDATORY** — read before creating prompts for specific models:
- [references/anthropic-best-practices.md](references/anthropic-best-practices.md) — Claude-specific: XML, prefill, extended thinking, context management
- [references/openai-best-practices.md](references/openai-best-practices.md) — GPT-specific: JSON mode, function calling

**Load on demand:**
- [references/prompt-templates.md](references/prompt-templates.md) — Ready-to-adapt templates (analysis, transformation, generation, code review)
- [references/context-management.md](references/context-management.md) — Long-horizon tasks, state tracking, multi-session patterns
- [references/anti-patterns.md](references/anti-patterns.md) — Extended anti-pattern catalog with examples
