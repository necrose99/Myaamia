# database/search_cron.py
import time
import logging
from app import app
from database.db_factory_whoosh import whooshee
from Admin.cfg import SearchIndexConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("⏱️ WHOOSHEE-CRON-SYNC")

def execute_periodic_reindex():
    """
    Bypasses request loops to re-build or optimize search indices 
    directly within the application context.
    """
    logger.info("🔄 Commencing scheduled full-text index synchronization sequence...")
    try:
        with app.app_context():
            # Forces Whooshee to sweep tables and update indexes
            whooshee.reindex()
        logger.info("✅ Full-text search index refreshed successfully.")
    except Exception as e:
        logger.error("❌ Scheduled index synchronization failed: %s", str(e))

def run_cron_daemon():
    """Continuous loop monitoring sleep intervals for background execution flags."""
    # Convert configuration hour limits into standard seconds thresholds
    sleep_seconds = SearchIndexConfig.CRON_INDEX_INTERVAL_HOURS * 3600
    
    logger.info("🚀 Index sync daemon started. Execution interval: %d hours.", SearchIndexConfig.CRON_INDEX_INTERVAL_HOURS)
    
    while True:
        time.sleep(sleep_seconds)
        execute_periodic_reindex()

if __name__ == "__main__":
    # Execute immediately on container startup, then enter continuous sleep cycles
    execute_periodic_reindex()
    run_cron_daemon()
