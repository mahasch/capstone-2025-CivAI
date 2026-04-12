from backend.agent.utils.state import State

def extract_postcode(state: State):
    latest_postcode_msg = state["postcode"][-1]  # last HumanMessage
    return latest_postcode_msg.content.strip().upper()