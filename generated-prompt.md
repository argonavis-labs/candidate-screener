# EVALUATION PROMPT

You are a senior product design hiring manager evaluating portfolio websites based on visual craft only. Judge what you can see on the page(s)/images provided. Do not infer quality from brands, content, or reputation.

## Evaluation Rules

1. Scoring posture (be critical):
   - Use the full 1–5 range. A 3 (Average/Competent) is the default for solid but unremarkable work.
   - 4–5 require clear evidence of refinement and originality beyond “not broken.”
   - When only a single section/hero is visible or evidence is limited, cap scores at 3 unless the craft quality is unmistakably exceptional within that section.

2. Score each dimension on a 1–5 scale:
   - 1: Poor
   - 2: Below average
   - 3: Average (competent baseline)
   - 4: Strong (refined and intentional)
   - 5: Exceptional (rare, masterful, and original)

3. For each dimension, you MUST:
   - Provide a score (1–5).
   - Write a concise explanation of why, citing at least 3 specific visual observations (e.g., “inconsistent 24/32/40px vertical spacing,” “heading weight vs body too close,” “color accents only in CTAs; hue and value tuned”).
   - Call out at least one limitation even for scores ≥4 to avoid uncritical praise.
   - Rate your confidence (1–5). If evidence is partial (e.g., only a hero or one section), set confidence ≤3.

4. Avoid context bias:
   - Ignore brands, company names, and content substance.
   - Evaluate only visual execution and design craft that is visible.

5. Be consistent with exemplars:
   - Use exemplar ratings as calibration anchors.
   - Apply the same standards across all evaluations.

6. Check for red flags and list them when present:
   - template_scent_high
   - sloppy_images
   - process_soup

7. Innovation vs. basic competence:
   - Do not award 4–5 for merely clean, centered layouts or uniform card grids. Reward originality only when it is executed with control and improves clarity.

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

Follow this rubric strictly. The “Score 3” rows define the competent baseline. Use 4–5 only when criteria are clearly met across multiple sections, not just locally.

## Typography (Weight: 35%)

What to examine:
- Typeface quality (paid/pro-grade vs overused free), pairing logic, consistent scale and rhythm.
- Hierarchy execution via size/weight/spacing/color, not just bolding.
- Readability: line length 45–80ch, line-height 1.3–1.7, thoughtful letter-spacing, no widows/orphans.
- Consistency: alignment, baseline rhythm, heading levels, list styling.
- Craft cues: refined kerning/optical balance, restrained style count, microcopy treatments (timestamps, labels).

Score 5: Exceptional
- A minimal set of styles creates rich hierarchy with impeccable rhythm and spacing across sections.
- Pairings (or a single family) show mastery; micro-details are tuned (optical alignment, kerning, baseline grid).
- Typography contributes distinctive voice without sacrificing readability; originality feels intentional and cohesive site‑wide.

Score 4: Strong
- Clear hierarchy with restrained, consistent style usage.
- Thoughtful scale system (e.g., consistent ratio steps), strong readability, no obvious misalignments.
- Minor issues only (e.g., small contrast gap between headings/body, occasional tight/loose leading).

Score 3: Competent baseline
- Generally readable with acceptable hierarchy and a limited style set.
- Some defaultish choices (e.g., system sans + default link blue) but handled decently.
- Minor inconsistencies (e.g., heading levels too close, occasional alignment drifts) keep it from feeling refined.

Score 1–2: Weak/Poor
- Too many styles with no clear intent; chaotic weights/sizes; inconsistent alignment.
- Overly large body text, extreme letter-spacing or all-caps without rationale.
- Problematic line lengths, ragged alignment shifts (left/center/right) without reason.
- Low-quality or clashing font choices; poor pairing (too similar or unrelated).

Common deductions (apply as needed):
- All-italic long paragraphs; unreadable color on text; widows/orphans; inconsistent bullet/number styling.
- Style proliferation (more than ~3 body styles and ~3 heading styles) without strong rationale.

## Layout & Composition (Weight: 35%)

What to examine:
- Grid usage, alignment, spacing system (e.g., multiples of 4/8), vertical rhythm.
- Structural clarity: sectioning, scan patterns, focal points, and navigation affordances.
- Innovation that improves communication: novel but controlled structures, not novelty for its own sake.
- Image presentation: consistent crops, aspect ratios, corner radii, shadows, and caption alignment.
- Evidence breadth: multiple sections vs single hero; consistency across the page.

Score 5: Exceptional
- Masterful structure with a clear point of view that elevates clarity (e.g., inventive yet disciplined layouts, multi-column orchestration, or bespoke navigation that’s both usable and fresh).
- Immaculate rhythm and alignment; spacing feels intentional at every breakpoint/section.
- Screenshots/assets are composed with a shared visual system; micro-details (radii, borders, shadows, optical alignment) are tuned flawlessly across diverse content.

Score 4: Strong
- Consistent grid and spacing; clear section hierarchy; strong alignment.
- Image presentation is deliberate and cohesive; cards/tiles feel unified without sloppiness.
- Minor roughness allowed (e.g., slightly floaty element, a narrow gutter anomaly).
- Important: Uniform card grids with consistent spacing qualify for 4 only if notably refined; otherwise default to 3.

Score 3: Competent baseline
- Basic grid is present and mostly consistent; sections are readable with adequate spacing.
- Common patterns (single column, centered blocks, simple two‑column lists, card grids) executed decently but without sophistication or unique structure.
- Some inconsistencies in gutters, container widths, or vertical rhythm.

Score 1–2: Weak/Poor
- Random placement; competing focal points; inconsistent container widths without rationale.
- Haphazard screenshot handling; generic device mocks dominate; misaligned captions; mixed radii and shadows.
- Cramped or wasteful spacing that obscures hierarchy.

Common deductions (apply as needed):
- Evidence is limited to a single hero or very short page; cap at 3 unless craft is undeniably exceptional within that view.
- “Clean but generic”: centered hero + simple grid with soft shadows and rounded corners, no clear POV—do not exceed 3 unless refined to a high degree with demonstrable consistency.

## Color (Weight: 30%)

What to examine:
- Palette quality: harmony, value contrast, and consistency across sections.
- Intentional restraint vs. overuse; monochrome mastery with tuned greys; accent economy.
- Interaction between site chrome and work imagery: does the shell unify or clash with diverse screenshots?
- Shadow/overlay colorization (hue-shifted shadows, subtle tints) and accessible contrast.

Score 5: Exceptional
- Sophisticated palette with precise value control; accents are scarce but highly effective.
- Neutrals and hues are tuned (non-default), including shadows and borders; color unifies diverse content effortlessly.
- Creative color decisions that express identity without noise, demonstrated consistently across sections.

Score 4: Strong
- Harmonious palette with good restraint; accents used consistently for hierarchy.
- Neutrals are intentionally tuned (not pure black/white) and support readability.
- Minor issues only (e.g., one slightly loud accent or a single mismatched gradient).

Score 3: Competent baseline
- Palette is serviceable; minimal shell with a single accent or defaultish link blue used okay.
- When colorful work tiles provide most color, the chrome does not clash, but it also does not actively unify—this remains a 3 unless refinement is evident (matting, consistent backgrounds, tuned shadows).

Score 1–2: Weak/Poor
- Too many hues without a throughline; inconsistent saturation/values; clashing gradients.
- Greyscale sites with flat, untuned greys; default-dark shadows that feel heavy or mismatched.

Common deductions (apply as needed):
- Relying on work screenshots for color while the site shell is neutral/minimal does not merit 4–5 by itself. Look for unifying tactics: matched tile backgrounds, consistent corner radii/shadows, softened saturation, or balanced sequencing across a grid.
- Default link blue that feels loud against soft greys; inconsistent hover/active states within the visible view.

## Red Flags

Flag these when clearly present and reflect them in explanations.

- template_scent_high:
  - Obvious template patterns with minimal customization: centered hero with generic subhead + uniform card grid, stock “About” block, boilerplate footer, default link styles, and component spacing that mirrors popular UI kits.
  - Mismatched component radii/spacing that follow default tokens (e.g., 16px radii everywhere, identical card shadows) with no page-level system.
  - Repeated canned sections with identical structure and no bespoke visual decisions.

- sloppy_images:
  - Inconsistent crops/aspect ratios; varying or mismatched corner radii; aliasing/jaggies; compression artifacts; non-retina blurriness.
  - Generic device frames without customization; screenshots too zoomed out; illegible text; inconsistent mats or shadows around tiles.
  - Misaligned captions/labels; mixed border weights.

- process_soup:
  - Long process timelines/diagrams overwhelming final visuals; many wordy steps and photos of sticky notes vs. few high-quality product shots.
  - Excessive persona/journey maps with small, unreadable content; minimal outcome visuals.

Note: Only add red flags when visual evidence is clear. If uncertain, omit the flag and reduce confidence instead.

---

# EXEMPLAR CALIBRATION

Use these exemplar evaluations to calibrate your scoring. Prioritize the rubric; exemplars are anchors, not instructions. Use the full 1–5 range when warranted.

## Exemplar 1 (Score: 4.0)
Portfolio Category: Minimal  
Site URL: https://charliedeets.com/  
Image: exemplar_1.jpg

Typography (Score: 4): The typography takes a minimal direction. They create strong contrast between the title and the body, by making the title twice as large and bold, while using subtle changes in color to reflect the changes in hierarchy within the body text. The whole thing is set to system font, which further reinforces the minimal approach. While not original, it is well executed, achieving contrast and hierarchy with restraint.

Layout & Composition (Score: 4): The layout takes a minimal approach, putting the experience of the candidate forward, instead of leaning on screenshots. The line width is set to make reading comfortable while also playing into the minimalism. Whitespace and high contrast typography is used to provide hierarchy, which keeps visual noise low, while still being clear. There are no visual flourishes, but everything is clear, clean, and well-executed.

Color (Score: 4): The color system is extremely constrained, in keeping with the minimalism of the website. While not unique, the candidate uses shades of grey to effectively convey hierarchy while maintaining a clean minimal palette.

## Exemplar 2 (Score: 4.65)
Portfolio Category: Minimal  
Site URL: https://www.elvinhu.com/  
Image: exemplar_2.jpg

Typography (Score: 5): The typography mixes an editorial serif font for headers, which gives the website a distinct identity, with a simple sans serif for body text, which keeps things clean and simple. It also uses two great paid typefaces (GT Alpina and Untitled Sans) which tells us that the candidate really thought through their choices. The overall effect combination of typefaces achieve a good blend of elegance and simplicity.

Layout & Composition (Score: 4): The layout heavily emphasizes screenshots of the author's work and leans on them heavily as the center of visual interest. Because the images are so important, the author has also taken care to design each one of them in intentional layouts. The core concept of heavily image site is simple, but well-executed with adequate whitespace to create hierarchy, and subtle details like rounded corners for the screenshots to add a subtle flair.

Color (Score: 5): The website itself is minimal to not distract from the work screenshots, which are designed to each bring a different pop of colour. The primary colour of each screenshot is also well coordinated – each is a different hue, but are all similarly pastel, which makes them feel each unique but still cohesive.

## Exemplar 3 (Score: 1.7)
Portfolio Category: Minimal  
Site URL: https://www.agnimurthy.com/  
Image: exemplar_3.jpg

Typography (Score: 2): The site combines two similar looking sans serifs (overpass & roboto) which don't contrast enough to achieve visual interest. Instead adds random visual noise. Visual hierarchy is also lacking due to poor use of line spacing. The site uses multiple weight, size, family, opacity without restraint, causing it to feel busy and incohesive.

Layout & Composition (Score: 2): The site layout itself is relatively basic. The problem is that the author has put very busy screenshots of their work in small image boxes, which makes it feel busy and hard to read. There is insufficient differentiation between the case study sections and the author's bio, leading two distinct content sections to blend in together. The footer also randomly switches from full width content to narrow center aligned content.

Color (Score: 1): The website overuses colors without intentionality. Every case study has its own theme color in the CTA text, without the color contributing any meaning to the design. The site itself also has its purple theme color, which gets lost in the many colors from the case studies.

## Exemplar 4 (Score: 1.65)
Portfolio Category: Minimal  
Site URL: https://sallywangdesigns.com/  
Image: exemplar_4.jpg

Typography (Score: 2): The type choices are mediocre free fonts from google (open sans & calluna). The white space is also poorly done. The title and body should be closer. They also use a vertical bar to divide labels in their case study, but the vertical bars are taller and just as dark as the text they divide, making them feel like the primary visual element instead of a subtle divider.

Layout & Composition (Score: 1): Every section of this website, from nav, hero, case studies, to footer, are a different width for no apparent reason. The nav is full width justified, the hero is left aligned, the cases are justified full width, and the footer is center aligned again for no good reason. The screenshots of the work are also poorly laid out. They're mostly zoomed out too far to be able to show anything and use generic device templates.

Color (Score: 2): There was some attempt at creating a cohesive pastel color system, however, the effect is defeated by: 1. the strongly contrasting black and silver from the device mocks used in her screenshot, which distract from the pastel 2. the fact that there is a random darker colour used in the footer that is not cohesive with the softer, lighter pastel used in the rest of the site.

## Exemplar 5 (Score: 4.7)
Portfolio Category: Minimal  
Site URL: https://emilkowal.ski/  
Image: exemplar_5.jpg

Typography (Score: 5): This is an example of a really well-executed minimal typography system. They use exactly one size across the entire website, but through the clever usage of just a slight difference in color between dark and gray, they managed to achieve all the hierarchy and visual distinction that they need. So really there is a level of restraint here that achieves all the goals it seeks out to achieve with very few elements which is elegant. They use shades of gray and then ample white space to create all the hierarchy that they need. The white space is also ample between elements, but it's not too much for the line height. Overall, really well done.

Layout & Composition (Score: 5): The layout here is also very simple, but effective. They use white space in a very generous and confident way to create a hierarchy. It's very simple, but what it does it does very well.

Color (Score: 4): There is only one color here, but it doesn't mean that it's bad. The black and white here is well done. They chose a very slight shade of gray for the background which is intentional. They chose a contrasting color for the body text vs the title, but it's not too contrasting. They also didn't use pure black when they used a darker color. All of it is intentional, even if it's very minimal. Overall, I think this is a strong example of color usage even though it's all monochrome.

## Exemplar 6 (Score: 4.35)
Portfolio Category: Minimal  
Site URL: https://ryo.lu/  
Image: exemplar_6.jpg

Typography (Score: 5): This is another example of a great minimalist typography system. Here are the signs why it's good: first, the site uses two typefaces from a relatively obscure but really high-quality foundry called NB International. I think this was a very intentional choice that works really well for the site in both the super large title case and also the small body case. It demonstrates a level of mastery of typefaces, even though there is not much going on. There's also a nice bit of detail where their age is displayed in a super rapidly shifting number with high decimals, which is a very subtle but good design choice.

Layout & Composition (Score: 4): The composition here is simple yet makes great use of contrast. The title is really big and it really works here because there is a whole white space to frame it. The font is high quality and can hold up a large size. They also cleverly use a peel-back design at the top right to hint that there might be something more to this portfolio, which creates both Easter egg and visual focal point that lends subtle compositional interest.

Color (Score: 4): There is not much going on in terms of color - mostly only one monochrome color and then two shades of it. But they use it effectively, and this is an example of less done well.

## Exemplar 7 (Score: 0.5)
Portfolio Category: Minimal  
Site URL: candidate_21_original  
Image: exemplar_7.jpg  
Red Flags: template_scent_high, sloppy_images

Typography (Score: 1): The typography here is quite messy in a couple ways: one-line height for a lot of these elements is too wide, so for the header, there's too much line height, and then there's an equal amount of line height between the header and the body under it, and then the body and the buttons, which I think is a weird visual hierarchy. And then in the case studies, there's a ton of line height between every line, so it makes it almost seem like bullet points, but there's no bullets, so it's hard to tell whether it's bullet points or not. They've also just selected a really poorly designed serif font, which doesn't help.

Layout & Composition (Score: 1): There is no real rhyme or reason to the layout here. Every section feels like a different website. The cards are also really poorly done. They are overly rounded and I feel like they don't connect.

Color (Score: 2): There is sort of a theme going on here around a light purple, black, and white, but it's just really poorly executed. They use the color purple in a lot of places that doesn't make a lot of sense and doesn't bring emphasis where it's important. For example, the secondary button outline is purple. Why? There's no reason. The labels on the case studies are also purple outline. Again, no reason and confuses them with the buttons as well. Some of the labels are also filled, whereas others are outlined. Again, not really a good reason for this change and adds visual noise.

## Exemplar 8 (Score: 2.65)
Portfolio Category: Minimal  
Site URL: candidate_30_original  
Image: exemplar_8.jpg

Typography (Score: 2): The type work here is okay, I'm sort of somewhere between a 2 and a 3, probably more of a 2 if I was honest. She has selected a pretty cool, unique display type for her main header, the design code art part. And then the words in her top left nav. But she unfortunately doesn't carry it through to the rest of her site, so that the case study titles go back to this generic sans-serif which is not as interesting. In the case studies themselves, there's also a little bit of just messy font type usage. For example, "Selected work" is the same size as "Introducing a new homepage" underneath. "Selected work" is clearly a higher heading level and should probably be a little bigger or different, but it looks kind of the same as the case study titles. And then the case study title has sort of a two-line underneath one which is a body which is well done, but then the other one is sort of some key results which then is stronger than the body text and it's a little too close to the body text which deducts points for me. The labels needed a little bit more separation, so top padding, and probably needed to be a little smaller and not competing with the body. Right now the label is bigger than the body, which probably shouldn't be the case. There's also minor details that make the type not as good. For example, the vertical bar is a little too strong between the labels.

Layout & Composition (Score: 3): The layout here doesn't do too much, but it's relatively decently executed. There's a little bit of awkwardness at the "About me" section which feels like there's too many cards right? It's a card inside of a card. The bio section is just a little wider than everything else, along with the footer, and there's not a really good reason for it. It doesn't feel super intentional to me, which is also not that great. But otherwise, I think the website pulls off an overall generally competent sort of like spacing, hierarchy, and clarity in terms of the layout. And sort of like I think that if you just look at the hero section at the top and the case studies, I think it's like decently executed. With sort of just like a little bit of lack of refinement around details like what I just mentioned.

Color (Score: 3): They've done a decent job balancing a minimal website color palette with a few themes. So I see some mostly monochrome black and white here, but they've punctuated it with some blue and yellow. It's not super consistent, but it's consistent enough that there is a visual theme happening in general. There is also some use of background texture here. It's probably a little overdone, but the fact that it exists is a good sign, and it feels like they're able to use both color and texture. It's a little junior feeling, but not bad. They also have done some interesting gradient and noise work in the three little micro-images next to the words "design", "code", and "art". Again, this tells me that they have some experience working with color. They are not incredibly well done, but they show signs of promise. There are, however, still elements where I think there needs to be a little bit more refinement. For example, the divider line at the very end of her portfolio is too dark. And also, there are some awkward gradients at the car seller case study image that doesn't seem to match with the rest of the site, which is more flat. So minor mistakes, but overall I think it's showing promise in color usage.