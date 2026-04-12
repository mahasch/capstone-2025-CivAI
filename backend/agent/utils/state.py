from typing import TypedDict, Optional, Dict, Annotated
from langgraph.graph import add_messages
# The State object defines all the information passed between agents in the LangGraph workflow.
class State(TypedDict):
    postcode: Annotated[str, add_messages]
    borough: Annotated[Optional[str], add_messages]
    policy: Annotated[Optional[Dict], add_messages]  
    housing: Annotated[Optional[Dict], add_messages]
    transport: Annotated[Optional[Dict], add_messages]
    community: Annotated[Optional[Dict], add_messages]
    crime: Annotated[Optional[Dict], add_messages]
    summary: Annotated[Optional[str], add_messages]
