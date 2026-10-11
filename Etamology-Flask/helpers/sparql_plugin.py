# helpers/sparql_plugin.py
import logging
import urllib.request
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional
from flask import Blueprint, request, jsonify
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL, SKOS, DCTERMS
from SPARQLWrapper import SPARQLWrapper, JSON

# Core Semantic & Linguistic Namespaces
SWIVT = Namespace("http://semantic-mediawiki.org/swivt/1.0#")
ONTOLEX = Namespace("http://www.w3.org/ns/lemon/ontolex#")
LIME = Namespace("http://www.w3.org/ns/lemon/lime#")
ALGIC = Namespace("http://example.org/algic/etymology#")
GLOTTOLOG = Namespace("http://glottolog.org/resource/languoid/id/")
WALS = Namespace("http://wals.info/feature/")
LEXVO = Namespace("http://lexvo.org/id/iso639-3/")

# Upstream Glottolog TTL & WALS Registry Mappings
UPSTREAM_ALGIC_REGISTRY: Dict[str, str] = {
    # Core Root & Family Branches
    "algic_root": "https://glottolog.org/resource/languoid/id/algi1248.ttl",
    "algonquian": "https://glottolog.org/resource/languoid/id/east2700.ttl",
    "eastern_algonquian": "https://glottolog.org/resource/languoid/id/east2765.ttl",
    
    # Specific Languoids & Dialects (Glottolog TTL Endpoints)
    "mia": "https://glottolog.org/resource/languoid/id/miam1252.ttl",      # Miami-Illinois
    "fox": "https://glottolog.org/resource/languoid/id/foxx1245.ttl",      # Fox / Meskwaki-Sauk dialect group
    "kic": "https://glottolog.org/resource/languoid/id/kick1244.ttl",      # Kickapoo
    "sac": "https://glottolog.org/resource/languoid/id/sacc1239.ttl",      # Sac
    "mesk": "https://glottolog.org/resource/languoid/id/mesk1243.ttl",     # Meskwaki
    "men": "https://glottolog.org/resource/languoid/id/meno1252.ttl",      # Menominee
    "sjw": "https://glottolog.org/resource/languoid/id/shaw1249.ttl",      # Shawnee
    "pot": "https://glottolog.org/resource/languoid/id/pota1247.ttl",      # Potawatomi
    "ojs": "https://glottolog.org/resource/languoid/id/seve1242.ttl",      # Severn Ojibwe / Oji-Cree
    "ojb": "https://glottolog.org/resource/languoid/id/nucl1723.ttl",      # Northwestern Ojibwe
    "otw": "https://glottolog.org/resource/languoid/id/otta1242.ttl",      # Ottawa
    "alq": "https://glottolog.org/resource/languoid/id/algo1255.ttl",      # Algonquin
    "cre": "https://glottolog.org/resource/languoid/id/cree1271.ttl",      # Cree
    "bft": "https://glottolog.org/resource/languoid/id/siks1238.ttl",      # Blackfoot
    "wiy": "https://glottolog.org/resource/languoid/id/wiyo1248.ttl",      # Wiyot
    "yur": "https://glottolog.org/resource/languoid/id/yuro1248.ttl",      # Yurok
    "chy": "https://glottolog.org/resource/languoid/id/chey1247.ttl",      # Cheyenne
    
    # WALS Typology Features
    "wals_129A": "https://wals.info/feature/129A.ttl",                     # Hand and Arm
    "wals_130A": "https://wals.info/feature/130A.ttl",                     # Finger and Hand
}

# ISO 639-3 & Regional Branch Taxonomy Registry
ALGIC_ISO_TAXONOMY: Dict[str, Dict[str, str]] = {
    # Plains Branch
    "bft": {"name": "Blackfoot", "group": "Plains", "glottocode": "siks1238"},
    "arp": {"name": "Arapaho", "group": "Plains", "glottocode": "arap1274"},
    "ats": {"name": "Gros Ventre", "group": "Plains", "glottocode": "gros1243"},
    "chy": {"name": "Cheyenne", "group": "Plains", "glottocode": "chey1247"},
    
    # Central Branch
    "men": {"name": "Menominee", "group": "Central", "glottocode": "meno1252"},
    "cre": {"name": "Cree", "group": "Central", "glottocode": "cree1271"},
    "csw": {"name": "Swampy Cree", "group": "Central", "glottocode": "swam1239"},
    "crj": {"name": "Southern East Cree", "group": "Central", "glottocode": "sout2964"},
    "atj": {"name": "Atikamekw", "group": "Central", "glottocode": "atik1239"},
    "pot": {"name": "Potawatomi", "group": "Central", "glottocode": "pota1247"},
    "oji": {"name": "Ojibwe", "group": "Central", "glottocode": "ojib1241"},
    "otw": {"name": "Ottawa", "group": "Central", "glottocode": "otta1242"},
    "ciw": {"name": "Chippewa", "group": "Central", "glottocode": "chip1262"},
    "ojs": {"name": "Severn Ojibwe", "group": "Central", "glottocode": "seve1242"},
    "ojb": {"name": "Northwestern Ojibwe", "group": "Central", "glottocode": "nucl1723"},
    "alq": {"name": "Algonquin", "group": "Central", "glottocode": "algo1255"},
    "mia": {"name": "Miami-Illinois", "group": "Central", "glottocode": "miam1252"},
    "sac": {"name": "Meskwaki (Fox / Sac)", "group": "Central", "glottocode": "sacc1239"},
    "kic": {"name": "Kickapoo", "group": "Central", "glottocode": "kick1244"},
    "sjw": {"name": "Shawnee (Shall-Zwall)", "group": "Central", "glottocode": "shaw1249"},
    
    # Eastern Branch
    "mic": {"name": "Mi'kmaq", "group": "Eastern", "glottocode": "mikm1235"},
    "abe": {"name": "Western Abenaki", "group": "Eastern", "glottocode": "west2630"},
    "aaq": {"name": "Eastern Abnaki", "group": "Eastern", "glottocode": "east2544"},
    "mal": {"name": "Maliseet-Passamaquoddy", "group": "Eastern", "glottocode": "mali1279"},
    "moo": {"name": "Mohegan-Pequot", "group": "Eastern", "glottocode": "mohe1244"},
    "mua": {"name": "Munsee", "group": "Eastern", "glottocode": "muns1243"},
    "unm": {"name": "Unami", "group": "Eastern", "glottocode": "unam1242"},
    
    # Proto-Language
    "alg-x-proto": {"name": "Proto-Algonquian", "group": "Proto-Language", "glottocode": "proto-alg"},
    
    # Western / Ritwan Branch
    "yur": {"name": "Yurok", "group": "Western", "glottocode": "yuro1248"},
    "wiy": {"name": "Wiyot", "group": "Western", "glottocode": "wiyo1248"},
    
    # Lost / Unattested / Remnant Languages
    "bue": {"name": "Beothuk", "group": "Remnant/Uncertain", "glottocode": "beot1247"},
    "etc": {"name": "Etchemin", "group": "Remnant/Uncertain", "glottocode": "etch1234"},
    "xlo": {"name": "Loup A (Mots loups)", "group": "Remnant/Uncertain", "glottocode": "loup1243"},
    "xlb": {"name": "Loup B", "group": "Remnant/Uncertain", "glottocode": "loup1244"},
    "crr": {"name": "Lumbee (Croatan, Pamlico)", "group": "Remnant/Uncertain", "glottocode": "paml1239"},
    "pim": {"name": "Powhatan (Virginia Algonkian)", "group": "Remnant/Uncertain", "glottocode": "powh1243"},
    "qyp": {"name": "Naugatuck/Quiripi/Unquachog", "group": "Remnant/Uncertain", "glottocode": "quir1238"},
}

OLAC_ENDPOINTS = {
    "olac_search_oai": "http://www.language-archives.org/cgi-bin/olac3.pl"
}


class SparqlPluginEngine:
    def __init__(self, db_path: str, xslt_dir: str):
        self.db_path = db_path
        self.xslt_dir = xslt_dir
        self.graph = Graph()
        self._bind_namespaces()
        self._seed_iso_taxonomy()
        self.blueprint = Blueprint("sparql_plugin", __name__, url_prefix="/sparql")
        self._register_routes()

    def _bind_namespaces(self):
        """Binds standard ontology prefixes for TTL/RDF serialization."""
        self.graph.bind("swivt", SWIVT)
        self.graph.bind("ontolex", ONTOLEX)
        self.graph.bind("lime", LIME)
        self.graph.bind("skos", SKOS)
        self.graph.bind("algic", ALGIC)
        self.graph.bind("glottolog", GLOTTOLOG)
        self.graph.bind("wals", WALS)
        self.graph.bind("lexvo", LEXVO)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("owl", OWL)
        self.graph.bind("dcterms", DCTERMS)

    def _seed_iso_taxonomy(self):
        """Populates the in-memory graph with taxonomy nodes for all registered ISO codes."""
        for iso, meta in ALGIC_ISO_TAXONOMY.items():
            lang_uri = ALGIC[f"language/{iso}"]
            self.graph.add((lang_uri, RDF.type, ONTOLEX.LexicalConcept))
            self.graph.add((lang_uri, RDFS.label, Literal(meta["name"])))
            self.graph.add((lang_uri, DCTERMS.identifier, Literal(iso)))
            self.graph.add((lang_uri, ALGIC.subgroup, Literal(meta["group"])))
            
            if "glottocode" in meta and not meta["glottocode"].startswith("proto-"):
                self.graph.add((lang_uri, OWL.sameAs, GLOTTOLOG[meta["glottocode"]]))
                
            if not iso.startswith("alg-x-"):
                self.graph.add((lang_uri, OWL.sameAs, LEXVO[iso]))

    def fetch_and_merge_upstream_ttl(self, resource_key: str) -> Dict[str, Any]:
        """Fetches upstream TTL/RDF and merges it into the local graph."""
        if resource_key not in UPSTREAM_ALGIC_REGISTRY:
            raise ValueError(f"Unknown upstream key: {resource_key}")

        target_url = UPSTREAM_ALGIC_REGISTRY[resource_key]
        req = urllib.request.Request(
            target_url, 
            headers={"User-Agent": "AlgicEtymologyFlask/2.0 (+https://github.com/necrose99/Algic-Etamology-Flask)"}
        )

        with urllib.request.urlopen(req) as response:
            raw_data = response.read()

        rdf_format = "rdf" if target_url.endswith(".rdf") else "turtle"
        initial_count = len(self.graph)
        self.graph.parse(data=raw_data.decode("utf-8", errors="ignore"), format=rdf_format)

        return {
            "key": resource_key,
            "url": target_url,
            "triples_added": len(self.graph) - initial_count,
            "total_graph_size": len(self.graph)
        }

    def harvest_olac_by_iso(self, iso_code: str) -> int:
        """Queries OLAC OAI-PMH archives directly using the ISO taxonomy mapping."""
        if iso_code not in ALGIC_ISO_TAXONOMY:
            logging.warning(f"Unregistered ISO code target: {iso_code}")
        
        oai_url = f"{OLAC_ENDPOINTS['olac_search_oai']}?verb=ListRecords&metadataPrefix=olac&set=language:{iso_code}"
        req = urllib.request.Request(oai_url, headers={"User-Agent": "AlgicEtymologyFlask/2.0"})
        
        try:
            with urllib.request.urlopen(req) as response:
                xml_data = response.read()

            tree = ET.fromstring(xml_data)
            count = 0
            
            for record in tree.findall(".//{http://www.openarchives.org/OAI/2.0/}record"):
                header = record.find("{http://www.openarchives.org/OAI/2.0/}header")
                if header is None:
                    continue
                
                identifier = header.findtext("{http://www.openarchives.org/OAI/2.0/}identifier")
                if not identifier:
                    continue

                res_uri = URIRef(f"http://www.language-archives.org/archive/{identifier.replace(':', '_')}")
                self.graph.add((res_uri, RDF.type, SKOS.Concept))
                self.graph.add((res_uri, DCTERMS.language, LEXVO[iso_code]))
                
                for title in record.findall(".//{http://purl.org/dc/elements/1.1/}title"):
                    if title.text:
                        self.graph.add((res_uri, RDFS.label, Literal(title.text)))
                        count += 1
            
            return count
        except Exception as e:
            logging.error(f"OLAC harvesting error for ISO [{iso_code}]: {str(e)}")
            return 0

    def execute_local_sparql(self, query: str) -> List[Dict[str, str]]:
        """Executes SPARQL against the internal RDFLib graph."""
        results = self.graph.query(query)
        output = []
        for row in results:
            output.append({str(k): str(v) for k, v in row.asdict().items()})
        return output

    def _register_routes(self):
        """Registers routing hooks exposed to Flask."""
        
        @self.blueprint.route("/taxonomy", methods=["GET"])
        def get_taxonomy():
            """Returns the pre-seeded ISO taxonomy graph metadata."""
            group_filter = request.args.get("group")
            filtered = {
                k: v for k, v in ALGIC_ISO_TAXONOMY.items() 
                if not group_filter or v["group"].lower() == group_filter.lower()
            }
            return jsonify({"total_languages": len(filtered), "taxonomy": filtered})

        @self.blueprint.route("/query", methods=["POST"])
        def handle_query():
            data = request.get_json() or {}
            query = data.get("query")
            if not query:
                return jsonify({"error": "Missing 'query' parameter"}), 400
            try:
                res = self.execute_local_sparql(query)
                return jsonify({"source": "local_graph", "triple_count": len(self.graph), "results": res})
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.blueprint.route("/harvest-olac", methods=["GET"])
        def handle_olac_harvest():
            iso = request.args.get("iso", "pot")
            count = self.harvest_olac_by_iso(iso)
            return jsonify({
                "status": "success",
                "iso_code": iso,
                "language_name": ALGIC_ISO_TAXONOMY.get(iso, {}).get("name", "Unknown"),
                "records_harvested": count,
                "total_graph_triples": len(self.graph)
            })

        @self.blueprint.route("/fetch-upstream", methods=["POST"])
        def handle_upstream_fetch():
            data = request.get_json() or {}
            target_key = data.get("key", "all")
            
            if target_key == "all":
                results = []
                for k in UPSTREAM_ALGIC_REGISTRY:
                    try:
                        res = self.fetch_and_merge_upstream_ttl(k)
                        results.append(res)
                    except Exception as e:
                        results.append({"key": k, "error": str(e)})
                return jsonify({"status": "completed", "results": results})
            else:
                try:
                    res = self.fetch_and_merge_upstream_ttl(target_key)
                    return jsonify({"status": "success", "result": res})
                except Exception as e:
                    return jsonify({"error": str(e)}), 400

        @self.blueprint.route("/export-ttl", methods=["GET"])
        def handle_export():
            ttl_bytes = self.graph.serialize(format="turtle")
            return ttl_bytes, 200, {"Content-Type": "text/turtle; charset=utf-8"}


def initialize_plugin(db_path: str, xslt_dir: str) -> SparqlPluginEngine:
    """Standard hook called by PluginManager during auto-discovery loop."""
    logging.info("Initializing SPARQL & ISO-Taxonomy Linkage Engine...")
    return SparqlPluginEngine(db_path=db_path, xslt_dir=xslt_dir)