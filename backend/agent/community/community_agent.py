from backend.agent.utils.extract_postcode import extract_postcode
from backend.agent.utils.genai_client import get_genai_client
from backend.agent.utils.google_search_grounding import safe_google_search
from backend.agent.utils.state import State
from backend.agent.transport.fallback_summary import BOROUGH_TRANSPORT_PROFILES
from langchain.schema import HumanMessage

def community_agent(state: State) -> State:
    """
    Fetches community + amenities info around a postcode using Google Search grounding.
    Includes: parks, schools, masjids, churches, shops, restaurants, walkability.
    Produces a natural-language summary.
    """
    postcode = extract_postcode(state)
    
    if not postcode:
        state["community"] = {"summary": "No postcode provided."}
        return state

    query = f"""
    Community amenities and cultural info near {postcode}, London:
    - Parks and green spaces
    - Primary & secondary schools (mention Ofsted if known)
    - Places of worship for different religions (mosques, churches, temples, synagogues)
    - Majority religion in the area
    - Local grocery stores, supermarkets, cultural food shops, and restaurants
    - Shopping areas for clothes, household items, and food
    - Walkability, safety for families, and general community vibe
    """
    sources = safe_google_search(query)

    # 5. Summarise community information
    if sources:
        text_to_summarise = "\n".join(sources)
    
        summary_prompt = f"""
        You are a community-living and cultural expert.

        Summarise the key community, lifestyle, and cultural features around postcode {postcode} in London.

        Include:
        - Local parks, playgrounds, and green spaces
        - Primary & secondary schools (mention Ofsted ratings if available)
        - Places of worship for different religions (mosques, churches, temples, synagogues, etc.)
        - The majority religion or dominant cultural communities in the area
        - Nearby grocery stores, supermarkets, cultural/ethnic food shops, and restaurants
        - Shopping areas for clothes, household items, and food
        - Walkability, cycling options, and safety for families
        - General community vibe and cultural highlights

        Be concise, friendly, and actionable (3-5 sentences). Focus on specifics useful for someone living or moving there.  
        Use ONLY the following search-grounded sources:

        {text_to_summarise}
        """
        summary_response = get_genai_client().models.generate_content(
            model="gemini-2.0-flash",
            contents=summary_prompt
        )
    else:
        profile = BOROUGH_TRANSPORT_PROFILES.get(
            state.get("borough"),
            "Standard London community amenities with parks, schools, places of worship, shops, and restaurants."
        )
        summary_response = f"""
Borough community profile:
{profile}
"""

    summary_text = (
        summary_response.text.strip()
        if hasattr(summary_response, "text")
        else summary_response.strip()
    )
    state["community"] = [HumanMessage(content=summary_text)]

    return state
