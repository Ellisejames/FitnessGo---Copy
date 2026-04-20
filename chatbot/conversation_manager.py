# chatbot/conversation_manager.py

from typing import Dict, Any, Optional
from datetime import datetime


class ConversationState:
    """Manages conversation state for each user"""

    def __init__(self, user_id: int):
        self.user_id = user_id
        self.current_flow = None  # BMI, CALORIES, WORKOUT, etc.
        self.flow_step = 0
        self.collected_data = {}
        self.last_updated = datetime.now()

        # ✅ Track wrong inputs per flow
        self.wrong_input_count = {
            "bmi": 0,
            "calories": 0,
            "workout": 0,
            "motivation": 0,
            "articles": 0
        }

    def reset(self):
        """✅ FIXED: Complete reset of conversation state"""
        self.current_flow = None
        self.flow_step = 0
        self.collected_data = {}
        self.wrong_input_count = {
            "bmi": 0,
            "calories": 0,
            "workout": 0,
            "motivation": 0,
            "articles": 0
        }
        self.last_updated = datetime.now()

    def update(self, flow: str = None, step: int = None, data: dict = None):
        """✅ FIXED: Update conversation state with proper initialization"""
        if flow is not None:
            self.current_flow = flow
        if step is not None:
            self.flow_step = step
        if data is not None:
            # ✅ FIXED: Ensure collected_data is a dict before updating
            if not isinstance(self.collected_data, dict):
                self.collected_data = {}
            self.collected_data.update(data)
        self.last_updated = datetime.now()

    def increment_wrong_input(self, flow: str) -> int:
        """
        Increment wrong input counter for a flow
        Returns the new count
        """
        flow_key = flow.lower()
        if flow_key in self.wrong_input_count:
            self.wrong_input_count[flow_key] += 1
            return self.wrong_input_count[flow_key]
        return 0

    def reset_wrong_input(self, flow: str):
        """Reset wrong input counter for a flow"""
        flow_key = flow.lower()
        if flow_key in self.wrong_input_count:
            self.wrong_input_count[flow_key] = 0

    def get_wrong_input_count(self, flow: str) -> int:
        """Get wrong input count for a flow"""
        flow_key = flow.lower()
        return self.wrong_input_count.get(flow_key, 0)


class ConversationManager:
    """Manages all user conversations"""

    def __init__(self):
        self.sessions: Dict[int, ConversationState] = {}

    def get_session(self, user_id: int) -> ConversationState:
        """
        ✅ FIXED: Get or create user session with proper initialization
        """
        if user_id not in self.sessions:
            self.sessions[user_id] = ConversationState(user_id)

        # ✅ Ensure collected_data is always a dict
        session = self.sessions[user_id]
        if not isinstance(session.collected_data, dict):
            session.collected_data = {}

        return session

    def reset_session(self, user_id: int):
        """✅ FIXED: Completely reset user session"""
        if user_id in self.sessions:
            self.sessions[user_id].reset()

    def clear_partial_flow(self, user_id: int, flow: str = None):
        """
        ✅ FIXED: Clear partial data for a specific flow or all flows

        Args:
            user_id: User identifier
            flow: Flow to clear (bmi, calories, workout) or None for all
        """
        session = self.get_session(user_id)

        if flow:
            # Clear specific flow
            flow_key = flow.lower()
            session.reset_wrong_input(flow_key)

            # Clear flow-specific collected data
            if flow_key in session.collected_data:
                session.collected_data.pop(flow_key, None)

            # ✅ FIXED: Only clear current_flow if it matches
            if session.current_flow and session.current_flow.lower() == flow_key:
                session.current_flow = None
                session.flow_step = 0
        else:
            # Clear all flows completely
            session.reset()


# Global conversation manager instance
conversation_manager = ConversationManager()