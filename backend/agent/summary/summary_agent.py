from backend.agent.utils.state import State
from langchain.schema import HumanMessage
import re

def summary_agent(state: State) -> State:
    """
    Builds a polished, well-structured Markdown report summarising
    the outputs of all other agents. Ensures all internal agent 
    headings are normalised so Markdown renders correctly.
    """

    # -------------------------
    # Helper: Extract postcode
    # -------------------------
    postcode_list = state.get("postcode", [])
    postcode = postcode_list[-1].content if postcode_list else "Unknown"

    # -------------------------
    # Helper: Collect markdown from agents
    # -------------------------
    def extract_agent_content(agent_key: str) -> str:
        messages = state.get(agent_key)
        if not messages or not isinstance(messages, list):
            return ""
        raw = "\n\n".join(
            m.content for m in messages if hasattr(m, "content")
        )
        return normalize_markdown(raw)

    # -------------------------
    # Helper: Normalise headings
    # -------------------------

    def normalize_markdown(text: str) -> str:
        """
        Prevents agent content from inserting H1/H2 headings that break layout.
        Downgrades all headings inside agent responses to ### or deeper.
        Also trims excess whitespace and removes accidental duplicates.
        """
        # Convert all headings (#, ##, ###...) into at least level 3
        text = re.sub(r"^#{1,6}\s+", "### ", text, flags=re.MULTILINE)

        # Remove duplicate consecutive lines
        lines = []
        for line in text.splitlines():
            if not lines or line.strip() != lines[-1].strip():
                lines.append(line)

        return "\n".join(lines).strip()

    # -------------------------
    # Build each section
    # -------------------------
    sections = []

    crime_content = extract_agent_content("crime")
    if crime_content:
        sections.append(f"## 🔒 Crime & Safety\n\n{crime_content}\n")

    housing_content = extract_agent_content("housing")
    if housing_content:
        sections.append(f"## 🏠 Housing Overview\n\n{housing_content}\n")

    transport_content = extract_agent_content("transport")
    if transport_content:
        sections.append(f"## 🚆 Transport & Connectivity\n\n{transport_content}\n")

    community_content = extract_agent_content("community")
    if community_content:
        sections.append(f"## 🏘️ Community & Local Amenities\n\n{community_content}\n")

    policy_content = extract_agent_content("policy")
    if policy_content:
        sections.append(f"## 📜 Local Policies & Regulations\n\n{policy_content}\n")

    # -------------------------
    # Final assembled report
    # -------------------------
    report = f"""# 🏙️ CIVAI Intelligence Report\n\n### Postcode: **{postcode}**

---

{''.join(sections)}

---

### 🧾 Report Generated Automatically by CIVAI"""


    state["summary"] = [HumanMessage(content=report)]
    return state
