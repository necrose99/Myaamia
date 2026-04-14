# FLex-enrichment.md

## Purpose
Expand raw TMX into FLEx-friendly lexical and grammatical records.

## Enrichment fields
- lemma
- surface form
- gloss
- part of speech
- inflection class
- affixation
- mood
- person
- number
- polarity
- pragmatics
- source provenance

## Enrichment rules
- Preserve the raw TMX pair.
- Add grammatical analysis when known.
- Separate dictionary sense from discourse use.
- Keep command forms distinct from base forms.
- Mark particles, interjections, and affixes explicitly.

## Example
- Raw TMX: `iihia = yes`
- Enriched record:
  - lemma: iihia
  - gloss: yes / affirmative
  - pos: particle
  - pragmatic role: confirmation
  - notes: may be used as a brief response.

- Raw TMX: `Mihšii Neewe`
- Enriched record:
  - lemma: Mihšii Neewe
  - gloss: thanks / thank you / much obliged
  - pos: expression
  - notes: context-dependent politeness formula.
