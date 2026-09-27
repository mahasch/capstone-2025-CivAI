from langchain.schema import HumanMessage
from backend.agent.utils.state import State
from backend.agent.crime.crime_data import CrimeData
from backend.agent.utils.extract_postcode import extract_postcode
from backend.agent.utils.genai_client import get_genai_client

def crime_and_safety_agent(state: State) -> State:
    # Get the latest postcode string
    postcode = extract_postcode(state)
    crime_data = CrimeData(postcode, borough=state["borough"]).get_crime_data

    if not crime_data or "data" not in crime_data:
        state["crime"] = [
            HumanMessage(content=f"No crime data available for {postcode}.")
        ]
        return state

    rate = crime_data["data"].get("rate", {})
    rank = crime_data["data"].get("rank", {})

    prompt = f"""
            You are a friendly assistant. Summarise the following crime data for postcode {postcode} in a concise, readable paragraph suitable for a public report. Include total crime rate, top 3 crime categories by value, and safety ranking.
            
            Crime Rate Data:
            {rate}
            
            Crime Rank Data:
            {rank}
            
            Return the summary as natural language text.
            """

    response = get_genai_client().models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    natural_text_summary = response.text.strip()
    state["crime"] = [
        HumanMessage(content=natural_text_summary)
    ]
    return state
