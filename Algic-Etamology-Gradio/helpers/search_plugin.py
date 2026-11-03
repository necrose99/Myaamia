# helpers/search_plugin.py
from database.models import Lexicon, DocumentCorpus

class AlgonquianSearchPlugin:
    """Unified engine presenting structural search queries over your linguistic indexes."""

    @staticmethod
    def search_dictionary(query_string: str, language_id: int = None, limit: int = 50):
        """Performs full-text searches over words, IPA entries, and definitions."""
        if not query_string:
            return []
            
        # Execute Whooshee query execution sequence
        search_query = Lexicon.query.whooshee_search(query_string)
        
        # Apply filtering if a specific language scope is provided
        if language_id:
            search_query = search_query.filter_by(language_id=language_id)
            
        return search_query.limit(limit).all()

    @staticmethod
    def search_manuscript_corpus(query_string: str, limit: int = 10):
        """Performs full-text search scans across all long-form text documents."""
        if not query_string:
            return []
            
        return DocumentCorpus.query.whooshee_search(query_string).limit(limit).all()
