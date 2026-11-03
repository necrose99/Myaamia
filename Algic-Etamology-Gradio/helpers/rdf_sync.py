# rdf_sync.py
import sqlite3
import requests
from rdflib import Graph, Namespace, URIRef
import etymology as ety
import visualization

# Define W3C / Ontolex / Glottolog Semantic Namespaces
LEXINFO = Namespace("http://lexinfo.net")
ONTOLEX = Namespace("http://w3.org")
GLOTTOLOG = Namespace("http://glottolog.org")
WALS_PROP = Namespace("https://wals.info") 

DB_FILE = "database.db"

def sync_language_rdf_updates(lang_code, glottocode):
    """
    Fetches the live Glottolog or Ontolex-Lemon RDF graph, parses semantic properties 
    (like updated lat/lon or typological values), and updates local SQLite rows.
    """
    rdf_url = f"https://glottolog.org{glottocode}.ttl"
    g = Graph()
    
    try:
        # Fetch and load turtle semantic dataset into memory
        response = requests.get(rdf_url, timeout=10)
        if response.status_code != 200:
            return False
            
        g.parse(data=response.text, format="turtle")
        
        # Define semantic properties to lookup
        # (Using standard Geo W3C vocabulary predicates usually linked in Glottolog RDF)
        GEO_LAT = URIRef("http://w3.org")
        GEO_LON = URIRef("http://w3.org")
        
        subject_uri = GLOTTOLOG[glottocode]
        
        new_lat = g.value(subject=subject_uri, predicate=GEO_LAT)
        new_lon = g.value(subject=subject_uri, predicate=GEO_LON)
        
        if new_lat and new_lon:
            lat_val = float(new_lat)
            lon_val = float(new_lon)
            
            # Recalculate geographic displacement vector from the homeland 
            new_geo_drift = ety.calculate_geographic_drift(lon_val, lat_val)
            
            # Persist fresh semantic properties down to SQLite layer
            with sqlite3.connect(DB_FILE) as conn:
                conn.execute("""
                    UPDATE dialect_sources 
                    SET lat = ?, lon = ?, geo_drift_km = ? 
                    WHERE lang_code = ?
                """, (lat_val, lon_val, new_geo_drift, lang_code))
                conn.commit()
                
            # Rebuild cache on successful extraction
            visualization.update_and_render_cache()
            return True
            
    except Exception as e:
        print(f"RDF Sync Failure for code {lang_code}: {e}")
        return False
def parse_lemon_lexicon_entry(rdf_data_stream, target_root):
    """
    Parses a lemon-model graph to extract lexical strings and match them to proto-roots.
    Ontolex-Lemon maps structure as: LexicalEntry -> canonicalForm -> writtenRep
    """
    g = Graph()
    g.parse(data=rdf_data_stream, format="turtle")
    
    extracted_words = []
    
    # Query all Ontolex lexical written representations
    for entry, canonical_form in g.subject_objects(predicate=ONTOLEX.canonicalForm):
        written_representation = g.value(subject=canonical_form, predicate=ONTOLEX.writtenRep)
        if written_representation:
            word_str = str(written_representation)
            
            # Compute etymological drift score on the fly using your Levenshtein engine
            drift_score = ety.calculate_etymological_drift(word_str, target_root)
            extracted_words.append({
                "word": word_str,
                "etym_drift": drift_score
            })
            
    return extracted_words
