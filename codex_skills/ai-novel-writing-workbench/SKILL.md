---
name: ai-novel-writing-workbench
description: Use when developing this AI novel writing app from open-source product research, distilling GitHub projects into safe writing Skills, improving sourcebook/scene beats/prompt builder/continuity workflows, or checking license-safe reuse boundaries.
---

# AI Novel Writing Workbench

## Workflow

1. Start from product patterns, not source-code copying. Record project URL, license, reusable level, useful workflow, and risk note before implementation.
2. Convert research into application Skills with this shape: name, category, summary, instruction, use_cases, risk_note.
3. Prefer writing-experience improvements: sourcebook context, scene beats, prompt builder, continuity guard, and style cards.
4. Keep the chapter editor dominant. Put heavy management in settings windows or drawers, and keep chapter-mode helpers low-noise.
5. If license is missing or unclear, mark the source `pattern_only` and do not reuse code.

## References

- For the current project pool, read `references/github_research_matrix.md`.
- For reusable UX and prompt patterns, read `references/writing_experience_patterns.md`.
- Before any code-level reuse, read `references/license_checklist.md`.

## Implementation Rules

- Do not change core novel data tables unless an additive migration is enough.
- Preserve existing book/volume/chapter flows and packaged exe compatibility.
- Generated Skills must be abstract constraints, not imitation instructions for a specific author or project.
- Any GitHub-derived source needs attribution metadata in the app before it can influence generation.
