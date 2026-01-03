import re
from langchain.schema import HumanMessage
from backend.agent.utils.state import State
from backend.agent.utils.extract_postcode import extract_postcode

POSTCODE_RE = re.compile(r"^[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}$")

def validate_postcode(state: State) -> State:
    postcode = extract_postcode(state)
    if not POSTCODE_RE.match(postcode):
        raise ValueError(f"Invalid postcode: {postcode}")
    state["postcode"] = [HumanMessage(content=postcode)]
    return state
    

