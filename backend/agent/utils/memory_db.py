import pickle
import os

from backend.agent.utils.session_memory import SessionMemory

MEMORY_FILE = "session_memory.pkl"

# Save the SessionMemory object
def save_session_memory(memory: SessionMemory):
    with open(MEMORY_FILE, "wb") as f:
        pickle.dump(memory, f)

# Load the SessionMemory object
def load_session_memory() -> SessionMemory:
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "rb") as f:
            return pickle.load(f)
    else:
        return SessionMemory()

memory_bank = load_session_memory()
