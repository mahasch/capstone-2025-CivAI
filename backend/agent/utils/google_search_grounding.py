import logging

from google.genai import types
from backend.agent.utils.genai_client import get_genai_client

logger = logging.getLogger(__name__)

def search_google(query: str) -> dict:
    # 1. Configure grounding
    config_with_search = types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())],
    )

    # 2. Helper to query search-grounded model
    def query_with_grounding():
        response = get_genai_client().models.generate_content(
            model="gemini-2.0-flash",
            contents=query,
            config=config_with_search
        )
        return response.candidates[0]

    # 3. Retry until grounding chunks exist
    rc = query_with_grounding()
    while not rc.grounding_metadata.grounding_supports or not rc.grounding_metadata.grounding_chunks:
        rc = query_with_grounding()

    # 4. Extract grounded search results
    chunks = rc.grounding_metadata.grounding_chunks
    sources = []
    for chunk in chunks:
        title = chunk.web.title or "Unknown"
        url = chunk.web.uri or ""
        sources.append(f"{title}: {url}")
    return sources

def safe_google_search(query):
    try:
        return search_google(query)
    except Exception as e:
        if isinstance(e, EnvironmentError) or "quota" in str(e).lower() or "429" in str(e):
            logger.warning("Google search unavailable; using fallback: %s", e)
            return []
        raise
