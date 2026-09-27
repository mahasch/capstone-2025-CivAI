from google.genai import types
from langchain.schema import HumanMessage
from backend.agent.utils.state import State
from backend.agent.utils.extract_postcode import extract_postcode
from backend.agent.utils.genai_client import get_genai_client
from backend.agent.utils.google_search_grounding import safe_google_search
from backend.agent.transport.fallback_summary import BOROUGH_TRANSPORT_PROFILES

def transport_agent(state: State) -> State:
    """
    Fetch transport & commute information for a given postcode
    using Google Search grounding and generate a natural language summary.
    """
    postcode = extract_postcode(state)
    
    if not postcode:
        state["transport"] = [HumanMessage(content="No postcode provided.")]
        return state

    query = f"Provide a concise summary of transport options near {postcode}, London. Include nearby Tube, rail, and bus stations (with lines), typical commute time to Central London, walkability and cycling options, and any restricted zones or time-based access limitations (e.g., school zones)."
    sources = safe_google_search(query)

    if sources:
        text_to_summarise = "\n".join(sources)

    # --- 5. Summarise with LLM ---
        summary_prompt = f"""
        You are a London transport assistant. Provide a practical, commuter-focused overview of transport options for postcode {postcode}.

        Include the following details:
        - Nearby Tube, rail, and bus stations (names and lines if available)
        - Typical commute time to Central London (by public transport)
        - Walkability and cycling options in the area, including nearby cycle routes
        - Any zone restrictions or time-based access limitations, such as school zones, pedestrian-only streets, or congestion charge areas, and the times they apply

        Use the context in {text_to_summarise} to inform your answer.

        Write a concise, actionable summary in 3-4 sentences, focusing on specifics a resident or commuter would find most useful. Include station names, lines, average travel times, and relevant restrictions.
        Avoid generic statements.
        """
        summary_response = get_genai_client().models.generate_content(
            model="gemini-2.0-flash",
            contents=summary_prompt
        )
    else:
        profile = BOROUGH_TRANSPORT_PROFILES.get(
            state.get("borough"),
            "Standard London public transport coverage with buses and rail links."
        )
        summary_response = f"""
Borough transport profile:
{profile}
"""

    summary_text = (
        summary_response.text.strip()
        if hasattr(summary_response, "text")
        else summary_response.strip()
    )
    state["transport"] = [HumanMessage(content=summary_text)]

    return state
