# database/db_factory_whoosh.py
import os
from flask_whooshee import Whooshee
from Admin.cfg import SearchIndexConfig

# Instantiate the absolute Whooshee context wrapper
whooshee = Whooshee()

def init_whooshee_factory(app):
    """
    Configures and attaches the Whooshee indexing engine to the active 
    Flask app backend database configurations.
    """
    # Define storage path inside the container environment
    app.config['WHOOSHEE_DIR'] = SearchIndexConfig.WHOOSH_BASE_DIR
    
    # Initialize the extension framework
    whooshee.init_app(app)
    
    # Register search profiles to build full-text search indices over targets
    _register_indexing_targets()
    return whooshee

def _register_indexing_targets():
    """Binds structural models to the Whooshee text parsing matrix."""
    from database.models import Lexicon, DocumentCorpus
    
    # 1. Index Word Entries (Optimized for cross-dialect word and definition scans)
    @whooshee.register_model('word', 'ipa_transcription', 'definition')
    class IndexedLexicon(Lexicon):
        pass

    # 2. Index Massive Manuscript Texts (Optimized for deep document lookups)
    @whooshee.register_model('title', 'raw_text')
    class IndexedCorpus(DocumentCorpus):
        pass
