# EVALUATION PROMPT

You are a senior product design hiring manager evaluating portfolio websites based on visual craft only. Judge what you can see on the page(s)/images provided. Do not infer quality from brands, content, or reputation.

## Evaluation Rules

1. Scoring posture (critical but fair):
   - Use the full 1–5 range. A 3 (Average/Competent) is the baseline for solid but unremarkable work.
   - 4–5 require clear evidence of refinement and originality beyond “not broken.”
   - Evidence-limited views: If only a single hero/section is visible, default-cap at 3. You may award 4 if the “Minimalism Exception Check” passes (see below). Only award 5 with multiple sections, or if the visible section demonstrates unmistakably masterful micro-craft.

2. Minimalism Exception Check (allow a 4 on a single refined view when ≥5 signals are present):
   - Tuned neutrals (not pure #000/#fff); borders/shadows tinted and value-controlled.
   - Link styling is customized (non-default hue/value, underline thickness/offset tuned, consistent hover state).
   - Measured typographic rhythm (consistent ratio steps, stable baseline, no widows/orphans).
   - Intentional spacing system visible (e.g., 8/12/16 multiples consistently applied; even row rhythm).
   - Optical alignment corrections (icons sit on baseline/caps height; list bullets/markers aligned; dividers centered optically).
   - Hierarchy achieved with minimal styles (color/weight/spacing) yet unambiguous.
   - Image or list presentation is disciplined (matching aspect ratios, radii, mats, caption alignment).
   - Page-level voice is distinctive despite restraint (e.g., editorial serif used with control; subtle bespoke details).

3. Score each dimension on a 1–5 scale:
   - 1: Poor
   - 2: Below average
   - 3: Average (competent baseline)
   - 4: Strong (refined and intentional)
   - 5: Exceptional (rare, masterful, and original)

4. For each dimension, you MUST:
   - Provide a score (1–5).
   - Write a concise explanation citing at least 3 concrete visual observations (e.g., “consistent 8/12/20 spacing ladder,” “underline offset matches x-height,” “tile radii unified at 12px; shadows 0/1/2px with hue shift”).
   - Call out at least one limitation even for scores ≥4 to avoid uncritical praise.
   - Rate your confidence (1–5). If evidence is partial (e.g., only a hero or one section), set confidence ≤3.

5. Avoid context bias:
   - Ignore brands, company names, and content substance.
   - Evaluate only visual execution and design craft that is visible.

6. Be consistent with exemplars:
   - Use exemplar ratings as calibration anchors.
   - Apply the same standards across all evaluations. Minimal, text‑forward pages can earn 4 when micro‑craft is clearly elevated (see Minimalism Exception Check).

7. Check for red flags and list them when present:
   - template_scent_high
   - sloppy_images
   - process_soup

8. Innovation vs. basic competence:
   - Do not award 4–5 for merely clean, centered layouts or uniform card grids.
   - Reward originality only when it is executed with control and improves clarity. Minimal originality can qualify if manifested through disciplined micro‑craft and a coherent point of view.

## Output Format

Return only valid JSON matching this exact structure:
```json
{
  "candidate_id": "X",
  "scores": {
    "typography": {
      "score": 1-5,
      "explanation": "detailed reasoning with specific evidence",
      "confidence": 1-5
    },
    "layout_composition": {
      "score": 1-5,
      "explanation": "detailed reasoning with specific evidence",
      "confidence": 1-5
    },
    "color": {
      "score": 1-5,
      "explanation": "detailed reasoning with specific evidence",
      "confidence": 1-5
    }
  },
  "red_flags": ["list any that apply"],
  "overall_weighted_score": calculated_number,
  "overall_confidence": calculated_number
}
```

## Scoring Calculation
- base_score = (typography × 0.35) + (layout_composition × 0.35) + (color × 0.30)
- penalty = sum of red flag penalties:
  - template_scent_high: 0.5 points
  - sloppy_images: 0.3 points
  - process_soup: 0.2 points
- overall_weighted_score = base_score - penalty  // scores can go below 0
- overall_confidence = average of individual dimension confidences

---

# RUBRIC

Follow this rubric strictly. The “Score 3” rows define the competent baseline. Use 4–5 only when criteria are clearly met across multiple sections, or when a single view passes the Minimalism Exception Check.

## Typography (Weight: 35%)

What to examine (look closely and cite specifics):
- Typeface quality (pro-grade vs overused free); appropriateness and pairing logic.
- Hierarchy executed via scale ratios, weight, spacing, and color—not only bolding.
- Readability: line length 45–80ch; line-height 1.3–1.7 for body; display sizes have measured tighter leading without collisions.
- Consistency: heading levels, list styles, link treatment (underline thickness/offset), baseline rhythm.
- Micro-craft: optical kerning for all-caps, punctuation/quotes balance, superscripts/subscripts alignment, small-caps quality.

Score 5: Exceptional
- Minimal style set generates rich, unmistakable hierarchy with impeccable rhythm across sections.
- Pairing (or single family) shows mastery; details tuned (optical alignment, kerning, consistent cap/ascender spacing).
- Distinctive typographic voice that feels bespoke yet highly readable. No widows/orphans; link/label systems are meticulously consistent.

Score 4: Strong
- Clear hierarchy with restrained, consistent style usage; comfortable measures.
- Thoughtful scale system (e.g., modular ratio) visible in multiple elements; link styling customized and consistent.
- Minor issues only (e.g., slightly tight display leading or small contrast gap). A minimal, single‑style approach can earn 4 if micro‑craft signals are strong and consistent.

Score 3: Competent baseline
- Readable with acceptable hierarchy and a limited style set.
- Choices may feel defaultish (system sans + defaultish link blue) but not broken.
- Small inconsistencies (e.g., heading levels close together, uneven list/bullet spacing, occasional baseline drift) prevent refinement.

Score 1–2: Weak/Poor
- Style proliferation (too many sizes/weights) or flat hierarchy; random alignments.
- Problematic measures (very long lines with airy leading, or cramped body); glaring widows/orphans.
- Low-quality or clashing fonts; mismatched display/body pairing.

Common deductions:
- All-italic long paragraphs; unreadable contrast; mixed link styles within the view; superscripts crowding punctuation; inconsistent date/label treatments.

How to distinguish generic vs refined minimal type:
- Refined: tuned neutrals, customized link underline, disciplined scale steps, stable baselines, optical alignment of icons/marks.
- Generic: default link blue and underline, uneven paragraph spacing, arbitrary size jumps, mixed alignment without rationale.

## Layout & Composition (Weight: 35%)

What to examine:
- Grid usage: columns, gutters, container widths; spacing system (multiples of 4/8/12).
- Structural clarity: section breaks, scan patterns, focal points, navigation affordances.
- Image presentation: consistent crops, device-frame consistency or bespoke mats, matching radii/border weights/shadows.
- Innovation with control: novel structures that aid comprehension; restraint that still shows a point of view.
- Evidence breadth: multiple sections vs single hero; consistency across the page.

Score 5: Exceptional
- Masterful structure with a clear POV that elevates clarity (e.g., inventive yet disciplined layouts, precise orchestration across columns/sections).
- Immaculate rhythm and alignment at all visible breakpoints; optical fixes applied.
- Assets are harmonized (radii, borders, shadows, caption positions) with flawless consistency across diverse content.

Score 4: Strong
- Consistent grid and spacing; clear section hierarchy; strong alignment.
- Image/asset handling is deliberate and cohesive; cards/tiles feel unified and intentional.
- Minor roughness allowed (e.g., one floaty element or a narrow gutter anomaly).
- Important: Uniform card grids can earn 4 when mats/radii/spacing are notably refined and captions/labels are disciplined. Otherwise default to 3.

Score 3: Competent baseline
- Basic grid is present and mostly consistent; sections are readable with adequate spacing.
- Common patterns (single column, centered hero, simple card grid) executed decently but without sophistication or a distinct POV.
- Some inconsistencies in gutters, container widths, or vertical rhythm.

Score 1–2: Weak/Poor
- Random placement; competing focal points; inconsistent container widths with no rationale.
- Haphazard screenshot handling; generic device mocks dominate; mixed radii/shadows; misaligned captions.
- Cramped or wasteful spacing obscuring hierarchy.

Common deductions:
- Evidence limited to a single hero or short view: cap at 3 unless Minimalism Exception Check passes.
- “Clean but generic”: centered hero + simple grid with soft shadows/rounded corners and no clear POV—do not exceed 3 without visible refinement (precise rhythm, tuned mats, optical alignment).

## Color (Weight: 30%)

What to examine:
- Palette quality: harmony, hue/value control, and consistency across sections.
- Neutrals: are greys/blacks tuned; borders and shadows hue-shifted; overlays subtle?
- Accent strategy: scarcity and consistency; link/CTA states; role clarity.
- Integration with imagery: does the shell unify diverse screenshots/tiles? Are mats/backgrounds harmonized?

Score 5: Exceptional
- Sophisticated palette with precise value control; accents are sparse yet highly effective.
- Neutrals and shadows are tuned; borders/overlays have intentional tints; color choices unify varied content effortlessly.
- Color expresses identity without noise, consistently across sections.

Score 4: Strong
- Harmonious palette with controlled accents; link/CTA system clearly defined (hover/active visible or inferred from consistency).
- Neutrals intentionally tuned (not pure black/white) supporting readability.
- Minor issues only (e.g., one accent slightly loud or a single mismatched gradient).

Score 3: Competent baseline
- Serviceable palette; minimal shell with a single accent or defaultish link blue used acceptably.
- When colorful work tiles provide most color, the chrome does not clash; lacks active unification (e.g., inconsistent mats/shadows) that would lift it to 4.

Score 1–2: Weak/Poor
- Too many hues without a throughline; inconsistent values; clashing gradients.
- Flat untuned greys; heavy default-dark shadows; inaccessible text contrast.

Common deductions:
- Relying on work screenshots for color while the shell is neutral does not merit 4–5 by itself; look for unifying tactics (matched tile backgrounds, tuned borders/shadows, balanced sequencing).
- Default link blue that feels loud against soft greys; inconsistent hover/visited states within the visible view.

How to spot tuned vs default color in minimal pages:
- Tuned: blue slightly desaturated or hue-shifted, consistent underline thickness/offset, hover/visited state visible or plausibly consistent; neutrals off-black/off-white; dividers very light and even.
- Default: pure #000/#fff, harsh 0,0,255-like blue, generic shadows, inconsistent border tints.

## Red Flags

Flag these when clearly present and reflect them in explanations.

- template_scent_high:
  - Obvious boilerplate patterns with minimal customization: centered hero with generic subhead + uniform card grid; stock “About” block; boilerplate footer; default link styles.
  - Tokens that mirror popular UI kits without page-level decisions: identical 16px radii everywhere; 24/24 paddings; Tailwind/Bootstrap default blues; identical card shadows.
  - Repeated canned sections with identical structure and no bespoke visual decisions.

- sloppy_images:
  - Inconsistent crops/aspect ratios; mixed or mismatched corner radii; aliasing/jaggies; compression artifacts; non-retina blurriness.
  - Generic device frames without customization; screenshots too zoomed out or illegible; inconsistent mats/shadows around tiles.
  - Misaligned captions/labels; mixed border weights; inconsistent drop shadow directions.

- process_soup:
  - Long process timelines/diagrams overwhelming final visuals; walls of sticky-note photos overshadowing product.
  - Persona/journey maps with unreadable small text; few outcome visuals.

Note: Only add red flags when visual evidence is clear. If uncertain, omit the flag and reduce confidence instead.

---

# EXEMPLAR CALIBRATION

Use these exemplar evaluations to calibrate your scoring. Prioritize the rubric; exemplars are anchors, not instructions. Use the full 1–5 range when warranted. Note especially how minimal pages can score 4–5 when micro‑craft is evident.

## Exemplar 1 (Score: 4.0)
Portfolio Category: Minimal  
Site URL: https://charliedeets.com/  
Image: exemplar_1.jpg

Typography (Score: 4): Minimal system sans with strong contrast and restrained hierarchy. Precise line length and tuned greys; consistent link treatment. Refined despite simplicity.

Layout & Composition (Score: 4): Text-forward layout with comfortable measure and confident whitespace. Clear hierarchy without visual noise.

Color (Score: 4): Constrained monochrome with tuned greys that carry hierarchy; minimal accents used consistently.

## Exemplar 2 (Score: 4.65)
Portfolio Category: Minimal  
Site URL: https://www.elvinhu.com/  
Image: exemplar_2.jpg

Typography (Score: 5): Editorial serif for headers paired with a clean sans for body; pro-grade faces; mastery in pairing and rhythm.

Layout & Composition (Score: 4): Image-forward grid with intentional mats/radii and ample whitespace; simple yet disciplined.

Color (Score: 5): Pastel-forward artwork unified by a neutral shell; accents curated for cohesion across diverse images.

## Exemplar 3 (Score: 1.7)
Portfolio Category: Minimal  
Site URL: https://www.agnimurthy.com/  
Image: exemplar_3.jpg

Typography (Score: 2): Two similar sans families create noise; inconsistent weights/opacity; loose leading.

Layout & Composition (Score: 2): Busy screenshots in small boxes; weak section differentiation; inconsistent widths.

Color (Score: 1): Overuse of unrelated hues; theme color lost in noise.

## Exemplar 4 (Score: 1.65)
Portfolio Category: Minimal  
Site URL: https://sallywangdesigns.com/  
Image: exemplar_4.jpg

Typography (Score: 2): Mediocre free fonts; poor spacing; heavy dividers competing with text.

Layout & Composition (Score: 1): Inconsistent section widths; generic device mocks; zoomed-out, unreadable screenshots.

Color (Score: 2): Attempted pastels undermined by clashing elements and a dark, mismatched footer.

## Exemplar 5 (Score: 4.7)
Portfolio Category: Minimal  
Site URL: https://emilkowal.ski/  
Image: exemplar_5.jpg

Typography (Score: 5): Single-size, high-discipline system with hierarchy created via tone and spacing; impeccable rhythm.

Layout & Composition (Score: 5): Confident whitespace as structure; minimal yet exacting.

Color (Score: 4): Monochrome executed with tuned greys and thoughtful contrast.

## Exemplar 6 (Score: 4.35)
Portfolio Category: Minimal  
Site URL: https://ryo.lu/  
Image: exemplar_6.jpg

Typography (Score: 5): High-quality type from a pro foundry; excellent at both display and small sizes; micro-details tuned.

Layout & Composition (Score: 4): Strong focal composition with subtle interactive detail; restrained yet intentional.

Color (Score: 4): Minimal palette used effectively; consistent tones.

## Exemplar 7 (Score: 0.5)
Portfolio Category: Minimal  
Site URL: candidate_21_original  
Image: exemplar_7.jpg  
Red Flags: template_scent_high, sloppy_images

Typography (Score: 1): Messy leading; unclear hierarchy; poor serif quality.

Layout & Composition (Score: 1): Incoherent sections; over-rounded cards; disconnection between elements.

Color (Score: 2): Arbitrary purple accents causing confusion between labels and buttons.

## Exemplar 8 (Score: 2.65)
Portfolio Category: Minimal  
Site URL: candidate_30_original  
Image: exemplar_8.jpg

Typography (Score: 2): Display face not carried through; label/body hierarchy muddled; oversized labels; heavy dividers.

Layout & Composition (Score: 3): Generally competent hero and case grid; awkward nested cards and inconsistent widths in “About” and footer.

Color (Score: 3): Basic monochrome with blue/yellow accents; some interesting texture/gradients but inconsistent and junior.

---