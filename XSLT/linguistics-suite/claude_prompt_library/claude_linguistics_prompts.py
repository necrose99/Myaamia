#!/usr/bin/env python3
"""
claude_linguistics_prompts.py
==============================
Claude AI prompt library for computational linguistics pipelines.

This module provides battle-tested system prompts, few-shot templates,
and chain-of-thought patterns that leverage Claude's capabilities for:

  • IPA transcription from orthographic forms
  • Leipzig interlinear glossing (morpheme segmentation + gloss)
  • Etymology reconstruction (DMLex etymonUnit format)
  • Psychoacoustic annotation from audio descriptions
  • EAF tier content generation and validation
  • LIFT lexical entry enrichment
  • TMX quality estimation and post-editing
  • XLIFF translation review and consistency checking
  • Cross-format metadata harmonisation
  • Fieldwork session summarisation

Each prompt is structured for use with the Anthropic Messages API:
  - system_prompt   : the system turn
  - user_template   : f-string template for the user turn
  - output_schema   : expected JSON output structure (for structured outputs)

Usage
-----
  from claude_linguistics_prompts import PromptLibrary, ClaudeAdapter

  cl = ClaudeAdapter(api_key="sk-ant-...")

  # Generate IPA for a LIFT entry
  ipa = cl.run(
      PromptLibrary.IPA_FROM_ORTH,
      orth="ama maka buru",
      lang_name="Tuwari",
      lang_code="tww",
      neighbours=["ama=dog", "maka=eat"]
  )

  # Add Leipzig glosses to an EAF morph tier
  glosses = cl.run(
      PromptLibrary.LEIPZIG_GLOSS,
      morphemes="ama-ki  misi-ki  war-a-tur-u",
      free_translation="The dog made the cat see it.",
      source_lang="tww",
      gloss_lang="en"
  )
"""

from __future__ import annotations

import json
import os
import sys
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

# ── Anthropic SDK (optional — graceful degradation) ───────────────────────────
try:
    import anthropic
    _ANTHROPIC_AVAILABLE = True
except ImportError:
    _ANTHROPIC_AVAILABLE = False


# ─────────────────────────────────────────────────────────────────────────────
# Prompt descriptor
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Prompt:
    """A reusable Claude prompt template for linguistics tasks."""
    name:          str
    task:          str
    system:        str
    user_template: str
    output_schema: dict = field(default_factory=dict)
    model:         str  = "claude-sonnet-4-20250514"
    max_tokens:    int  = 1024
    temperature:   float = 0.0   # deterministic for linguistic annotation


# ─────────────────────────────────────────────────────────────────────────────
# Prompt Library
# ─────────────────────────────────────────────────────────────────────────────

class PromptLibrary:
    """
    Curated prompt templates for computational linguistics workflows.

    All prompts are designed to produce structured JSON output that maps
    directly onto generateDS binding objects (lift_ds, eaf_ds, tmx14_ds,
    xliff_ds) for downstream pipeline integration.
    """

    # ── IPA Transcription ─────────────────────────────────────────────────────

    IPA_FROM_ORTH = Prompt(
        name="ipa_from_orth",
        task="Generate IPA phonetic transcription from orthographic form",
        system="""You are a computational phonologist and IPA expert.
Given an orthographic word or phrase in an under-documented language,
produce a Unicode IPA transcription following these rules:

1. Use the full IPA Unicode block (U+0250–U+02AF, U+0300–U+036F for diacritics).
2. Mark primary stress with ˈ (U+02C8) before the stressed syllable.
3. Mark secondary stress with ˌ (U+02CC).
4. Use syllable dot · only when syllabification is unambiguous.
5. If the language family is known, apply known phonological patterns.
6. Mark uncertainty with parentheses around the uncertain segment.
7. Return ONLY valid JSON matching the schema — no prose, no markdown fences.

Output schema:
{
  "ipa": "string — the IPA transcription",
  "syllabified": "string — syllabified form using ·",
  "confidence": 0.0-1.0,
  "notes": "string — phonological assumptions made (empty string if none)",
  "fonipa_lang_tag": "string — BCP-47 fonipa subtag e.g. tww-fonipa"
}""",
        user_template="""Transcribe the following into IPA:

Orthographic form : {orth}
Language name     : {lang_name}
Language code     : {lang_code}
Language family   : {lang_family}
Known phonemes    : {known_phonemes}
Neighbouring forms for analogy: {neighbours}

Return only the JSON object.""",
        output_schema={
            "ipa": str, "syllabified": str,
            "confidence": float, "notes": str, "fonipa_lang_tag": str
        },
    )

    # ── Leipzig Interlinear Glossing ──────────────────────────────────────────

    LEIPZIG_GLOSS = Prompt(
        name="leipzig_gloss",
        task="Generate Leipzig interlinear morpheme glosses",
        system="""You are a morphological analyst trained in the Leipzig Glossing Rules
(https://www.eva.mpg.de/lingua/resources/glossing-rules.php).

Given a morpheme-segmented string and a free translation, produce
Leipzig-style interlinear glosses. Rules:

1. Morpheme boundaries: hyphens (-) for affixes, equals (=) for clitics.
2. Grammatical categories in SMALL CAPS (write as ALL CAPS in plain text).
3. One gloss per morpheme, separated by spaces matching the morpheme count.
4. Use standard Leipzig abbreviations: NOM,ACC,DAT,GEN,ERG,ABS,NPST,PST,
   PRS,FUT,SG,PL,1,2,3,M,F,N,CAUS,PASS,REFL,NEG,Q,COMP,REL,TOP,FOC,...
5. Lexical morphemes in lowercase.
6. If a morpheme is ambiguous, use the most contextually appropriate gloss.
7. Return ONLY valid JSON — no prose.

Output schema:
{
  "glosses": "string — space-separated glosses matching morpheme count",
  "morpheme_count": integer,
  "parse_notes": "string — any ambiguities or assumptions",
  "grammatical_features": ["list of grammatical features identified"]
}""",
        user_template="""Gloss the following morpheme string:

Morpheme segmentation : {morphemes}
Free translation      : {free_translation}
Source language       : {source_lang}
Gloss metalanguage    : {gloss_lang}
Known paradigm info   : {paradigm_notes}

Return only the JSON object.""",
        output_schema={
            "glosses": str, "morpheme_count": int,
            "parse_notes": str, "grammatical_features": list
        },
    )

    # ── Etymology (DMLex etymonUnit) ──────────────────────────────────────────

    ETYMOLOGY = Prompt(
        name="etymology",
        task="Generate DMLex-compatible etymonUnit data",
        system="""You are a historical linguist and etymology specialist.
Given a lexical form, propose its etymological origin following the
OASIS DMLex 1.0 etymonUnit object type specification.

Output a JSON array of etymon chain steps (oldest first):
[
  {
    "langCode": "BCP-47 language code of the etymon language",
    "text": "the reconstructed or attested etymon form",
    "reconstructed": true/false,
    "partOfSpeech": ["list of POS tags if known"],
    "translation": "meaning of the etymon in the target metalanguage",
    "listingOrder": integer starting at 1,
    "confidence": 0.0-1.0,
    "sourceRef": "citation or 'unknown'"
  }
]

Rules:
1. Mark unattested reconstructed forms with leading asterisk in "text" AND reconstructed=true.
2. Use ISO 639-3 codes for ancient languages (e.g. "ang" for Old English, "lat" for Latin).
3. Include at most 5 steps in the chain.
4. If etymology is unknown, return a single step with reconstructed=true and confidence<0.3.
5. Return ONLY the JSON array — no prose.""",
        user_template="""Propose the etymology of:

Headword      : {headword}
Language      : {lang_name} ({lang_code})
Meaning       : {meaning}
Language family: {lang_family}
Known cognates : {cognates}

Return only the JSON array.""",
        output_schema={"etymon_chain": list},
    )

    # ── Psychoacoustic Annotation ─────────────────────────────────────────────

    PSYCHOACOUSTIC_TAG = Prompt(
        name="psychoacoustic_tag",
        task="Extract structured psychoacoustic features from audio description",
        system="""You are an acoustic phonetician specialising in field recording analysis.
Given a natural-language description of a speech segment's acoustic properties,
extract structured psychoacoustic parameters.

Output schema:
{
  "F0_mean_hz":      number or null,
  "F0_range_hz":     [min, max] or null,
  "intensity_db":    number or null,
  "duration_ms":     number or null,
  "VOT_ms":          number or null,
  "aspiration":      "yes" | "no" | "partial" | null,
  "nasalisation":    "yes" | "no" | "partial" | null,
  "creaky_voice":    "yes" | "no" | "partial" | null,
  "breathy_voice":   "yes" | "no" | "partial" | null,
  "tone":            "high" | "low" | "rising" | "falling" | "mid" | null,
  "formants": {
    "F1_hz": number or null,
    "F2_hz": number or null,
    "F3_hz": number or null
  },
  "notes": "string"
}

Return ONLY the JSON object.""",
        user_template="""Extract psychoacoustic parameters from:

Audio description : {description}
Segment type      : {segment_type}
Speaker           : {speaker_id}
Language          : {lang_name}

Return only the JSON object.""",
        output_schema={
            "F0_mean_hz": float, "intensity_db": float,
            "VOT_ms": float, "aspiration": str, "tone": str
        },
    )

    # ── EAF Tier Validator ────────────────────────────────────────────────────

    EAF_TIER_REVIEW = Prompt(
        name="eaf_tier_review",
        task="Review and correct EAF tier annotation content",
        system="""You are a linguistic annotator reviewing ELAN tier data.
Given a set of annotation values from an EAF tier, identify errors and
suggest corrections. Return structured JSON.

Error types to detect:
  - ipa_error: malformed IPA characters or syllabification
  - gloss_error: non-Leipzig abbreviations, wrong morpheme count
  - ortho_error: apparent typos in orthographic transcription
  - consistency: same morpheme glossed differently across annotations
  - completeness: missing required annotation

Output schema:
{
  "errors": [
    {
      "annotation_id": "string",
      "annotation_value": "string",
      "error_type": "string",
      "description": "string",
      "suggested_correction": "string or null"
    }
  ],
  "summary": {
    "total_checked": integer,
    "errors_found": integer,
    "consistency_issues": integer
  }
}""",
        user_template="""Review the following EAF tier annotations:

Tier ID   : {tier_id}
Tier type : {tier_type}
Language  : {lang_code}

Annotations (annotation_id: value):
{annotations_json}

Return only the JSON object.""",
        output_schema={"errors": list, "summary": dict},
    )

    # ── LIFT Entry Enrichment ─────────────────────────────────────────────────

    LIFT_ENRICH = Prompt(
        name="lift_enrich",
        task="Enrich a LIFT lexical entry with missing fields",
        system="""You are a computational lexicographer. Given a partial LIFT
lexical entry in JSON representation, suggest values for missing fields.

Fill these fields if absent:
  - ipa: IPA pronunciation
  - semantic_domains: 1-3 semantic domain codes (SIL DDP4 numbering)
  - grammatical_info: POS tag
  - antonyms: list of antonym headwords if any
  - synonyms: list of synonym headwords if any
  - register: "formal" | "informal" | "technical" | "archaic" | null
  - etymology_note: brief note on etymology (or null)

Output schema:
{
  "headword": "string",
  "ipa": "string or null",
  "semantic_domains": ["list of domain codes"],
  "grammatical_info": "string or null",
  "antonyms": ["list"],
  "synonyms": ["list"],
  "register": "string or null",
  "etymology_note": "string or null",
  "confidence": 0.0-1.0
}

Base your suggestions on the provided glosses and context.
Return ONLY the JSON object.""",
        user_template="""Enrich this LIFT entry:

Headword      : {headword}
Language      : {lang_name} ({lang_code})
Glosses       : {glosses_json}
Definitions   : {definitions_json}
Examples      : {examples_json}
Existing morph: {morph_type}

Return only the JSON object.""",
        output_schema={
            "headword": str, "ipa": str,
            "semantic_domains": list, "grammatical_info": str,
            "confidence": float
        },
    )

    # ── TMX Quality Estimation ────────────────────────────────────────────────

    TMX_QE = Prompt(
        name="tmx_quality_estimate",
        task="Estimate translation quality of TMX translation units",
        system="""You are a translation quality estimator specialising in
under-resourced language pairs. Given source and target text pairs from a TMX,
estimate translation quality without a reference translation.

For each pair output:
{
  "tuid": "string",
  "score": 0.0-1.0,
  "issues": [
    {"type": "over_translation"|"under_translation"|"mistranslation"|
              "fluency"|"terminology"|"register", "description": "string"}
  ],
  "suggested_edit": "string or null"
}

Return a JSON array of these objects.""",
        user_template="""Estimate quality for these TMX translation units:

Source language : {source_lang}
Target language : {target_lang}
Domain          : {domain}

Translation units:
{tu_list_json}

Return only the JSON array.""",
        output_schema={"units": list},
    )

    # ── XLIFF Consistency Check ───────────────────────────────────────────────

    XLIFF_CONSISTENCY = Prompt(
        name="xliff_consistency",
        task="Check XLIFF file for translation consistency and glossary adherence",
        system="""You are a translation consistency checker.
Given a list of XLIFF trans-units and an optional glossary, identify:

1. Same source translated differently (inconsistency)
2. Different sources translated the same (over-harmonisation)
3. Glossary violations (key term translated incorrectly)
4. ITS translate="no" content that was translated (ITS violation)
5. Untranslated units (missing target)

Output schema:
{
  "inconsistencies": [{"source": str, "translations": [str], "unit_ids": [str]}],
  "its_violations": [{"unit_id": str, "note_content": str, "target_content": str}],
  "glossary_violations": [{"unit_id": str, "term": str, "expected": str, "found": str}],
  "untranslated": ["list of unit ids"],
  "summary": {"total_units": int, "issues_found": int}
}""",
        user_template="""Check consistency for XLIFF units:

Source language : {source_lang}
Target language : {target_lang}
Glossary        : {glossary_json}

Trans-units (id: source → target):
{units_json}

Return only the JSON object.""",
        output_schema={
            "inconsistencies": list, "its_violations": list,
            "untranslated": list, "summary": dict
        },
    )

    # ── Fieldwork Session Summariser ──────────────────────────────────────────

    SESSION_SUMMARY = Prompt(
        name="session_summary",
        task="Summarise a fieldwork session from EAF annotation data",
        system="""You are a documentary linguist summarising fieldwork sessions.
Given utterance-level data extracted from an ELAN annotation file, produce
a structured session summary for archiving and metadata purposes.

Output schema:
{
  "session_overview": "2-3 sentence description",
  "language_features_observed": ["list of notable phonological/morphological/syntactic features"],
  "vocabulary_domains": ["semantic domains covered"],
  "text_types": ["narrative"|"procedural"|"conversational"|"elicited"|...],
  "speaker_profile": {"estimated_age_range": str, "register": str, "dialect_notes": str},
  "data_quality": {
    "audio_quality": "good"|"fair"|"poor",
    "transcription_completeness": 0.0-1.0,
    "recommended_followup": ["list of follow-up elicitation targets"]
  },
  "olac_genre": "string — OLAC discourse type URI",
  "suggested_archive_keywords": ["list"]
}""",
        user_template="""Summarise this fieldwork session:

Language    : {lang_name} ({lang_code})
Duration    : {duration_ms}ms
Speaker     : {speaker_id}
Utterance count: {utterance_count}

Orthographic utterances:
{utterances_json}

Free translations:
{translations_json}

Elicitation notes:
{notes}

Return only the JSON object.""",
        output_schema={
            "session_overview": str,
            "language_features_observed": list,
            "olac_genre": str
        },
    )

    # ── All prompts registry ──────────────────────────────────────────────────

    ALL: dict[str, Prompt] = {}

    @classmethod
    def _register(cls):
        for attr in dir(cls):
            val = getattr(cls, attr)
            if isinstance(val, Prompt):
                cls.ALL[val.name] = val

    @classmethod
    def get(cls, name: str) -> Prompt:
        cls._register()
        return cls.ALL[name]

    @classmethod
    def list_prompts(cls) -> list[str]:
        cls._register()
        return sorted(cls.ALL)


PromptLibrary._register()


# ─────────────────────────────────────────────────────────────────────────────
# Claude API adapter
# ─────────────────────────────────────────────────────────────────────────────

class ClaudeAdapter:
    """
    Thin wrapper around the Anthropic Messages API for linguistics tasks.

    Parameters
    ----------
    api_key : Anthropic API key (env: ANTHROPIC_API_KEY)
    model   : Default model override
    """

    DEFAULT_MODEL = "claude-sonnet-4-20250514"

    def __init__(
        self,
        api_key: str | None = None,
        model:   str | None = None,
    ):
        if not _ANTHROPIC_AVAILABLE:
            raise ImportError("pip install anthropic")
        self.client = anthropic.Anthropic(
            api_key=api_key or os.getenv("ANTHROPIC_API_KEY", "")
        )
        self.default_model = model or self.DEFAULT_MODEL

    def run(
        self,
        prompt: Prompt,
        **kwargs,
    ) -> dict | str:
        """
        Execute a Prompt template with the provided keyword arguments.

        Fills *prompt.user_template* with **kwargs, calls the API,
        parses JSON response (if prompt.output_schema is non-empty),
        and returns the parsed dict or raw string.

        Parameters
        ----------
        prompt : A Prompt instance from PromptLibrary
        **kwargs : Template variables for prompt.user_template
        """
        # Fill defaults for missing template vars
        import re
        placeholders = re.findall(r'\{(\w+)\}', prompt.user_template)
        for p in placeholders:
            if p not in kwargs:
                kwargs[p] = ""

        user_text = prompt.user_template.format(**kwargs)

        message = self.client.messages.create(
            model=prompt.model or self.default_model,
            max_tokens=prompt.max_tokens,
            temperature=prompt.temperature,
            system=prompt.system,
            messages=[{"role": "user", "content": user_text}],
        )

        raw = message.content[0].text.strip()

        if prompt.output_schema:
            # Strip accidental markdown fences
            clean = raw.replace("```json", "").replace("```", "").strip()
            try:
                return json.loads(clean)
            except json.JSONDecodeError:
                log.warning("JSON parse failed for prompt %r; returning raw string",
                            prompt.name)
                return raw
        return raw

    # ── High-level convenience methods ───────────────────────────────────────

    def ipa_for_lift_entry(self, entry, lang_name: str = "", lang_code: str = "") -> str:
        """
        Generate IPA for a lift_ds.entry object.
        Returns the IPA string or "" if generation fails.
        """
        lu = entry.get_lexical_unit()
        if not lu or not lu.get_form():
            return ""
        orth = lu.get_form()[0].get_text() or ""
        senses = entry.get_sense()
        glosses = []
        for s in senses:
            for g in s.get_gloss():
                if g.get_text():
                    glosses.append(f"{g.get_lang()}:{g.get_text()}")

        result = self.run(
            PromptLibrary.IPA_FROM_ORTH,
            orth=orth,
            lang_name=lang_name,
            lang_code=lang_code,
            lang_family="",
            known_phonemes="",
            neighbours=", ".join(glosses[:5]),
        )
        if isinstance(result, dict):
            return result.get("ipa", "")
        return ""

    def gloss_for_eaf_morph(
        self,
        morph_value: str,
        free_translation: str = "",
        source_lang: str = "und",
        gloss_lang: str = "en",
    ) -> str:
        """
        Generate Leipzig glosses for an EAF morph tier annotation value.
        Returns the gloss string.
        """
        result = self.run(
            PromptLibrary.LEIPZIG_GLOSS,
            morphemes=morph_value,
            free_translation=free_translation,
            source_lang=source_lang,
            gloss_lang=gloss_lang,
            paradigm_notes="",
        )
        if isinstance(result, dict):
            return result.get("glosses", "")
        return ""

    def enrich_lift_file(
        self,
        lift_path: str | Path,
        lang_name: str,
        lang_code: str,
        output_path: str | Path | None = None,
    ) -> Path:
        """
        Enrich every entry in a LIFT file with Claude-generated IPA,
        semantic domains, and etymology notes.
        Writes back to output_path (defaults to .enriched.lift).
        """
        import lift_ds as lds  # local import to avoid circular if used as lib

        lift_path   = Path(lift_path)
        output_path = Path(output_path) if output_path else \
                      lift_path.with_suffix(".enriched.lift")

        root    = lds.parse(str(lift_path), silence=True)
        updated = 0

        for entry in root.get_entry():
            lu = entry.get_lexical_unit()
            if not lu or not lu.get_form():
                continue
            orth = lu.get_form()[0].get_text() or ""

            # IPA — only add if no pronunciation exists
            if not entry.get_pronunciation():
                ipa_str = self.ipa_for_lift_entry(entry, lang_name, lang_code)
                if ipa_str:
                    pron    = lds.pronunciation()
                    form    = lds.form()
                    form.set_lang(f"{lang_code}-fonipa")
                    form.set_text(ipa_str)
                    pron.get_form().append(form)
                    entry.get_pronunciation().append(pron)

            # LIFT enrich prompt for semantic domains etc.
            senses = entry.get_sense()
            if senses:
                glosses = [{"lang": g.get_lang(), "text": g.get_text()}
                           for s in senses for g in s.get_gloss()]
                result = self.run(
                    PromptLibrary.LIFT_ENRICH,
                    headword=orth,
                    lang_name=lang_name,
                    lang_code=lang_code,
                    glosses_json=json.dumps(glosses),
                    definitions_json="[]",
                    examples_json="[]",
                    morph_type=entry.get_morph_type() or "",
                )
                if isinstance(result, dict):
                    # Add semantic domains
                    for sense in senses:
                        for dom in result.get("semantic_domains", []):
                            if dom:
                                sd = lds.semantic_domain()
                                sd.set_name(dom)
                                sense.get_semantic_domain().append(sd)
                    updated += 1

        with open(output_path, "w", encoding="utf-8") as fh:
            root.export(fh, 0)

        log.info("enrich_lift_file: %d entries enriched → %s", updated, output_path)
        return output_path

    def summarise_eaf_session(
        self,
        eaf_path: str | Path,
        lang_name: str,
        lang_code: str,
        orth_tier: str = "orth",
        trans_tier: str = "trans-en",
    ) -> dict:
        """
        Produce a structured session summary from an EAF file.
        """
        import eaf_ds as eds

        root   = eds.parse(str(eaf_path), silence=True)
        tiers  = {t.get_TIER_ID(): t for t in root.get_TIER()}
        ts_map = {
            ts.get_TIME_SLOT_ID(): ts.get_TIME_VALUE()
            for ts in root.get_TIME_ORDER().get_TIME_SLOT()
        }

        # Collect utterance data
        utterances   = []
        translations = []

        for tid, tier in tiers.items():
            if orth_tier in tid:
                for ann in tier.get_ANNOTATION():
                    ra = ann.get_REF_ANNOTATION()
                    if ra:
                        utterances.append(ra.get_ANNOTATION_VALUE() or "")
            if trans_tier in tid:
                for ann in tier.get_ANNOTATION():
                    ra = ann.get_REF_ANNOTATION()
                    if ra:
                        translations.append(ra.get_ANNOTATION_VALUE() or "")

        # Approximate duration from last time slot
        all_times = [ts.get_TIME_VALUE() or 0
                     for ts in root.get_TIME_ORDER().get_TIME_SLOT()]
        duration_ms = max(all_times) if all_times else 0

        return self.run(
            PromptLibrary.SESSION_SUMMARY,
            lang_name=lang_name,
            lang_code=lang_code,
            duration_ms=str(duration_ms),
            speaker_id="SP1",
            utterance_count=str(len(utterances)),
            utterances_json=json.dumps(utterances[:20]),
            translations_json=json.dumps(translations[:20]),
            notes="",
        )


# ─────────────────────────────────────────────────────────────────────────────
# Standalone demo
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse, textwrap
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    ap = argparse.ArgumentParser(
        description="Claude linguistics prompt library",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Available prompts:
          """ + "\n          ".join(PromptLibrary.list_prompts()))
    )
    ap.add_argument("--key", default=os.getenv("ANTHROPIC_API_KEY",""),
                    help="Anthropic API key (or set ANTHROPIC_API_KEY)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    # list
    sub.add_parser("list", help="List all available prompts")

    # show-prompt
    sp = sub.add_parser("show", help="Show a prompt's system text")
    sp.add_argument("name")

    # ipa
    ip = sub.add_parser("ipa", help="IPA transcription")
    ip.add_argument("orth"); ip.add_argument("lang_name"); ip.add_argument("lang_code")
    ip.add_argument("--lang-family", default=""); ip.add_argument("--phonemes", default="")

    # gloss
    gl = sub.add_parser("gloss", help="Leipzig glossing")
    gl.add_argument("morphemes"); gl.add_argument("free_translation")
    gl.add_argument("--source-lang", default="und"); gl.add_argument("--gloss-lang", default="en")

    # summarise-eaf
    se = sub.add_parser("summarise-eaf", help="Summarise EAF session")
    se.add_argument("eaf_path"); se.add_argument("lang_name"); se.add_argument("lang_code")

    # enrich-lift
    el = sub.add_parser("enrich-lift", help="Enrich LIFT file with Claude")
    el.add_argument("lift_path"); el.add_argument("lang_name"); el.add_argument("lang_code")
    el.add_argument("--output")

    args = ap.parse_args()

    if args.cmd == "list":
        for name in PromptLibrary.list_prompts():
            p = PromptLibrary.get(name)
            print(f"  {name:30s}  {p.task}")
        raise SystemExit(0)

    if args.cmd == "show":
        p = PromptLibrary.get(args.name)
        print(f"=== {p.name} ===\n{p.system}\n\n--- USER TEMPLATE ---\n{p.user_template}")
        raise SystemExit(0)

    cl = ClaudeAdapter(api_key=args.key)

    match args.cmd:
        case "ipa":
            result = cl.run(PromptLibrary.IPA_FROM_ORTH,
                            orth=args.orth, lang_name=args.lang_name,
                            lang_code=args.lang_code, lang_family=args.lang_family,
                            known_phonemes=args.phonemes, neighbours="")
            print(json.dumps(result, ensure_ascii=False, indent=2))

        case "gloss":
            result = cl.run(PromptLibrary.LEIPZIG_GLOSS,
                            morphemes=args.morphemes,
                            free_translation=args.free_translation,
                            source_lang=args.source_lang,
                            gloss_lang=args.gloss_lang,
                            paradigm_notes="")
            print(json.dumps(result, ensure_ascii=False, indent=2))

        case "summarise-eaf":
            result = cl.summarise_eaf_session(
                args.eaf_path, args.lang_name, args.lang_code
            )
            print(json.dumps(result, ensure_ascii=False, indent=2))

        case "enrich-lift":
            out = cl.enrich_lift_file(
                args.lift_path, args.lang_name, args.lang_code,
                output_path=args.output
            )
            print(f"Written: {out}")
