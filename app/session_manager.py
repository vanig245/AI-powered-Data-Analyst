import uuid
from typing import Dict, List, Optional
from langchain_core.messages import BaseMessage

class SessionData:
    """Stores the state for a single user session."""
    def __init__(self):
        self.history: List[BaseMessage] = []
        self.active_table: Optional[str] = None

class SessionManager:
    """Manages all active user sessions in-memory."""
    def __init__(self):
        self._sessions: Dict[str, SessionData] = {}

    def create_session(self) -> str:
        """Generates a unique session ID and initializes empty data."""
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = SessionData()
        return session_id

    def get_session(self, session_id: str) -> SessionData:
        """Retrieves session data, creating it dynamically if it doesn't exist."""
        if session_id not in self._sessions:
            self._sessions[session_id] = SessionData()
        return self._sessions[session_id]

    def get_history(self, session_id: str) -> List[BaseMessage]:
        """Returns the conversation history for the LLM context."""
        return self.get_session(session_id).history

    def add_message(self, session_id: str, message: BaseMessage):
        """Appends a LangChain message (HumanMessage or AIMessage) to the history."""
        session = self.get_session(session_id)
        session.history.append(message)

    def set_active_table(self, session_id: str, table_name: str):
        """Links an uploaded dataset (table name) to the user's session."""
        session = self.get_session(session_id)
        session.active_table = table_name

    def get_active_table(self, session_id: str) -> Optional[str]:
        """Retrieves the active table name so the agent knows what to query."""
        return self.get_session(session_id).active_table

session_manager = SessionManager()