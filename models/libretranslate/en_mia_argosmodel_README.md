---
language:
  - en
  - mia
tags:
  - translation
  - argos-translate
  - libretranslate
  - low-resource
  - endangered-language
  - indigenous-language
  - algonquian
  - algic
license: mit
license_link: LICENSE
extra_gated_prompt: >-
  The trained model weights derive from the Myaamia Dictionary (Myaamia
  Center, Miami Tribe of Oklahoma). Code in this repo is MIT-licensed; the
  underlying lexical data is not relicensed by this project. See LICENSE.
---

# English ⟷ Myaamia (mia) — Alpha Translation Model

**Status: very early alpha.** This is a personal, volunteer research artifact, not an official release from the Myaamia Center or the Miami Tribe of Oklahoma. Treat outputs accordingly — this is a research/testing tool, not a source of truth for the language.

## What this is

A [LibreTranslate](https://libretranslate.com/) / [Argos Translate](https://github.com/argosopentech/argos-translate)-compatible `.argosmodel` package for English ⟷ Myaamia (Miami-Illinois, ISO 639-3: `mia`), a Central Algonquian (Algic) language. It's built to give researchers and community members an early, unofficial tool to work with while a more complete, community-directed effort continues.

I'm building this in spare time alongside cybersecurity/AI certification study, so progress is incremental — contributions, testing, and corrections are genuinely welcome.

## Data and known limitations

Trained on roughly **2,580 unique English–Myaamia pairs** after deduplication, drawn from:
- The Myaamia Dictionary (ILDA), primarily at the headword/gloss level — word and short-phrase pairs, not full sentences
- A small set of sentence-level pairs from an 1891 vocabulary and Lord's Prayer text

**This is low-resource data, and it shows in the output.** Myaamia is polysynthetic — words are built from richly inflected stems, and full sentences are not concatenations of dictionary entries. This model does not yet model that morphology. Expect:
- Reasonable results on isolated words and short, dictionary-adjacent phrases
- Unreliable results on full, freely-composed sentences

If you're using this for anything beyond casual testing, verify output against the Myaamia Dictionary or a fluent speaker rather than trusting it directly.

## Roadmap toward 1.0

- Morphological/polysynthetic feature handling, rather than whole-word lookup
- Growing the sentence-level training corpus (more parallel data recovered into TMX/dictionary form, not just word pairs)
- GGUF and ONNX variants alongside the CTranslate2/Argos package, for broader local tooling
- The hope is that 1.0 becomes genuinely useful for language revitalization and research, not just a proof of concept

## Contributing / testing

Volunteer testers are welcome — the most useful contribution right now is real Myaamia sentence data (existing texts, recordings with transcription, corrections to current output) rather than code. If you can help recover more parallel text into TMX or dictionary form, that has more impact on model quality at this stage than architecture changes.

## License

The code, training scripts, and model architecture in this repo are **MIT licensed** — free for anyone to use, adapt, and build on, as a voluntary contribution back to the community and to open MT tooling generally.

The **trained model weights and underlying lexical data are not covered by that MIT license**. They derive from the Myaamia Dictionary, maintained by the Myaamia Center at Miami University on behalf of the Miami Tribe of Oklahoma, and remain the Tribe's under whatever terms they set. See `LICENSE` for the full split. If the Myaamia Center wants this handled differently — different terms, takedown, or a transfer of the repo itself — that takes precedence over anything stated here.

## Provenance and respect for the source community

The underlying lexical data derives from the Myaamia Dictionary, maintained by the Myaamia Center at Miami University on behalf of the Miami Tribe of Oklahoma. This project is offered in that spirit, and the intent is for it — and future, better versions — to ultimately be shared with and handed over to the Myaamia Center rather than maintained as a separate, disconnected effort. It is not an official Center or Tribe product.
