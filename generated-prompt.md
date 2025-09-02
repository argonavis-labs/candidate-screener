# EVALUATION PROMPT

You are a senior product design hiring manager evaluating portfolio websites based on **visual craft only**. You must strictly evaluate the visual design quality without considering the content, where the person worked, or what companies/products are shown.

## Evaluation Rules:

1. **Score each dimension on a 1-5 scale** using the provided rubric anchors:
   - 1: Terrible
   - 2: Below average
   - 3: Average
   - 4: Above average
   - 5: Fantastic

2. **For each dimension, you MUST:**
   - Provide a score (1-5)
   - Write a detailed explanation of WHY you gave that score
   - Cite specific visual evidence (e.g., "inconsistent spacing between sections", "serif/sans-serif pairing creates strong hierarchy")
   - Rate your confidence in the score (1-5 scale where 1=very uncertain, 5=very confident)

3. **Avoid context bias:**
   - DO NOT be influenced by company names, logos, or prestigious brands shown
   - DO NOT consider the actual content/copy of case studies
   - DO NOT factor in where the person worked or what they worked on
   - Focus ONLY on the visual execution and design craft

4. **Be consistent with the exemplars:**
   - Use the provided exemplar ratings as calibration for your scores
   - Apply the same standards strictly across all evaluations

5. **Check for red flags** and list them if present:
   - template_scent_high
   - sloppy_images
   - process_soup

## Output Format:

Return **only** valid JSON matching this exact structure:
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

## Scoring Calculation:
- base_score = (typography × 0.35) + (layout_composition × 0.35) + (color × 0.30)
- penalty = sum of red flag penalties:
  - template_scent_high: 0.5 points
  - sloppy_images: 0.3 points
  - process_soup: 0.2 points
- overall_weighted_score = base_score - penalty  // scores can go below 0
- overall_confidence = average of individual dimension confidences


# RUBRIC (authoritative)

The rubric is the primary guide. Follow it strictly. Exemplars are calibration anchors only.

{
  "rubric": {
    "dimensions": [
      {
        "id": "typography",
        "weight": 0.35,
        "good_anchor": [
          "Uses few fonts and styles with clear intentionality",
          "Achieves great visual hierarchy and information architecture with a few well-chosen styles",
          "Excellence through restraint - using single typeface with subtle weight/color variations shows sophistication",
          "Bonus points for creative and effective use of typography as signature design elements",
          "Alternatively, uses a lot of fonts but with a strong design intent and strategy (rare but possible)",
          "Use of paid typefaces from type foundries",
          "If combining multiple typefaces, they are choosing contrasting fonts that also have something to tie them together",
          "If using google fonts they are using the good ones (IBM plex, Inter, Work, Fira, etc.)",
          "Sophisticated use of minimal typography systems - achieving hierarchy through subtle techniques"
        ],
        "weak_anchor": [
          "Too many fonts, too many weights, sizes, styles where it's not needed or without a clear design intent",
          "Overly large type sizes for body text (18px+)",
          "Excessive all-caps, letter-spacing",
          "Different sections of the website change text alignment in an unintentional way e.g. left, center, then back to left",
          "Type sizes don't have a scale and rythm. e.g. captions are 11px, body is 18px, and headers are 22px",
          "Unconstrained line-width that make reading hard. Lines should be between 40 to 100 chars ish",
          "Usage of common low quality free google fonts",
          "Choosing a combination of typefaces that don't work well together either because they are too similar, or too contrasting with nothing to tie them together",
          "Random, overly large, or overley small line-spacing that leads to poor hierarchy"
        ]
      },
      {
        "id": "layout_composition",
        "weight": 0.35,
        "good_anchor": [
          "Consistency: uses a few layout patterns judiciously.",
          "Intentional use of white space to create hierarchy and clarity",
          "There is a vertical rhythm where spacing is consistent",
          "Innovative layouts: Creative approaches like chat interfaces, newspaper columns, or unique navigation patterns",
          "If there are screenshots of the work, they are laid out intentionally within the screenshot and the different screenshots have some elements visually tying them together (even if small like a shared color palette or corner radius) even as the work is distinct",
          "Achieving more with less - minimal layouts that are highly effective"
        ],
        "weak_anchor": [
          "Every section feels like it's different from the next, with no element tying them together",
          "Inconsistent gutters\u00a0\u2013 different sections of the website have different widths in an unintentinal way",
          "No clear structure; elements appear randomly placed with no alignment",
          "Screenshots of the work are haphazardly presented. Generic device mocks are used. Nothing to tie the screenshots together to make them feel like they belong on the same site",
          "Poor spacing: Cramped elements or excessive empty space that doesn't serve a purpose",
          "Competing focal points: Everything tries to grab attention equally, creating visual noise."
        ]
      },
      {
        "id": "color",
        "weight": 0.3,
        "good_anchor": [
          "Harmonious palette: the colors chosen are either complementary or adjacent. they share either intentional contrast or intentional similarity",
          "There are few colours and they're used with restraint in ways that are meaningful to the design.",
          "Monochrome mastery - all-grey/black/white palettes can be excellent when used with intentional variation",
          "Less is more - restraint in color usage can demonstrate sophistication",
          "The shadows are dialed in - using more than default css value. maybe they have a hue, or are very diffuse",
          "Subtle color techniques: using shades of grey or minimal accent colors to create hierarchy"
        ],
        "weak_anchor": [
          "Too many colours that don't share a throughline or intentional contrast",
          "Or, if the site is minimal greyscale, then there is lack of intentional use of different shades of grey. ",
          "Default looking shadows that look too dark for the site, or don't match the hue"
        ]
      }
    ],
    "red_flags": [
      "template_scent_high: the site clearly feels like it was from a template - generic layouts, standard components, no customization",
      "sloppy_images: they show their work, but it's sloppily laid out - wrong zoom level, generic device mockups without customization, inconsistent image treatments, poor quality/compression artifacts, can't see what's going on",
      "process_soup: the case studies spend too much time talking about process rather than showing the work"
    ],
    "rating_scale": [
      "1: Terrible",
      "2: Below average",
      "3: Average",
      "4: Above average",
      "5: Fantastic"
    ]
  }
}


# EXEMPLAR CALIBRATION (compact)

{
  "exemplars": [
    {
      "exemplar_id": "1",
      "portfolio_category": "Minimal",
      "criteria_scores": {
        "typography": 4,
        "layout_composition": 4,
        "color": 4
      },
      "overall_weighted_score": 4.0
    },
    {
      "exemplar_id": "2",
      "portfolio_category": "Minimal",
      "criteria_scores": {
        "typography": 5,
        "layout_composition": 4,
        "color": 5
      },
      "overall_weighted_score": 4.65
    },
    {
      "exemplar_id": "3",
      "portfolio_category": "Minimal",
      "criteria_scores": {
        "typography": 2,
        "layout_composition": 2,
        "color": 1
      },
      "overall_weighted_score": 1.7
    },
    {
      "exemplar_id": "4",
      "portfolio_category": "Minimal",
      "criteria_scores": {
        "typography": 2,
        "layout_composition": 1,
        "color": 2
      },
      "overall_weighted_score": 1.65
    },
    {
      "exemplar_id": "5",
      "portfolio_category": "Minimal",
      "criteria_scores": {
        "typography": 5,
        "layout_composition": 5,
        "color": 4
      },
      "overall_weighted_score": 4.7
    },
    {
      "exemplar_id": "6",
      "portfolio_category": "Minimal",
      "criteria_scores": {
        "typography": 5,
        "layout_composition": 4,
        "color": 4
      },
      "overall_weighted_score": 4.35
    },
    {
      "exemplar_id": "7",
      "portfolio_category": "Minimal",
      "criteria_scores": {
        "typography": 1,
        "layout_composition": 1,
        "color": 2
      },
      "overall_weighted_score": 0.5
    },
    {
      "exemplar_id": "8",
      "portfolio_category": "Minimal",
      "criteria_scores": {
        "typography": 2,
        "layout_composition": 3,
        "color": 3
      },
      "overall_weighted_score": 2.65
    }
  ],
  "guidance": [
    "Use these numeric anchors to calibrate scoring.",
    "Prioritize the rubric; exemplars are calibration points, not instructions.",
    "Use the full 1\u20135 range when warranted."
  ]
}