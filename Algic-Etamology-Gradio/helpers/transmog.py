# helpers/transmog.py
import io
import json
import re
import xml.etree.ElementTree as ET
from rdflib import Graph, Namespace, Literal, URIRef

# Core Namespaces for Ontolex-Lemon Models
ONTOLEX = Namespace("http://w3.org")
LEXINFO = Namespace("http://lexinfo.net")
SKOS    = Namespace("http://w3.org")

class TransmogEngine:
    @staticmethod
    def parse_extended_tmx(tmx_bytes: bytes) -> list[dict]:
        """
        Parses TMX files tracking complex properties (like provenance fields, 
        regex patterns, and citation metadata flags).
        """
        root = ET.fromstring(tmx_bytes)
        entries = []
        
        for tu in root.iter("tu"):
            # Extract standard custom property maps
            props = {}
            for prop in tu.findall("prop"):
                p_type = prop.get("type")
                if p_type:
                    props[p_type.lower()] = (prop.text or "").strip()
            
            tuvs = list(tu.findall("tuv"))
            if len(tuvs) < 2:
                continue
                
            # Isolate text segment strings
            src_word = (tuvs[0].findtext("seg") or "").strip()
            tgt_word = (tuvs[1].findtext("seg") or "").strip()
            
            # Clean up content using a regex pattern
            src_clean = re.sub(r'\s+', ' ', src_word)
            
            if src_clean:
                entries.append({
                    "form": src_clean,
                    "gloss_en": tgt_word,
                    "proto_form": props.get("x-proto-algonquian") or props.get("x-pa") or "",
                    # Capture deep archival fields from custom tags
                    "source_url": props.get("x-provenance") or props.get("provenance") or "",
                    "notes": props.get("x-citation") or props.get("note") or "",
                    "source_type": "extended-tmx"
                })
        return entries

    @staticmethod
    def parse_xdxf(xml_bytes: bytes) -> list[dict]:
        """Parses XDXF structures into standard translation records."""
        root = ET.fromstring(xml_bytes)
        entries = []
        for ar in root.findall(".//ar"):
            k = ar.findtext("k")
            def_text = "".join(ar.itertext()).replace(k or "", "", 1).strip()
            if k:
                entries.append({
                    "form": k.strip(),
                    "gloss_en": def_text,
                    "source_type": "xdxf"
                })
        return entries

    @staticmethod
    def parse_ontolex_lemon_ttl(ttl_bytes: bytes) -> list[dict]:
        """Parses Turtle syntax files matching ontolex-lemon topologies."""
        g = Graph()
        g.parse(data=ttl_bytes.decode("utf-8"), format="turtle")
        entries = []
        
        for entry_uri, canonical_form in g.subject_objects(predicate=ONTOLEX.canonicalForm):
            rep = g.value(subject=canonical_form, predicate=ONTOLEX.writtenRep)
            sense = g.value(subject=entry_uri, predicate=ONTOLEX.sense)
            definition = g.value(subject=sense, predicate=SKOS.definition) if sense else None
            
            if rep:
                entries.append({
                    "form": str(rep),
                    "gloss_en": str(definition) if definition else "",
                    "source_type": "lemon-ttl"
                })
        return entries
# Add this method inside your TransmogEngine class in helpers/transmog.py

@staticmethod
def parse_elan_eaf(eaf_bytes: bytes) -> list[dict]:
    """
    Parses ELAN EAF XML byte streams directly.
    Extracts time-aligned alignable transcription segments and 
    cross-references child structural translation nodes.
    """
    root = ET.fromstring(eaf_bytes)
    entries = []
    
    # 1. Map absolute text nodes by annotation identifiers
    annotation_map = {}
    for tier in root.findall(".//TIER"):
        for ann in tier.findall(".//ALIGNABLE_ANNOTATION"):
            ann_id = ann.get("ANNOTATION_ID")
            val = ann.findtext("ANNOTATION_VALUE")
            if ann_id and val:
                annotation_map[ann_id] = val.strip()

    # 2. Extract child translation nodes anchored back to parents
    for tier in root.findall(".//TIER"):
        for ann in tier.findall(".//REF_ANNOTATION"):
            parent_id = ann.get("ANNOTATION_REF")
            translation_val = ann.findtext("ANNOTATION_VALUE")
            
            if parent_id in annotation_map and translation_val:
                src_phrase = annotation_map[parent_id]
                if src_phrase:
                    entries.append({
                        "form": src_phrase,
                        "gloss_en": translation_val.strip(),
                        "source_type": "elan-eaf"
                    })
    return entries
