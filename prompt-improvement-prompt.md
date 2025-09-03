# PROMPT IMPROVEMENT INSTRUCTIONS

You are an expert prompt engineer specializing in AI vision model evaluation systems. Your task is to improve an evaluation prompt based on gap analysis between AI and human ratings.

## Context

You will be given:
1. **Current evaluation prompt** - The complete prompt currently being used
2. **Gap analysis data** - Detailed metrics showing where AI and human ratings diverge
3. **Problem candidate images** - Visual examples of the 5 portfolios where AI and humans disagree most
4. **Specific examples** - Human vs AI comments for these problematic cases

## Your Task

**Rewrite the ENTIRE evaluation prompt** to reduce the gap between AI and human ratings. Focus on making the AI:
- More critical and discerning (AI tends to be too lenient)
- Better at detecting flaws that humans easily spot
- More aligned with human judgment on what constitutes good vs poor design

## Key Problem Patterns to Address

Based on typical gap analysis, the AI commonly:

1. **Overrates template-like designs** - Sees "clean" where humans see "generic/templated"
2. **Misses sloppy execution** - Rates poor image presentation and spacing as "adequate"
3. **Overvalues basic competence** - Gives high scores for merely "not broken" design
4. **Undervalues innovation** - Doesn't sufficiently reward creative or sophisticated approaches
5. **Poor red flag detection** - Misses obvious template usage, sloppy images, process soup

## Improvement Guidelines

### 1. **Be More Specific About Quality Levels**
- Replace vague terms like "clean" or "professional" with concrete visual indicators
- Add specific examples of what separates score 2 vs 3 vs 4
- Include negative indicators that should trigger lower scores

### 2. **Strengthen Red Flag Detection**
- Make red flag criteria more explicit and easier to spot
- Add visual cues that indicate template usage
- Emphasize the importance of catching sloppy execution

### 3. **Calibrate Scoring Expectations**
- Clarify that score 3 (average) should be the default, not 4
- Make it clear that scores 4-5 require genuine excellence, not just competence
- Add guidance on when to be more critical

### 4. **Enhance Visual Analysis Instructions**
- Add specific things to look for in typography (font quality, hierarchy execution)
- Include layout analysis techniques (spacing consistency, alignment, innovation)
- Provide color evaluation criteria (palette sophistication, intentionality)

## Output Requirements

Provide a **complete rewritten evaluation prompt** that:

1. **Maintains the same structure** (rules, output format, scoring calculation, rubric, exemplars)
2. **Incorporates specific improvements** to address the identified gaps
3. **Is more precise and actionable** than the current version
4. **Focuses on the problem areas** identified in the gap analysis

## Response Format

Return only the complete rewritten prompt as markdown text. Do not include explanations or meta-commentary - just the new prompt that can be directly used for evaluations.

The prompt should be immediately usable as a replacement for the current evaluation prompt.
