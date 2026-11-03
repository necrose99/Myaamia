# database/models.py (Append to your existing models file)
from database.models import db

class BibliographySource(db.Model):
    """Stores master source metadata (Books, ILDA PDFs, WALS references, URLs)."""
    __tablename__ = 'bibliography_sources'
    
    id = db.Column(db.Integer, primary_key=True)
    cite_key = db.Column(db.String(50), unique=True, nullable=False, index=True) # e.g., 'costa2003', 'wals-77A'
    source_type = db.Column(db.String(30), nullable=False) # e.g., 'book', 'pdf', 'web', 'rdf_ttl'
    
    title = db.Column(db.String(255), nullable=False)
    author_creator = db.Column(db.String(255))
    publication_year = db.Column(db.Integer)
    
    # Flexible identifiers for cross-referencing external catalogs
    isbn = db.Column(db.String(20), nullable=True, index=True)
    external_url = db.Column(db.Text, nullable=True) # URLs for Wikipedia, GLottolog, or local assets
    local_archive_path = db.Column(db.String(255), nullable=True) # Path to local ILDA PDFs
    
    # Relationships
    citations = db.relationship('LexiconCitation', backref='source_meta', lazy='dynamic')


class LexiconCitation(db.Model):
    """Cross-reference matrix linking specific dictionary words to their sources."""
    __tablename__ = 'lexicon_citations'
    
    id = db.Column(db.Integer, primary_key=True)
    lexicon_id = db.Column(db.Integer, db.ForeignKey('lexicon.id'), nullable=False)
    source_id = db.Column(db.Integer, db.ForeignKey('bibliography_sources.id'), nullable=False)
    
    page_or_node = db.Column(db.String(50), nullable=True) # e.g., 'p. 142', 'Node #134'
    context_snippet = db.Column(db.Text, nullable=True) # Verbatim string from historical text
# database/models.py (Append to your models file)
from database.models import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class AdminUser(db.Model, UserMixin):
    """User table model managing secure access control for administrative tasks."""
    __tablename__ = 'admin_users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
