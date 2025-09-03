# Old Prompt Components (Archived)

These files were the original components that made up the evaluation prompt system before consolidation:

- `core-prompt.md`: The main evaluation instructions and rules
- `rubric.json`: The detailed scoring rubric for each dimension
- `examplars.json`: The exemplar portfolios with scores for calibration

**These files have been consolidated into a single `prompt.md` file in the project root.**

The old system used `PortfolioEvaluator.generate_prompt()` to assemble these components at runtime. The new system simply reads the complete prompt from `prompt.md`, making it much simpler to manage and edit.

Date archived: September 3, 2024
