from backend.agent.utils.state import State

# SessionMemory is a lightweight in-memory store that keeps each session’s state separate.
class SessionMemory:
    """
    Simple in-memory session store keyed by session_id.
    Stores State objects for the duration of the session.
    """
    def __init__(self):
        self.sessions = {}

    def save(self, session_id: str, state: State):
        self.sessions[session_id] = state

    def load(self, session_id: str) -> State:
        return self.sessions.get(session_id)

    def exists(self, session_id: str) -> bool:
        return session_id in self.sessions
