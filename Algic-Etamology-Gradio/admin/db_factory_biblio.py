# Admin/db_factory_biblio.py
import json
import redis
from database.models import db, BibliographySource, LexiconCitation
from Admin.cfg import AppConfig

class BibliographyFactoryHelper:
    """Manages data provenance, PDF lookups, and RDF triple rendering for citations."""
    
    def __init__(self):
        self.cfg = AppConfig()
        self.redis_client = None
        if self.cfg.USE_REDIS_CACHE:
            self.redis_client = redis.Redis.from_url(self.cfg.REDIS_URI)

    def fetch_source_by_key(self, cite_key: str) -> dict:
        """Retrieves bibliography metadata, leveraging the Redis hot-cache if enabled."""
        cache_key = f"bib:{cite_key}"
        
        if self.redis_client:
            cached = self.redis_client.get(cache_key)
            if cached:
                return json.loads(cached.decode('utf-8'))
                
        source = BibliographySource.query.filter_by(cite_key=cite_key).first()
        if not source:
            return {}
            
        data = {
            "cite_key": source.cite_key,
            "type": source.source_type,
            "title": source.title,
            "author": source.author_creator,
            "year": source.publication_year,
            "isbn": source.isbn,
            "url": source.external_url,
            "local_path": source.local_archive_path
        }
        
        if self.redis_client:
            self.redis_client.setex(cache_key, self.cfg.CACHE_TTL_SECONDS, json.dumps(data))
            
        return data

    def generate_rdf_turtle(self, cite_key: str) -> str:
        """
        Converts database citation attributes into standardized RDF Turtle (TTL) triples.
        Useful for publishing open graph link mappings upstream.
        """
        src = self.fetch_source_by_key(cite_key)
        if not src:
            return ""
            
        # Clean string formats for RDF literal fields
        ttl_block = f"""
@prefix ex: <http://example.org> .
@prefix dcterms: <http://purl.org> .

ex:{src['cite_key']}
    a dcterms:BibliographicResource ;
    dcterms:title "{src['title']}" ;
    dcterms:creator "{src['author']}" ;
    dcterms:date "{src['year']}"^^xsd:gYear ;
"""
        if src.get('isbn'):
            ttl_block += f'    dcterms:identifier "urn:isbn:{src["isbn"]}" ;\n'
        if src.get('url'):
            ttl_block += f'    dcterms:relation <{src["url"]}> ;\n'
            
        ttl_block = ttl_block.strip()[:-2] + " ." # Finalize triple termination
        return ttl_block
