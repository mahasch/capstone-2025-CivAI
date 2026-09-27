import sys
import json
import logging
from datetime import datetime, timedelta

from backend.agent.utils.session_memory import SessionMemory
from backend.agent.utils.memory_db import save_session_memory
from backend.agent.orchestrator.orchestrator import create_pipeline_app
from backend.agent.utils.state import State

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CACHE_TTL_DAYS = 60
memory_bank = SessionMemory()

def is_cache_valid(state, ttl_days):
    cached_at = state.get("_cached_at")
    if not cached_at:
        return False
    cached_time = datetime.fromisoformat(cached_at)
    return datetime.utcnow() - cached_time < timedelta(days=ttl_days)

def run_pipeline(postcode, borough, session_id="default"):
    app = create_pipeline_app()

    # Try loading from memory first
    state = memory_bank.load(session_id)
    if state and is_cache_valid(state, CACHE_TTL_DAYS):
        logger.info("[CACHE HIT] Returning cached state")
        return state
    
    logger.info("[CACHE MISS] Running pipeline")
    state = State(postcode=postcode, borough=borough)
    logger.info("Invoking agent workflow")
    final_state = app.invoke(state)
    logger.info("Agent workflow completed")
    final_state["_cached_at"] = datetime.utcnow().isoformat()

    memory_bank.save(session_id, final_state)
    save_session_memory(memory_bank)

    return final_state

def main():
    if len(sys.argv) < 2:
        logger.error("Usage: python -m backend.start_agent <postcode>")
        sys.exit(1)

    postcode = sys.argv[1]
    
    try:
        # Node already validated format; assume borough is in state or use default
        session_id = f"postcode_{postcode.replace(' ', '_').lower()}"
        
        final_state = run_pipeline(postcode, borough="", session_id=session_id)
        
        # Output to stdout as JSON for Node to parse
        summary = final_state.get("summary", "")
        if isinstance(summary, list):
            summary = "\n\n".join(
                m.content if hasattr(m, "content") else str(m)
                for m in summary
            )
        
        print(json.dumps({"markdown": str(summary).strip()}))
        
    except Exception as e:
        logger.exception("Pipeline failed")
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()