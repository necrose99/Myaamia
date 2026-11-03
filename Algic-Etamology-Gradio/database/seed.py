# database/seed.py
from app import app
from database.models import db, Language
from Admin.cfg import AppConfig

def seed_algonquian_languages():
    """Loops through your dialect registry configuration block to seed the database tables."""
    with app.app_context():
        print("🌱 Seeding Algonquian Language Matrix (25-40 target variations)...")
        db.create_all()
        
        for lang_data in AppConfig.ALGONQUIAN_DIALECT_REGISTRY:
            exists = Language.query.filter_by(iso_code=lang_data["iso"]).first()
            if not exists:
                new_lang = Language(
                    iso_code=lang_data["iso"],
                    name=lang_data["name"],
                    subgroup=lang_data["subgroup"]
                )
                db.session.add(new_lang)
        
        db.session.commit()
        print("✅ Seeding sequence finalized successfully.")

if __name__ == "__main__":
    seed_algonquian_languages()
