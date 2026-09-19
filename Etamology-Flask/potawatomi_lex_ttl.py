#!/usr/bin/env python3
"""
potawatomi_lex_ttl.py

Convert:

    potawatomi_full.tmx
            |
            v
    potawatomi_full.ttl

TMX language pair:

    pot -> en

RDF vocabulary:

    OntoLex-Lemon
    LexInfo
    Dublin Core Terms
    SKOS
    PROV-O
    Glottolog

Language:

    Potawatomi
    ISO 639-3: pot
    Glottocode: pota1247
    Family: Algic

This is intentionally a conservative TMX -> RDF conversion.

English translations are initially represented as lexical sense
definitions rather than asserting that the English gloss is a
confirmed ontology concept/cognate.

That distinction is important for later Miami-Illinois /
Potawatomi comparison.
"""

from pathlib import Path
import hashlib
import re
import xml.etree.ElementTree as ET

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, RDF, RDFS, SKOS, XSD


# ---------------------------------------------------------------------------
# Files
# ---------------------------------------------------------------------------

TMX_FILE = Path("potawatomi_full.tmx")
TTL_FILE = Path("potawatomi_full.ttl")


# ---------------------------------------------------------------------------
# Base URI
#
# Change this later to the permanent URI for your Etamology-Flask dataset.
# ---------------------------------------------------------------------------

BASE = "https://wiwkwebthegen.com/rdf/potawatomi/"

LEXICON_URI = URIRef(BASE + "lexicon")


# ---------------------------------------------------------------------------
# Ontologies
# ---------------------------------------------------------------------------

ONTOLEX = Namespace(
    "http://www.w3.org/ns/lemon/ontolex#"
)

LEXINFO = Namespace(
    "http://www.lexinfo.net/ontology/3.0/lexinfo#"
)

LIME = Namespace(
    "http://www.w3.org/ns/lemon/lime#"
)

PROV = Namespace(
    "http://www.w3.org/ns/prov#"
)

LEXVO = Namespace(
    "http://lexvo.org/id/iso639-3/"
)

# Glottolog language URI
GLOTTOLOG_POT = URIRef(
    "https://glottolog.org/resource/languoid/id/pota1247"
)

# Glottolog Algic URI supplied for the project
GLOTTOLOG_ALGIC = URIRef(
    "https://glottolog.org/resource/languoid/id/algi1248"
)

# Potawatomi Lexvo/ISO identifier
LEXVO_POT = URIRef(
    "http://lexvo.org/id/iso639-3/pot"
)


# ---------------------------------------------------------------------------
# Dataset metadata
# ---------------------------------------------------------------------------

DATASET_TITLE = (
    "Potawatomi Lexicon — Wiwkwébthëgen"
)

DATASET_DESCRIPTION = (
    "Potawatomi lexical data converted from TMX into "
    "OntoLex-Lemon RDF."
)

SOURCE_NAME = "Wiwkwébthëgen"

SOURCE_URL = URIRef(
    "https://wiwkwebthegen.com/dictionary"
)


# ---------------------------------------------------------------------------
# XML helpers
# ---------------------------------------------------------------------------

def local_name(tag):
    """
    Remove XML namespace from an element name.
    """

    if "}" in tag:
        return tag.rsplit("}", 1)[1]

    return tag


def normalize_text(value):
    if value is None:
        return ""

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value.strip()


def find_tuv(tu, language):
    """
    Find a TMX tuv matching an ISO language code.
    """

    for child in tu:

        if local_name(child.tag) != "tuv":
            continue

        lang = (
            child.attrib.get(
                "{http://www.w3.org/XML/1998/namespace}lang"
            )
            or child.attrib.get("lang")
            or ""
        )

        if lang.lower() == language.lower():
            seg = next(
                (
                    x
                    for x in child
                    if local_name(x.tag) == "seg"
                ),
                None,
            )

            if seg is not None:
                return normalize_text(
                    "".join(seg.itertext())
                )

    return ""


def get_props(tu):
    props = {}

    for child in tu:

        if local_name(child.tag) != "prop":
            continue

        key = child.attrib.get("type")

        if not key:
            continue

        value = normalize_text(
            "".join(child.itertext())
        )

        props.setdefault(
            key,
            [],
        ).append(value)

    return props


# ---------------------------------------------------------------------------
# Stable URI generation
# ---------------------------------------------------------------------------

def slugify(value):
    value = normalize_text(value)

    value = value.lower()

    value = re.sub(
        r"\s+",
        "-",
        value,
    )

    value = re.sub(
        r"[^a-z0-9\u0080-\uffff_-]",
        "",
        value,
    )

    return value[:120]


def lexical_entry_uri(headword, tuid=None):
    """
    Generate a stable URI.

    Prefer the TMX tuid when available, but retain the readable headword.
    """

    slug = slugify(headword)

    if not slug:
        slug = "entry"

    if tuid:
        digest = hashlib.sha1(
            tuid.encode("utf-8")
        ).hexdigest()[:8]

        return URIRef(
            BASE + "entry/" + slug + "-" + digest
        )

    return URIRef(
        BASE + "entry/" + slug
    )


def sense_uri(entry_uri):
    return URIRef(
        str(entry_uri) + "/sense"
    )


def form_uri(entry_uri):
    return URIRef(
        str(entry_uri) + "/form"
    )


# ---------------------------------------------------------------------------
# RDF initialization
# ---------------------------------------------------------------------------

def create_graph():
    graph = Graph()

    graph.bind(
        "ontolex",
        ONTOLEX,
    )

    graph.bind(
        "lexinfo",
        LEXINFO,
    )

    graph.bind(
        "lime",
        LIME,
    )

    graph.bind(
        "lexvo",
        LEXVO,
    )

    graph.bind(
        "dct",
        DCTERMS,
    )

    graph.bind(
        "skos",
        SKOS,
    )

    graph.bind(
        "prov",
        PROV,
    )

    graph.bind(
        "rdfs",
        RDFS,
    )

    return graph


# ---------------------------------------------------------------------------
# Lexicon metadata
# ---------------------------------------------------------------------------

def add_lexicon_metadata(graph):
    lexicon = LEXICON_URI

    graph.add(
        (
            lexicon,
            RDF.type,
            ONTOLEX.Lexicon,
        )
    )

    graph.add(
        (
            lexicon,
            DCTERMS.title,
            Literal(
                DATASET_TITLE,
                lang="en",
            ),
        )
    )

    graph.add(
        (
            lexicon,
            DCTERMS.description,
            Literal(
                DATASET_DESCRIPTION,
                lang="en",
            ),
        )
    )

    graph.add(
        (
            lexicon,
            DCTERMS.language,
            Literal(
                "pot",
            ),
        )
    )

    # Link language to Lexvo/ISO 639-3.
    graph.add(
        (
            lexicon,
            LIME.language,
            Literal("pot"),
        )
    )

    graph.add(
        (
            lexicon,
            DCTERMS.language,
            LEXVO_POT,
        )
    )

    # Glottolog identity.
    graph.add(
        (
            lexicon,
            SKOS.broader,
            GLOTTOLOG_POT,
        )
    )

    graph.add(
        (
            GLOTTOLOG_POT,
            RDF.type,
            SKOS.Concept,
        )
    )

    graph.add(
        (
            GLOTTOLOG_POT,
            SKOS.prefLabel,
            Literal(
                "Potawatomi",
                lang="en",
            ),
        )
    )

    graph.add(
        (
            GLOTTOLOG_POT,
            SKOS.broader,
            GLOTTOLOG_ALGIC,
        )
    )

    graph.add(
        (
            GLOTTOLOG_ALGIC,
            RDF.type,
            SKOS.Concept,
        )
    )

    graph.add(
        (
            GLOTTOLOG_ALGIC,
            SKOS.prefLabel,
            Literal(
                "Algic",
                lang="en",
            ),
        )
    )

    # Source.
    graph.add(
        (
            lexicon,
            DCTERMS.source,
            SOURCE_URL,
        )
    )

    graph.add(
        (
            lexicon,
            DCTERMS.publisher,
            Literal(
                SOURCE_NAME,
                lang="en",
            ),
        )
    )


# ---------------------------------------------------------------------------
# Lexical entry
# ---------------------------------------------------------------------------

def add_entry(
    graph,
    headword,
    english,
    tuid=None,
    props=None,
):
    """
    Add:

        LexicalEntry
            |
            +-- canonicalForm
            |
            +-- sense
                    |
                    +-- definition
    """

    props = props or {}

    entry = lexical_entry_uri(
        headword,
        tuid,
    )

    form = form_uri(entry)

    sense = sense_uri(entry)

    # ---------------------------------------------------------------
    # Entry
    # ---------------------------------------------------------------

    graph.add(
        (
            entry,
            RDF.type,
            ONTOLEX.LexicalEntry,
        )
    )

    graph.add(
        (
            LEXICON_URI,
            ONTOLEX.entry,
            entry,
        )
    )

    graph.add(
        (
            entry,
            DCTERMS.language,
            LEXVO_POT,
        )
    )

    # ---------------------------------------------------------------
    # Form
    # ---------------------------------------------------------------

    graph.add(
        (
            entry,
            ONTOLEX.canonicalForm,
            form,
        )
    )

    graph.add(
        (
            form,
            RDF.type,
            ONTOLEX.Form,
        )
    )

    graph.add(
        (
            form,
            ONTOLEX.writtenRep,
            Literal(
                headword,
                lang="pot",
            ),
        )
    )

    # ---------------------------------------------------------------
    # Sense
    # ---------------------------------------------------------------

    graph.add(
        (
            entry,
            ONTOLEX.sense,
            sense,
        )
    )

    graph.add(
        (
            sense,
            RDF.type,
            ONTOLEX.LexicalSense,
        )
    )

    if english:

        graph.add(
            (
                sense,
                SKOS.definition,
                Literal(
                    english,
                    lang="en",
                ),
            )
        )

        graph.add(
            (
                sense,
                RDFS.comment,
                Literal(
                    english,
                    lang="en",
                ),
            )
        )

    # ---------------------------------------------------------------
    # Source metadata
    # ---------------------------------------------------------------

    source_url = (
        props.get("source_url", [""])[0]
        if props.get("source_url")
        else ""
    )

    if source_url:

        graph.add(
            (
                entry,
                DCTERMS.source,
                URIRef(source_url),
            )
        )

    # ---------------------------------------------------------------
    # Audio
    # ---------------------------------------------------------------

    for audio_url in props.get(
        "audio_url",
        [],
    ):

        graph.add(
            (
                entry,
                DCTERMS.references,
                URIRef(audio_url),
            )
        )

    # ---------------------------------------------------------------
    # Entry type
    # ---------------------------------------------------------------

    if "morpheme" in (
        props.get("entry_type", [])
    ):

        graph.add(
            (
                entry,
                LEXINFO.morphologicalPattern,
                Literal("morpheme"),
            )
        )

    return entry


# ---------------------------------------------------------------------------
# TMX conversion
# ---------------------------------------------------------------------------

def convert():
    if not TMX_FILE.exists():
        raise FileNotFoundError(
            f"Missing input file: {TMX_FILE}"
        )

    tree = ET.parse(
        TMX_FILE
    )

    root = tree.getroot()

    graph = create_graph()

    add_lexicon_metadata(
        graph
    )

    count = 0

    for tu in root.iter():

        if local_name(tu.tag) != "tu":
            continue

        pot = find_tuv(
            tu,
            "pot",
        )

        english = find_tuv(
            tu,
            "en",
        )

        if not pot:
            continue

        tuid = tu.attrib.get(
            "tuid"
        )

        props = get_props(
            tu
        )

        add_entry(
            graph,
            pot,
            english,
            tuid=tuid,
            props=props,
        )

        count += 1

    graph.serialize(
        destination=str(TTL_FILE),
        format="turtle",
    )

    print(
        f"Converted {count} Potawatomi entries."
    )

    print(
        f"Input : {TMX_FILE}"
    )

    print(
        f"Output: {TTL_FILE}"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    convert()
