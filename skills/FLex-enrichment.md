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
## Example Miami mia 
- Raw TMX: `Mihšii Neewe`
- Enriched record:
  - lemma: Mihšii Neewe
  - gloss: thanks / thank you / much obliged
  - pos: expression
  - notes: context-dependent politeness formula.

## Example Miami mia 
- Mihšii: big, much, great; intensifier / quantitative adjective depending on context.
- siipiiwi: river.
- Mihsi-siipiiwi: Big River / Great River.
- Mississippi: French rendering of an Algonquian river name, often glossed as Great River.

### Mihšii / Mihsi- Example Miami mia 

- lemma: Mihšii
- gloss: big / much / great
- notes: intensity or size-related meaning; context dependent.

### siipiiwi

- lemma: siipiiwi
- gloss: river noun 
- notes: appears in river names and place-name compounds.

### Mihsi-siipiiwi

- gloss: big river / great river
- notes: compound form; compare Mississippi river-name tradition.
- # Miami-Illinois mia for Mississippi river literally. 
