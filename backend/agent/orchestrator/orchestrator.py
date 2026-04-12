from langgraph.graph import StateGraph, END
from backend.agent.utils.state import State
from backend.agent.community.community_agent import community_agent
from backend.agent.transport.transport_agent import transport_agent
from backend.agent.summary.summary_agent import summary_agent
from backend.agent.crime.crime_agent import crime_and_safety_agent
from backend.agent.postcode_processor.process_postcode import validate_postcode

def create_pipeline_app():
    """
    Creates and compiles the CIVAI agent workflow graph.
    Returns the compiled application ready to run.
    """
    graph = StateGraph(State)

    # Add nodes for each agent
    graph.add_node("validate", validate_postcode)
    # graph.add_node("policy_info", policy_agent)
    graph.add_node("crime_safety", crime_and_safety_agent)
    # graph.add_node("housing_info", housing_agent)
    graph.add_node("transport_info", transport_agent)
    graph.add_node("community_info", community_agent)
    graph.add_node("build_summary", summary_agent)

    # Set the entry point
    graph.set_entry_point("validate")

    # Parallel execution after validation
    # graph.add_edge("validate", "policy_info")
    # graph.add_edge("validate", "housing_info")
    graph.add_edge("validate", "crime_safety")
    graph.add_edge("validate", "transport_info")
    graph.add_edge("validate", "community_info")

    # Summary collects outputs from all agents
    # graph.add_edge("policy_info", "build_summary")
    # graph.add_edge("housing_info", "build_summary")
    graph.add_edge("transport_info", "build_summary")
    graph.add_edge("community_info", "build_summary")
    graph.add_edge("crime_safety", "build_summary")

    # End node
    graph.add_edge("build_summary", END)

    # Compile the graph
    app = graph.compile()
    return app
