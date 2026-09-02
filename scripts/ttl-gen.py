import re
from bs4 import BeautifulSoup

def clean_xml_string(xml_str):
    """Safely cleans common XML parsing bugs or escaping issues."""
    return xml_str.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def parse_tmx_to_ontolex(tmx_content):
    soup = BeautifulSoup(tmx_content, "xml")
    
    # Prefix layout for high-density Semantic Web formats
    ttl_lines = [
        "@prefix ontolex: <http://w3.org> .",
        "@prefix lexinfo: <http://lexinfo.net> .",
        "@prefix morph:   <http://w3.org> .",
        "@prefix alg:     <http://example.org> .",
        "@prefix rdfs:    <http://w3.org> .",
        "@prefix rdf:     <http://w3.org> .",
        "@prefix ex:      <http://example.org> .",
        ""
    ]
    
    # Process translation units
    for tu_index, tu in enumerate(soup.find_all("tu")):
        # Extract metadata from custom property tags
        props = {p.get("type"): p.get_text(strip=True) for p in tu.find_all("prop")}
        
        # Pull text from language variants
        tuv_mia = tu.find("tuv", {"xml:lang": "mia"})
        tuv_en = tu.find("tuv", {"xml:lang": "en"})
        
        if not tuv_mia or not tuv_en:
            continue
            
        mia_text = tuv_mia.find("seg").get_text(strip=True) if tuv_mia.find("seg") else ""
        en_text = tuv_en.find("seg").get_text(strip=True) if tuv_en.find("seg") else ""
        
        if not mia_text:
            continue
            
        # Clean terms for URI generation
        safe_id = re.sub(r'[^a-zA-Z0-9_]', '', mia_text.replace(" ", "_"))
        if not safe_id:
            safe_id = f"entry_{tu_index}"
            
        # Heuristic Rule Engine to explicitly catch missing parts of speech
        pos_uri = "lexinfo:LexicalParticle"  # Default fallback
        is_animate_verb = False
        
        # 1. Catch Numbers/Numerals using pure numeric context or trailing regex pattern loops
        if re.search(r'^\d+$', en_text) or any(num_word in en_text.lower().split() for num_word in ["one", "two", "three", "four", "five"]):
            pos_uri = "lexinfo:Numeral"
            
        # 2. Catch "Him Verb" (Animate Transitive Verbs)
        elif any(tgt in en_text.lower().split() for tgt in ["him", "her", "them"]):
            pos_uri = "lexinfo:TransitiveVerb"
            is_animate_verb = True
            
        # 3. Basic verb checks
        elif "to " in en_text.lower() or en_text.lower().endswith("ing"):
            pos_uri = "lexinfo:Verb"
            
        # 4. Basic noun checks
        elif any(art in en_text.lower().split() for art in ["a", "an", "the"]):
            pos_uri = "lexinfo:Noun"
            
        # Build out triples string block
        ttl_lines.append(f"ex:{safe_id} rdf:type ontolex:Word ;")
        if is_animate_verb:
            ttl_lines.append(f"    rdf:type alg:AnimateTransitiveVerb ;")
        ttl_lines.append(f"    rdfs:label \"{mia_text}\"@mia ;")
        ttl_lines.append(f"    ontolex:canonicalForm ex:{safe_id}_form ;")
        ttl_lines.append(f"    lexinfo:partOfSpeech {pos_uri} .")
        
        # Build form and morphology blocks
        ttl_lines.append(f"ex:{safe_id}_form rdf:type ontolex:Form ;")
        ttl_lines.append(f"    ontolex:writtenRep \"{mia_text}\"@mia .")
        
        # Extract dictionary links embedded in property tags safely
        url_source = props.get("url") or props.get("miami_dict_url")
        
        # Build sense semantic mapping layers
        ttl_lines.append(f"ex:{safe_id}_sense rdf:type ontolex:LexicalSense ;")
        ttl_lines.append(f"    ontolex:isSenseOf ex:{safe_id} ;")
        ttl_lines.append(f"    rdfs:comment \"{en_text}\"@en ;")
        if url_source:
            ttl_lines.append(f"    rdfs:seeAlso <{url_source}> ;")
        ttl_lines.append(f"    rdfs:isDefinedBy <http://myaamiadictionary.org> .")
        ttl_lines.append("")
        
    return "\n".join(ttl_lines)
