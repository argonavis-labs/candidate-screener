# Exemplar Images Directory

This directory contains the reference portfolio images used for evaluation calibration.

## Purpose

These exemplar images are:
- **Essential for consistent scoring** - The AI uses them to calibrate ratings
- **Always committed to git** - Team members need the same reference images
- **Pre-compressed and optimized** - Small enough for version control
- **Linked to exemplars.json** - Each image corresponds to a rated example

## Current Exemplars

- `exemplar_1.jpg` - Minimal portfolio (Charlie Deets)
- `exemplar_2.jpg` - Minimal portfolio (Elvin Hu) 
- `exemplar_3.jpg` - Minimal portfolio (Agni Murthy)
- `exemplar_4.jpg` - Minimal portfolio (Sally Wang)

## Adding New Exemplars

1. Add the image file: `exemplar_N.jpg`
2. Update `exemplars.json` with ratings and metadata
3. Update this README
4. Commit both the image and JSON changes together

## Git Handling

Unlike candidate images, exemplar images ARE committed because:
- They're small (~200KB - 1MB each)
- They're essential for evaluation consistency
- The team needs the same reference set
- They change infrequently
