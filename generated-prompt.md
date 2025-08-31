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


# RUBRIC

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


# EXEMPLAR RATINGS

{
  "1": {
    "exemplar_id": "1",
    "portfolio_category": "Minimal",
    "site_url": "https://charliedeets.com/",
    "image_filename": "exemplar_1.jpg",
    "criteria": {
      "typography": {
        "score": 4,
        "comment": "The typography takes a minimal direction. They create strong constrast between the title and the body, by making the title twice as large and bold, while using subtle changes in color to reflect the changes in hierarchy within the body text. The whole thing is set to system font, which further reinforces the minimal approach. While not original, it is well executed, achieving contrast and hierarchy with restraint"
      },
      "layout_composition": {
        "score": 4,
        "comment": "The layout is takes a minimal approach, putting in the experience of the candidate forward, instead of leaning on screenshots. The line width is set to make reading comfortable while also playing into the minimalism. Whitespace and high constrast typography is used to provide hierarchy, which keeps visual noise low, while still being clear. There are no visual flourishes, but everything is clear, clean, and well-executed"
      },
      "color": {
        "score": 4,
        "comment": "The color system is extremely constrained, in keeping with the minimalism of the website. While not unique, the candidate uses shades of grey to effectively convey hierarchy while maintaing a clean minimal palette"
      }
    }
  },
  "2": {
    "exemplar_id": "2",
    "portfolio_category": "Minimal",
    "site_url": "https://www.elvinhu.com/",
    "image_filename": "exemplar_2.jpg",
    "criteria": {
      "typography": {
        "score": 5,
        "comment": "The typography mixes an editorial serif font for headers, which gives the website a distinct identity, with a simple sans serif for body text, which keeps things clean and simple. It also two great paid typefaces (GT Alpina and Untitled Sans) which tells us that the candidate really thought through their choices.\n\nThe overall effect combination of typefaces achieve a good blend of elegance and simplicity"
      },
      "layout_composition": {
        "score": 4,
        "comment": "The layout heavily emphasizes screenshots of the author's work and leans on them heavily as the center of visual interest. Because the images are so important, the author has also taken care to design each one of them in intentional layouts.\n\nThe core concept of heavily image site is simple, but well-execute with adequate whitespace to create hierarchy, and subtle details like rounded corners for the screenshots to add a subtle flair."
      },
      "color": {
        "score": 5,
        "comment": "The website itself is minimal to not distract from the work screenshots, which are designed to each bring a different pop of colour. The primary colour of each screenshot is also well coordinate \u2013 each is a different hue, but are all similarly pastel, which makes them feel each unique but still cohesive"
      }
    }
  },
  "3": {
    "exemplar_id": "3",
    "portfolio_category": "Minimal",
    "site_url": "https://www.agnimurthy.com/",
    "image_filename": "exemplar_3.jpg",
    "criteria": {
      "typography": {
        "score": 2,
        "comment": "The site combines two similar looking sans serifs (overpass & roboto) which don't constrast enough to achieve visual interest. Instead adds random visual noise. Visual hierachy is also lacking due to poor use of line spacing. The site uses multiple weight, size, family, opacity without restraint, causing it to feel busy and incohesive."
      },
      "layout_composition": {
        "score": 2,
        "comment": "The site layout itself is relatively basic. The problem is that the author has put very busy screenshots of their work in small image boxes, which makes it feel busy and hard to read. There is insufficient differentiation between the case study sections and the author's bio, leading two distinct content sections to blend in together. The footer also randomly switches from full width content to narrow center aligned content."
      },
      "color": {
        "score": 1,
        "comment": "The website overuses colors without intentionality. Every case study has its own theme color in the CTA text, without the color contributing any meaning to the design. The site itself also has its purple theme color, which gets lost in the many colors from the case studies."
      }
    }
  },
  "4": {
    "exemplar_id": "4",
    "portfolio_category": "Minimal",
    "site_url": "https://sallywangdesigns.com/",
    "image_filename": "exemplar_4.jpg",
    "criteria": {
      "typography": {
        "score": 2,
        "comment": "The type choices are mediocre free fonts from google (open sans & calluna). The white space is also poorly done. The title and body should be closer. They also use a vertical bar to divide labels in their case study, but the vertical bars are taller and just as dark as the text they divider, making them feel like the primary visual element instead of a subtle divider."
      },
      "layout_composition": {
        "score": 1,
        "comment": "Every section of this website, from nav, hero, case studies, to footer, are a different width for no apparent reason. The nav is full width jusified, the hero is left aligned, the cases are justified full width, and the footer is center aligned again for no good reason.\n\nThe screenshots of the work are also poorly laid out. They're mosty zoomed out too far to be able to show anything and use generic device templates."
      },
      "color": {
        "score": 2,
        "comment": "There was some attempt at creating a cohesive pastel color system, however, the effect is defeated by: \n1. the strongly contrasting black and silver from the device mocks used in her screenshot, which distract from the pastelle\n2. the fact that there is a random darker colour used in the footer that is not cohesive with the softer, lighter pastelle used in the rest of the site"
      }
    }
  },
  "5": {
    "exemplar_id": "5",
    "portfolio_category": "Minimal",
    "site_url": "https://emilkowal.ski/",
    "image_filename": "exemplar_5.jpg",
    "criteria": {
      "typography": {
        "score": 5,
        "comment": "This is an example of a really well-executed minimal typography system. They use exactly one size across the entire website, but through the clever usage of just a slight difference in color between dark and gray, they managed to achieve all the hierarchy and visual distinction that they need. So really there is a level of restraint. Here that achieves all the goals it seeks out to achieve with very few elements which is elegant. They use shades of gray and then ample white space to create all the hierarchy that they need. The white space is also ample between elements, but it's not too much for the light height. Overall, really well done."
      },
      "layout_composition": {
        "score": 5,
        "comment": "The layout here is also very simple, but effective. They use white space in a very generous and confident way to create a hierarchy. It's very simple, but what it does it does very well."
      },
      "color": {
        "score": 4,
        "comment": "There is only one color here, but it doesn't mean that it's bad. The black and white here is well done. They chose a very slight shade of gray for the background which is intentional. They chose a contrasting color for the body text vs the title, but it's not too contrasting. They also didn't use pure black when they used a darker color. All of it is intentional, even if it's very minimal. Overall, I think this is a strong example of color usage even though it's all monochrome."
      }
    }
  },
  "6": {
    "exemplar_id": "6",
    "portfolio_category": "Minimal",
    "site_url": "https://ryo.lu/",
    "image_filename": "exemplar_6.jpg",
    "criteria": {
      "typography": {
        "score": 5,
        "comment": "This is another example of a great minimalist typography system. Here are the signs why it's good:first, the site uses two typefaces from a relatively obscure but really high-quality foundry called NB International. I think this was a very intentional choice that works really well for the site in both the super large title case and also the small body case.It demonstrates a level of mastery of typefaces, even though there is not much going on. There's also a nice bit of detail where their age is displayed in a super rapidly shifting number with high decimals, which is a very subtle but good design choice."
      },
      "layout_composition": {
        "score": 4,
        "comment": "The composition here is simple yet makes great use of contrast.The title is really big and it really works here because there is a whole white space to frame it. The font is high quality and can hold up a large size. They also cleverly use a peel-back design at the top right to hint that there might be something more to this portfolio, which creates both Easter egg and visual focal point that lends subtle compositional interest."
      },
      "color": {
        "score": 4,
        "comment": "There is not much going on in terms of color - mostly only one monochrome color and then two shades of it. But they use it effectively, and this is an example of less done well."
      }
    }
  },
  "7": {
    "exemplar_id": "7",
    "portfolio_category": "Minimal",
    "site_url": "candidate_21_original",
    "image_filename": "exemplar_7.jpg",
    "criteria": {
      "typography": {
        "score": 1,
        "comment": "The typography here is quite messy in a couple ways:one-line height for a lot of these elements is too wide, so for the header, there's too much line height, and then there's an equal amount of line height between the header and the body under it, and then the body and the buttons, which I think is a weird visual hierarchy.And then in the case studies, there's a ton of line height between every line, so it makes it almost seem like bullet points, but there's no bullets, so it's hard to tell whether it's bullet points or not.They've also just selected a really poorly designed serif font, which doesn't help."
      },
      "layout_composition": {
        "score": 1,
        "comment": "There is no real rhyme or reason to the layout here. Every section feels like a different website. The cards are also really poorly done. They are overly rounded and I feel like they don't connect. "
      },
      "color": {
        "score": 2,
        "comment": "There is sort of a theme going on here around a light purple, black, and white, but it's just really poorly executed.They use the color purple in a lot of places. That doesn't make a lot of sense and doesn't bring emphasis where it's important. For example, the secondary button outline is purple. Why? There's no reason.The labels on the case studies are also purple outline. Again, no reason and confuses them with the buttons as well.Some of the labels are also filled, whereas others are outlined. Again, not really a good reason for this change and adds visual noise. "
      }
    },
    "red_flags": [
      "template_scent_high",
      "sloppy_images"
    ]
  },
  "8": {
    "exemplar_id": "8",
    "portfolio_category": "Minimal",
    "site_url": "candidate_30_original",
    "image_filename": "exemplar_8.jpg",
    "criteria": {
      "typography": {
        "score": 2,
        "comment": "The type of work here is okay, I'm sort of somewhere between a 2 and a 3, probably more of a 2 if I was honest.She has selected a pretty cool, unique display type for her main header, the design code art part. And then the words in her top left nav. But she unfortunately doesn't carry it through to the rest of her site, so that the case study titles go back to this generic sans-serif which is not as interesting.In the case study themselves, there's also a little bit of just messy font type usage. For example, \"Selected work\" is the same size as \"Introducing a new homepage\" underneath. \"Selected work\" is clearly a higher heading level and should probably be a little bigger or different, but it looks kind of the same as the case study titles. And then the case study title has sort of a two-line underneath one which is a body which is well done, but then the other one is sort of some key results which then is stronger than the body text and it's a little too close to the body text which deducts points for me.The labels needed a little bit more separation, so top padding, and probably needed to be a little smaller and not competing with the body. Right now the label is bigger than the body, which probably shouldn't be the case.There's also minor details that make the type not as good. For example, the vertical bar is a little too strong between the labels."
      },
      "layout_composition": {
        "score": 3,
        "comment": "The layout here doesn't do too much, but it's relatively decently executed. There's a little bit of awkwardness at the \"About me\" section which feels like there's too many cards right? It's a card inside of a card. The bio section is just a little wider than everything else, along with the footer, and there's not a really good reason for it. It doesn't feel super intentional to me, which is also not that great.But otherwise, I think the website pulls off an overall generally competent sort of like spacing, hierarchy, and clarity in terms of the layout. And sort of like I think that if you just look at the hero section at the top and the case studies, I think it's like decently executed. With sort of just like a little bit of lack of refinement around details like what I just mentioned."
      },
      "color": {
        "score": 3,
        "comment": "They've done a decent job balancing a minimal website color palette with a few themes. So I see some mostly monochrome black and white here, but they've punctuated it with some blue and yellow. It's not super consistent, but it's consistent enough that there is a visual theme happening in general. There is also some use of background texture here. It's probably a little overdone, but the fact that it exists is a good sign, and it feels like they're able to use both color and texture. It's a little junior feeling, but not bad.They also have done some interesting gradient and noise work in the three little micro-images next to the words \"design\", \"code\", and \"art\". Again, this tells me that they have some experience working with color. They are not incredibly well done, but they show signs of promise. There are, however, still elements where I think there needs to be a little bit more refinement. For example, the divider line at the very end of her portfolio is too dark.And also, there are some awkward gradients at the car seller case study image that doesn't seem to match with the rest of the site, which is more flat. So minor mistakes, but overall I think it's showing promise in color usage."
      }
    }
  }
}