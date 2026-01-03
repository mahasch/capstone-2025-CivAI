from backend.agent.utils.session_memory import SessionMemory, save_session_memory
from backend.agent.orchestrator.orchestrator import create_pipeline_app
from backend.agent.utils.state import State
from IPython.display import display, Markdown
import sys, requests
from datetime import datetime, timedelta
import logging

# Configure logging
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
        logger.info(f"[CACHE HIT] Returning cached state for {session_id}")
        return state
    logger.info(f"[CACHE MISS] Running pipeline for {session_id}")
    state = State(postcode=postcode, borough=borough)
    final_state = app.invoke(state)
    final_state["_cached_at"] = datetime.utcnow().isoformat()

    memory_bank.save(session_id, final_state)
    save_session_memory(memory_bank)

    return final_state

def render_md(state):
    """
    Render the summary in Markdown format from the state.
    Handles:
      - Plain string
      - List of HumanMessage objects (LangGraph style)
    Preserves all embedded Markdown.
    """
    summary = state.get("summary")

    # If summary is a list of HumanMessage, extract all content
    if isinstance(summary, list):
        md_text = "\n\n".join(
            m.content if hasattr(m, "content") else str(m)
            for m in summary
        )
    # If summary is a plain string
    elif isinstance(summary, str):
        md_text = summary
    else:
        md_text = str(summary)

    display(Markdown(md_text.strip()))


def main():
    if len(sys.argv) < 2:
        logger.error("Usage: python -m process_postcode <postcode>")
        sys.exit(1)

    postcode = sys.argv[1]
    logger.info(f"Processing postcode: {postcode}")
    url = f"https://api.postcodes.io/postcodes/{postcode}"
    try:
        resp = requests.get(url).json()
        if resp['status'] == 200:
            result = resp['result']
            lsoa = result['codes']['lsoa']
            msoa = result['codes']['msoa']
            borough = result['admin_district']
            lat = result['latitude']
            lng = result['longitude']
        else:
            logger.error(f"Failed to fetch postcode data: {resp}")
            sys.exit(1)
    except Exception as e:
        logger.exception("An error occurred while fetching postcode data.")
        sys.exit(1)

    session_id = f"borough_{borough.replace(' ', '_').lower()}" # Unique session per postcode

    try:
        final_state = run_pipeline(postcode, borough, session_id=session_id)
        render_md(final_state)
    except Exception as e:
        logger.exception("An error occurred while running the pipeline.")
        sys.exit(1)