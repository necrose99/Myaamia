#!/usr/bin/env python3
"""
potawatomi_lex_ttl.py

Convert Potawatomi TMX lexical data into OntoLex-Lemon RDF/Turtle.

Input:
    potawatomi_full.tmx

Output:
    potawatomi_full.ttl

Design:
    TMX
      |
      +-- OntoLex-Lemon lexical entry/form/sense
      |
      +-- LexInfo POS when known
      |
      +-- Algic/Potawatomi linguistic metadata
            - Animate / Inanimate
            - Verb
            - Noun
            - VAI / VII / VTI / VTA
            - morphology metadata when explicitly supplied
      |
      +-- Glottolog language/family references
      +-- source URL / audio / provenance

Important:
    Do NOT infer Potawatomi grammatical category from the English gloss alone.

    Example:
        English "red"
        does NOT imply English adjective == Potawatomi adjective.

    Citizen Potawatomi Nation documentation explicitly describes
    VII verbs whose English translations may be adjectives such as
    "red", "big", and "long".
"""

from __future__ import annotations

import argparse
import hashlib
import re
import unicodedata
from pathlib import Path
from urllib.parse import quote
import xml.etree.ElementTree as ET

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SKOS, XSD


# ---------------------------------------------------------------------------
# Namespaces
# ---------------------------------------------------------------------------

ONTOLEX = Namespace("http://www.w3.org/ns/lemon/ontolex#")
LEXINFO = Namespace("http://www.lexinfo.net/ontology/3.0/lexinfo#")

# Shared ontology for the user's Algic / Etamology project.
ALGIC = Namespace(
    "https://github.com/necrose99/Myaamia/ontology/algic#"
)

# Potawatomi-specific namespace.
POT = Namespace(
    "https://github.com/necrose99/Myaamia/ontology/potawatomi#"
)

# Lexvo language identifier.
LEXVO = Namespace("http://lexvo.org/id/iso639-3/")

# Glottolog.
GLOTTOLOG = Namespace(
    "https://glottolog.org/resource/languoid/id/"
)

# Source vocabulary.
WIWK = Namespace(
    "https://wiwkwebthegen.com/"
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

LANGUAGE = "pot"

GLOTTOLOG_POTAWATOMI = GLOTTOLOG.pota1247
GLOTTOLOG_ALGIC = GLOTTOLOG.algi1248

SOURCE_DICTIONARY = URIRef(
    "https://wiwkwebthegen.com/dictionary"
)

SOURCE_DOMAIN = "https://wiwkwebthegen.com"

DEFAULT_INPUT = Path("potawatomi_full.tmx")
DEFAULT_OUTPUT = Path("potawatomi_full.ttl")


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

def clean_text(value: str | None) -> str:
    """Normalize whitespace while preserving Unicode."""
    if not value:
        return ""

    value = unicodedata.normalize("NFC", value)
    return re.sub(r"\s+", " ", value).strip()


def slugify(value: str) -> str:
    """
    Unicode-safe-ish URI slug.

    Keep letters/numbers where possible, replace everything else.
    """
    value = clean_text(value)

    value = unicodedata.normalize("NFKD", value)
    value = "".join(
        ch for ch in value
        if not unicodedata.combining(ch)
    )

    value = re.sub(r"[^A-Za-z0-9]+", "-", value)
    value = value.strip("-").lower()

    return value or "entry"


def stable_id(*parts: str) -> str:
    """Stable short SHA256 identifier."""
    raw = "\x1f".join(clean_text(p) for p in parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def first_text(element: ET.Element | None) -> str:
    if element is None:
        return ""

    return clean_text(
        "".join(element.itertext())
    )


# ---------------------------------------------------------------------------
# TMX helpers
# ---------------------------------------------------------------------------

def get_prop(tu: ET.Element, names: set[str]) -> str:
    """
    Find a TMX <prop> by property name.

    Handles:
        <prop type="audio">...</prop>
        <prop type="source_url">...</prop>
        etc.
    """
    for prop in tu.findall(".//prop"):
        prop_type = (
            prop.attrib.get("type")
            or prop.attrib.get("name")
            or ""
        ).strip().lower()

        if prop_type in names:
            return clean_text(first_text(prop))

    return ""


def get_all_props(tu: ET.Element) -> dict[str, str]:
    props = {}

    for prop in tu.findall(".//prop"):
        key = (
            prop.attrib.get("type")
            or prop.attrib.get("name")
            or ""
        ).strip().lower()

        value = clean_text(first_text(prop))

        if key:
            props[key] = value

    return props


def get_tuv_text(tuv: ET.Element) -> str:
    """
    Extract TMX <seg> text.
    """
    seg = tuv.find("./seg")

    if seg is not None:
        return clean_text(first_text(seg))

    return clean_text(first_text(tuv))


def get_language(tuv: ET.Element) -> str:
    return (
        tuv.attrib.get("{http://www.w3.org/XML/1998/namespace}lang")
        or tuv.attrib.get("lang")
        or tuv.attrib.get("xml:lang")
        or ""
    ).lower()


def extract_tuvs(tu: ET.Element) -> dict[str, list[str]]:
    """
    Return:
        {
            "pot": [...],
            "en": [...]
        }

    Supports multiple TUVs for a language.
    """
    result: dict[str, list[str]] = {}

    for tuv in tu.findall(".//tuv"):
        lang = get_language(tuv)

        if not lang:
            continue

        # Accept things such as:
        # pot
        # pot-US
        # en
        # en-US
        lang = lang.split("-")[0]

        value = get_tuv_text(tuv)

        if value:
            result.setdefault(lang, []).append(value)

    return result


# ---------------------------------------------------------------------------
# Potawatomi linguistic classification
# ---------------------------------------------------------------------------

def normalize_category(value: str) -> str:
    value = clean_text(value).lower()

    # Normalize common punctuation.
    value = value.replace("_", " ")
    value = value.replace("-", " ")

    return value


VERB_CLASSES = {
    "vai": ALGIC.VAI,
    "v ai": ALGIC.VAI,
    "animate intransitive": ALGIC.VAI,
    "animate intransitive verb": ALGIC.VAI,

    "vii": ALGIC.VII,
    "v ii": ALGIC.VII,
    "inanimate intransitive": ALGIC.VII,
    "inanimate intransitive verb": ALGIC.VII,

    "vti": ALGIC.VTI,
    "v ti": ALGIC.VTI,
    "transitive inanimate": ALGIC.VTI,
    "transitive inanimate verb": ALGIC.VTI,

    "vta": ALGIC.VTA,
    "v ta": ALGIC.VTA,
    "transitive animate": ALGIC.VTA,
    "transitive animate verb": ALGIC.VTA,
}


POS_MAP = {
    "verb": LEXINFO.verb,
    "v": LEXINFO.verb,

    "noun": LEXINFO.noun,
    "n": LEXINFO.noun,

    "adverb": LEXINFO.adverb,
    "adv": LEXINFO.adverb,

    "adjective": LEXINFO.adjective,
    "adj": LEXINFO.adjective,

    "particle": LEXINFO.particle,
}


def classify_entry(props: dict[str, str]) -> tuple[URIRef | None, URIRef | None]:
    """
    Return:
        (lexinfo POS, algic verb class)

    Only use explicit metadata.

    We deliberately DO NOT classify from the English gloss.
    """

    pos_raw = ""

    for key in (
        "pos",
        "part_of_speech",
        "part-of-speech",
        "word_class",
        "word-class",
        "category",
        "grammatical_category",
        "grammatical-category",
    ):
        if props.get(key):
            pos_raw = props[key]
            break

    verb_raw = ""

    for key in (
        "verb_class",
        "verb-class",
        "verbclass",
        "class",
    ):
        if props.get(key):
            verb_raw = props[key]
            break

    pos = POS_MAP.get(
        normalize_category(pos_raw)
    )

    verb_class = VERB_CLASSES.get(
        normalize_category(verb_raw)
    )

    # If explicit VAI/VII/VTI/VTA exists, it is inherently a verb.
    if verb_class:
        pos = LEXINFO.verb

    return pos, verb_class


def get_animacy(props: dict[str, str]) -> URIRef | None:
    """
    Extract explicit animacy only.

    Do not infer animacy merely from an English translation.
    """
    for key in (
        "animacy",
        "animate",
        "noun_class",
        "gender",
    ):
        value = normalize_category(props.get(key, ""))

        if value in {
            "animate",
            "anim",
            "a",
        }:
            return ALGIC.Animate

        if value in {
            "inanimate",
            "inan",
            "i",
        }:
            return ALGIC.Inanimate

    return None


# ---------------------------------------------------------------------------
# RDF setup
# ---------------------------------------------------------------------------

def bind_namespaces(graph: Graph) -> None:
    graph.bind("ontolex", ONTOLEX)
    graph.bind("lexinfo", LEXINFO)

    graph.bind("algic", ALGIC)
    graph.bind("pot", POT)

    graph.bind("lexvo", LEXVO)
    graph.bind("glottolog", GLOTTOLOG)

    graph.bind("dcterms", DCTERMS)
    graph.bind("skos", SKOS)

    graph.bind("rdf", RDF)
    graph.bind("rdfs", RDFS)
    graph.bind("owl", OWL)
    graph.bind("xsd", XSD)


# ---------------------------------------------------------------------------
# Ontology declarations
# ---------------------------------------------------------------------------

def add_ontology_metadata(graph: Graph) -> None:
    """
    Minimal local vocabulary declarations.

    These can later move to algic.ttl / potawatomi.ttl.
    """

    algic_ontology = URIRef(
        "https://github.com/necrose99/Myaamia/ontology/algic"
    )

    pot_ontology = URIRef(
        "https://github.com/necrose99/Myaamia/ontology/potawatomi"
    )

    graph.add(
        (algic_ontology, RDF.type, OWL.Ontology)
    )

    graph.add(
        (
            algic_ontology,
            RDFS.label,
            Literal(
                "Shared Algic linguistic vocabulary",
                lang="en",
            ),
        )
    )

    graph.add(
        (pot_ontology, RDF.type, OWL.Ontology)
    )

    graph.add(
        (
            pot_ontology,
            RDFS.label,
            Literal(
                "Potawatomi linguistic vocabulary",
                lang="en",
            ),
        )
    )

    # ------------------------------------------------------------------
    # Animacy
    # ------------------------------------------------------------------

    for cls, label in (
        (ALGIC.Animate, "Animate"),
        (ALGIC.Inanimate, "Inanimate"),
        (ALGIC.Verb, "Verb"),
        (ALGIC.Noun, "Noun"),
        (ALGIC.Modifier, "Modifier"),
        (ALGIC.Adverb, "Adverb"),
        (ALGIC.Particle, "Particle"),
        (ALGIC.LexiconStatistics, "Lexicon statistics"),
        (ALGIC.Initial, "Initial"),
        (ALGIC.Medial, "Medial"),
        (ALGIC.Final, "Final"),
    ):
        graph.add((cls, RDF.type, OWL.Class))
        graph.add(
            (
                cls,
                RDFS.label,
                Literal(label, lang="en"),
            )
        )

    # ------------------------------------------------------------------
    # Potawatomi verb classes
    # ------------------------------------------------------------------

    verb_classes = {
        ALGIC.VAI: "VAI — animate intransitive verb",
        ALGIC.VII: "VII — inanimate intransitive verb",
        ALGIC.VTI: "VTI — transitive inanimate verb",
        ALGIC.VTA: "VTA — transitive animate verb",
    }

    for cls, label in verb_classes.items():
        graph.add((cls, RDF.type, OWL.Class))
        graph.add(
            (
                cls,
                RDFS.subClassOf,
                ALGIC.Verb,
            )
        )
        graph.add(
            (
                cls,
                RDFS.label,
                Literal(label, lang="en"),
            )
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    properties = {
        ALGIC.verbClass: "verb class",
        ALGIC.animacy: "animacy",
        ALGIC.hasInitial: "has initial",
        ALGIC.hasMedial: "has medial",
        ALGIC.hasFinal: "has final",
        ALGIC.classificationSource: "classification source",
        ALGIC.analysisConfidence: "analysis confidence",
    }

    for prop, label in properties.items():
        graph.add((prop, RDF.type, OWL.ObjectProperty))
        graph.add(
            (
                prop,
                RDFS.label,
                Literal(label, lang="en"),
            )
        )


# ---------------------------------------------------------------------------
# Lexicon
# ---------------------------------------------------------------------------

def create_lexicon(graph: Graph) -> URIRef:
    lexicon = URIRef(
        "https://github.com/necrose99/Myaamia/lexicon/potawatomi"
    )

    graph.add(
        (lexicon, RDF.type, ONTOLEX.Lexicon)
    )

    graph.add(
        (
            lexicon,
            DCTERMS.language,
            LEXVO.pot,
        )
    )

    graph.add(
        (
            lexicon,
            DCTERMS.source,
            SOURCE_DICTIONARY,
        )
    )

    graph.add(
        (
            lexicon,
            DCTERMS.references,
            GLOTTOLOG_POTAWATOMI,
        )
    )

    graph.add(
        (
            lexicon,
            DCTERMS.references,
            GLOTTOLOG_ALGIC,
        )
    )

    graph.add(
        (
            lexicon,
            SKOS.note,
            Literal(
                "Potawatomi lexical data converted from TMX.",
                lang="en",
            ),
        )
    )

    return lexicon


# ---------------------------------------------------------------------------
# Entry URI
# ---------------------------------------------------------------------------

def make_entry_uri(
    headword: str,
    tuid: str,
    source_url: str,
) -> URIRef:

    if source_url:
        digest = stable_id(source_url)
    elif tuid:
        digest = stable_id(tuid, headword)
    else:
        digest = stable_id(headword)

    slug = slugify(headword)

    return URIRef(
        f"https://github.com/necrose99/Myaamia/lexicon/potawatomi/"
        f"{slug}-{digest}"
    )


# ---------------------------------------------------------------------------
# Individual TMX entry
# ---------------------------------------------------------------------------

def convert_tu(
    graph: Graph,
    lexicon: URIRef,
    tu: ET.Element,
    index: int,
) -> bool:

    tuid = clean_text(tu.attrib.get("tuid", ""))

    tuvs = extract_tuvs(tu)

    pot_forms = tuvs.get("pot", [])
    en_glosses = tuvs.get("en", [])

    if not pot_forms:
        return False

    headword = pot_forms[0]
    english_gloss = en_glosses[0] if en_glosses else ""

    props = get_all_props(tu)

    source_url = (
        props.get("source_url")
        or props.get("source")
        or props.get("url")
        or ""
    )

    audio_url = (
        props.get("audio")
        or props.get("audio_url")
        or props.get("audio-url")
        or ""
    )

    # If crawler stored the dictionary URL as a prop.
    if (
        not source_url
        and props.get("dictionary_url")
    ):
        source_url = props["dictionary_url"]

    # Fallback.
    if not source_url:
        source_url = (
            f"{SOURCE_DOMAIN}/dictionary-word/"
            f"{quote(headword, safe='')}"
        )

    entry = make_entry_uri(
        headword,
        tuid,
        source_url,
    )

    # ---------------------------------------------------------------
    # Entry
    # ---------------------------------------------------------------

    graph.add(
        (entry, RDF.type, ONTOLEX.LexicalEntry)
    )

    graph.add(
        (entry, DCTERMS.language, LEXVO.pot)
    )

    graph.add(
        (entry, DCTERMS.source, URIRef(source_url))
    )

    graph.add(
        (entry, DCTERMS.references, GLOTTOLOG_POTAWATOMI)
    )

    graph.add(
        (entry, DCTERMS.references, GLOTTOLOG_ALGIC)
    )

    # ---------------------------------------------------------------
    # Canonical form
    # ---------------------------------------------------------------

    form_id = stable_id(
        str(entry),
        "canonical",
        headword,
    )

    form = URIRef(
        f"{entry}/form/{form_id}"
    )

    graph.add(
        (entry, ONTOLEX.canonicalForm, form)
    )

    graph.add(
        (form, RDF.type, ONTOLEX.Form)
    )

    graph.add(
        (
            form,
            ONTOLEX.writtenRep,
            Literal(headword, lang="pot"),
        )
    )

    # ---------------------------------------------------------------
    # Sense
    # ---------------------------------------------------------------

    sense = URIRef(
        f"{entry}/sense/{stable_id(str(entry), english_gloss)}"
    )

    graph.add(
        (entry, ONTOLEX.sense, sense)
    )

    graph.add(
        (sense, RDF.type, ONTOLEX.LexicalSense)
    )

    if english_gloss:
        graph.add(
            (
                sense,
                SKOS.definition,
                Literal(
                    english_gloss,
                    lang="en",
                ),
            )
        )

    # ---------------------------------------------------------------
    # Part of speech / verb class
    # ---------------------------------------------------------------

    pos, verb_class = classify_entry(props)

    if pos:
        graph.add(
            (
                entry,
                LEXINFO.partOfSpeech,
                pos,
            )
        )

    if verb_class:
        graph.add(
            (
                entry,
                ALGIC.verbClass,
                verb_class,
            )
        )

        graph.add(
            (
                entry,
                ALGIC.classificationSource,
                URIRef(source_url),
            )
        )

        graph.add(
            (
                entry,
                RDF.type,
                ALGIC.Verb,
            )
        )

    # ---------------------------------------------------------------
    # Animacy
    # ---------------------------------------------------------------

    animacy = get_animacy(props)

    if animacy:
        graph.add(
            (
                entry,
                ALGIC.animacy,
                animacy,
            )
        )

    # ---------------------------------------------------------------
    # Morphology
    #
    # Only emit what the source explicitly supplied.
    # ---------------------------------------------------------------

    initial = (
        props.get("initial")
        or props.get("morph_initial")
        or props.get("morph-initial")
    )

    medial = (
        props.get("medial")
        or props.get("morph_medial")
        or props.get("morph-medial")
    )

    final = (
        props.get("final")
        or props.get("morph_final")
        or props.get("morph-final")
    )

    if initial:
        initial_uri = URIRef(
            f"{entry}/morph/initial/"
            f"{stable_id(initial)}"
        )

        graph.add(
            (entry, ALGIC.hasInitial, initial_uri)
        )

        graph.add(
            (initial_uri, RDF.type, ALGIC.Initial)
        )

        graph.add(
            (
                initial_uri,
                RDFS.label,
                Literal(initial, lang="pot"),
            )
        )

    if medial:
        medial_uri = URIRef(
            f"{entry}/morph/medial/"
            f"{stable_id(medial)}"
        )

        graph.add(
            (entry, ALGIC.hasMedial, medial_uri)
        )

        graph.add(
            (medial_uri, RDF.type, ALGIC.Medial)
        )

        graph.add(
            (
                medial_uri,
                RDFS.label,
                Literal(medial, lang="pot"),
            )
        )

    if final:
        final_uri = URIRef(
            f"{entry}/morph/final/"
            f"{stable_id(final)}"
        )

        graph.add(
            (entry, ALGIC.hasFinal, final_uri)
        )

        graph.add(
            (final_uri, RDF.type, ALGIC.Final)
        )

        graph.add(
            (
                final_uri,
                RDFS.label,
                Literal(final, lang="pot"),
            )
        )

    # ---------------------------------------------------------------
    # Audio
    # ---------------------------------------------------------------

    if audio_url:
        graph.add(
            (
                entry,
                DCTERMS.references,
                URIRef(audio_url),
            )
        )

    # ---------------------------------------------------------------
    # Crawler metadata
    # ---------------------------------------------------------------

    if tuid:
        graph.add(
            (
                entry,
                POT.tmxId,
                Literal(tuid),
            )
        )

    graph.add(
        (
            entry,
            POT.dictionaryEntry,
            URIRef(source_url),
        )
    )

    # ---------------------------------------------------------------
    # Add all Potawatomi variants from TMX.
    # ---------------------------------------------------------------

    for n, variant in enumerate(pot_forms):
        if variant == headword:
            continue

        variant_form = URIRef(
            f"{entry}/form/{stable_id(str(entry), variant)}"
        )

        graph.add(
            (
                entry,
                ONTOLEX.otherForm,
                variant_form,
            )
        )

        graph.add(
            (
                variant_form,
                RDF.type,
                ONTOLEX.Form,
            )
        )

        graph.add(
            (
                variant_form,
                ONTOLEX.writtenRep,
                Literal(variant, lang="pot"),
            )
        )

    graph.add(
        (
            lexicon,
            ONTOLEX.entry,
            entry,
        )
    )

    return True


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------

def add_source_estimate(graph: Graph) -> None:
    """
    Store the approximate 70% source claim separately from
    computed dictionary statistics.

    This is intentionally NOT applied to individual entries.
    """

    stats = POT.WIWKSourceEstimate

    graph.add(
        (stats, RDF.type, ALGIC.LexiconStatistics)
    )

    graph.add(
        (
            stats,
            RDFS.label,
            Literal(
                "WIWK / Potawatomi verb proportion estimate",
                lang="en",
            ),
        )
    )

    graph.add(
        (
            stats,
            POT.estimatedVerbProportion,
            Literal(
                "0.70",
                datatype=XSD.decimal,
            ),
        )
    )

    graph.add(
        (
            stats,
            POT.estimateQualifier,
            Literal(
                "Approximate source-reported/educational estimate; "
                "not a computed proportion of this TMX dataset.",
                lang="en",
            ),
        )
    )

    graph.add(
        (
            stats,
            DCTERMS.source,
            SOURCE_DICTIONARY,
        )
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:

    parser = argparse.ArgumentParser(
        description="Convert Potawatomi TMX to OntoLex-Lemon Turtle."
    )

    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"Input TMX (default: {DEFAULT_INPUT})",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output TTL (default: {DEFAULT_OUTPUT})",
    )

    parser.add_argument(
        "--no-source-estimate",
        action="store_true",
        help="Do not include the approximate 70%% source statistic.",
    )

    args = parser.parse_args()

    if not args.input.exists():
        raise SystemExit(
            f"ERROR: TMX file not found: {args.input}"
        )

    graph = Graph()
    bind_namespaces(graph)

    add_ontology_metadata(graph)

    lexicon = create_lexicon(graph)

    if not args.no_source_estimate:
        add_source_estimate(graph)

    tree = ET.parse(args.input)
    root = tree.getroot()

    tus = root.findall(".//tu")

    converted = 0
    skipped = 0

    for index, tu in enumerate(tus, start=1):

        try:
            if convert_tu(
                graph,
                lexicon,
                tu,
                index,
            ):
                converted += 1
            else:
                skipped += 1

        except Exception as exc:
            skipped += 1

            print(
                f"WARNING: entry {index} failed: {exc}"
            )

    args.output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    graph.serialize(
        destination=str(args.output),
        format="turtle",
    )

    print()
    print("Potawatomi TMX → RDF complete")
    print("--------------------------------")
    print(f"Input:      {args.input}")
    print(f"Output:     {args.output}")
    print(f"TMX entries: {len(tus)}")
    print(f"Converted:  {converted}")
    print(f"Skipped:    {skipped}")
    print(f"RDF triples:{len(graph)}")
    print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
