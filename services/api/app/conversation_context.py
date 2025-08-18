"""
Conversation Context Manager for Agentic Agri Advisor
Manages conversational state across multiple interactions
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import uuid
import re


class ConversationContext:
    """Manages conversation state for a single user session"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.created_at = datetime.now()
        self.last_updated = datetime.now()
        self.conversation_history = []
        self.active_agent = None
        self.agent_state = {}  # Agent-specific state
        self.user_profile = {}  # Accumulated user information
        self.pending_questions = []  # Questions agent is waiting for answers to
        self.expecting_response = False  # Whether agent is waiting for user response
        self.context_understanding = {}  # Context from previous interactions
        
    def add_interaction(self, query: str, agent_used: str, response: Dict[str, Any], is_followup_question: bool = False):
        """Add a new interaction to conversation history"""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "agent_used": agent_used,
            "response": response,
            "is_followup_question": is_followup_question,
            "extracted_entities": self._extract_entities(query)
        }
        
        self.conversation_history.append(interaction)
        self.last_updated = datetime.now()
        
        # Update active agent and state
        if is_followup_question:
            self.active_agent = agent_used
            self.expecting_response = True
            self._extract_pending_questions(response)
        else:
            # Check if this response contains follow-up questions
            if self._response_has_questions(response):
                self.active_agent = agent_used
                self.expecting_response = True
                self._extract_pending_questions(response)
            else:
                self.active_agent = None
                self.expecting_response = False
                self.pending_questions = []
        
        # Update user profile with extracted information
        self._update_user_profile(query, response)
    
    def is_response_to_agent(self, query: str) -> Tuple[bool, Optional[str]]:
        """Determine if query is a response to pending agent questions"""
        if not self.expecting_response or not self.active_agent:
            return False, None
        
        # Check if query contains information requested by agent
        if self._contains_requested_information(query):
            return True, self.active_agent
        
        # Check if query is explicitly switching to a new topic/agent
        if self._is_explicit_topic_switch(query):
            return False, None
        
        # If we're in a conversation and query seems like follow-up, assume it's for active agent
        if self._seems_like_followup(query):
            return True, self.active_agent
        
        return False, None
    
    def should_continue_with_agent(self, query: str, agent_name: str) -> bool:
        """Check if we should continue with the current agent"""
        if self.active_agent != agent_name:
            return False
        
        if not self.expecting_response:
            return False
        
        # If query contains financial information and finance agent is active
        if agent_name == "finance_agent" and self._contains_financial_info(query):
            return True
        
        # If query seems to be answering pending questions
        if self._answers_pending_questions(query):
            return True
        
        return False
    
    def _extract_entities(self, query: str) -> Dict[str, Any]:
        """Extract entities from user query"""
        entities = {}
        query_lower = query.lower()
        
        # Extract financial information
        financial_patterns = {
            'land_size': r'(\d+(?:\.\d+)?)\s*(?:acres?|hectares?)',
            'cost_amount': r'₹?(\d+(?:,\d+)*(?:\.\d+)?)',
            'production': r'(\d+(?:\.\d+)?)\s*(?:quintals?|kg|tons?)',
            'percentage': r'(\d+(?:\.\d+)?)%'
        }
        
        for entity_type, pattern in financial_patterns.items():
            matches = re.findall(pattern, query_lower)
            if matches:
                entities[entity_type] = matches
        
        # Extract crops mentioned
        crops = ['wheat', 'rice', 'cotton', 'sugarcane', 'maize', 'barley', 'pulses']
        mentioned_crops = [crop for crop in crops if crop in query_lower]
        if mentioned_crops:
            entities['crops'] = mentioned_crops
        
        # Extract locations
        locations = ['karnataka', 'punjab', 'haryana', 'gujarat', 'maharashtra', 'uttar pradesh', 'rajasthan']
        mentioned_locations = [loc for loc in locations if loc in query_lower]
        if mentioned_locations:
            entities['locations'] = mentioned_locations
        
        return entities
    
    def _response_has_questions(self, response: Dict[str, Any]) -> bool:
        """Check if response contains follow-up questions"""
        # Check for finance agent form data (structured form)
        if "form_data" in response.get("result", {}):
            return True
        
        answer = response.get("result", {}).get("advice", "")
        if not answer:
            answer = response.get("answer", "")
        
        # Look for question indicators
        question_indicators = [
            "please share", "please provide", "need more", "can you tell",
            "what is your", "how much", "how many", "which type",
            "📊 Please share", "information:", "details:", "?", "questions:",
            "form", "fill", "provide details"
        ]
        
        return any(indicator in answer.lower() for indicator in question_indicators)
    
    def _extract_pending_questions(self, response: Dict[str, Any]):
        """Extract questions that agent is asking"""
        answer = response.get("result", {}).get("advice", "")
        if not answer:
            answer = response.get("answer", "")
        
        # Extract numbered questions or bullet points
        question_patterns = [
            r'\*\*\d+\.\s*([^*]+)\*\*',  # **1. Question**
            r'\d+\.\s*([^\n]+)',         # 1. Question
            r'•\s*([^\n]+)',             # • Question
            r'-\s*([^\n]+)'              # - Question
        ]
        
        questions = []
        for pattern in question_patterns:
            matches = re.findall(pattern, answer)
            questions.extend(matches)
        
        self.pending_questions = [q.strip() for q in questions if q.strip()]
    
    def _contains_requested_information(self, query: str) -> bool:
        """Check if query contains information that was requested"""
        query_lower = query.lower()
        
        # Financial information indicators
        financial_keywords = [
            'acres', 'hectares', 'quintals', 'cost', 'spend', 'annual',
            'fertilizer', 'water', 'irrigation', 'labor', 'machinery',
            'production', 'yield', 'price', 'selling', 'farm', 'land'
        ]
        
        # Check if query contains financial data
        has_financial_info = any(keyword in query_lower for keyword in financial_keywords)
        
        # Check if query contains numbers (likely answering quantity questions)
        has_numbers = bool(re.search(r'\d+', query))
        
        # Additional patterns for financial responses
        financial_response_patterns = [
            r'my\s+(farm|land|cost|production|spend)',  # "my farm is", "my cost is"
            r'i\s+(have|spend|produce|own)',  # "I have 5 acres", "I spend 30000"
            r'\d+\s*(acres?|hectares?|quintals?|rupees?|₹)',  # Numbers with units
        ]
        
        has_financial_patterns = any(re.search(pattern, query_lower) for pattern in financial_response_patterns)
        
        return (has_financial_info and has_numbers) or has_financial_patterns
    
    def _contains_financial_info(self, query: str) -> bool:
        """Check if query contains financial information"""
        query_lower = query.lower()
        
        financial_patterns = [
            r'₹?\d+',  # Currency amounts
            r'\d+\s*(?:acres?|hectares?)',  # Land size
            r'\d+\s*(?:quintals?|kg|tons?)',  # Production
            r'spend|cost|expense|annual'  # Cost-related words
        ]
        
        return any(re.search(pattern, query_lower) for pattern in financial_patterns)
    
    def _is_explicit_topic_switch(self, query: str) -> bool:
        """Check if user is explicitly switching topics/agents"""
        switch_indicators = [
            "now tell me about", "what about", "instead", "rather than",
            "forget that", "never mind", "actually", "let's talk about",
            "change topic", "different question", "new question"
        ]
        
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in switch_indicators)
    
    def _seems_like_followup(self, query: str) -> bool:
        """Check if query seems like a follow-up to previous conversation"""
        followup_indicators = [
            "also", "and", "my", "i", "yes", "no", "that is", "it is",
            "here are", "the", "additionally", "plus", "furthermore"
        ]
        
        query_lower = query.lower().strip()
        
        # Short queries starting with followup words are likely continuations
        if len(query_lower.split()) <= 10:
            return any(query_lower.startswith(indicator) for indicator in followup_indicators)
        
        return False
    
    def _answers_pending_questions(self, query: str) -> bool:
        """Check if query seems to answer pending questions"""
        if not self.pending_questions:
            return False
        
        query_lower = query.lower()
        
        # Look for answers to specific question types
        for question in self.pending_questions:
            question_lower = question.lower()
            
            # If question asks about farm size and query mentions acres/hectares
            if any(word in question_lower for word in ['farm size', 'acres', 'land']) and \
               any(word in query_lower for word in ['acres', 'hectares']):
                return True
            
            # If question asks about costs and query mentions money/expenses
            if any(word in question_lower for word in ['cost', 'expense', 'spend']) and \
               any(word in query_lower for word in ['cost', 'spend', '₹', 'rupees']):
                return True
            
            # If question asks about production and query mentions quintals/yield
            if any(word in question_lower for word in ['production', 'yield']) and \
               any(word in query_lower for word in ['quintals', 'production', 'yield']):
                return True
        
        return False
    
    def _update_user_profile(self, query: str, response: Dict[str, Any]):
        """Update user profile with information from conversation"""
        entities = self._extract_entities(query)
        
        # Update profile with extracted entities
        for entity_type, values in entities.items():
            if entity_type not in self.user_profile:
                self.user_profile[entity_type] = []
            self.user_profile[entity_type].extend(values)
        
        # Update agent-specific state
        agent_used = response.get("agent", "unknown")
        if agent_used not in self.agent_state:
            self.agent_state[agent_used] = {}
        
        # Store session IDs for future reference
        if "session_id" in response:
            self.agent_state[agent_used]["session_id"] = response["session_id"]
    
    def get_context_summary(self) -> str:
        """Get a summary of conversation context"""
        if not self.conversation_history:
            return "No previous conversation"
        
        summary_parts = []
        
        # Recent interactions
        recent = self.conversation_history[-3:]  # Last 3 interactions
        summary_parts.append(f"Recent interactions: {len(recent)} exchanges")
        
        # Active agent and state
        if self.active_agent and self.expecting_response:
            summary_parts.append(f"Active conversation with {self.active_agent}")
            if self.pending_questions:
                summary_parts.append(f"Waiting for answers to {len(self.pending_questions)} questions")
        
        # User profile highlights
        if self.user_profile:
            profile_summary = []
            for key, values in self.user_profile.items():
                if values:
                    profile_summary.append(f"{key}: {values[-1]}")  # Latest value
            if profile_summary:
                summary_parts.append(f"Known: {', '.join(profile_summary)}")
        
        return " | ".join(summary_parts)


class ConversationContextManager:
    """Manages conversation contexts for all users"""
    
    def __init__(self):
        self.sessions = {}
        self.session_timeout = timedelta(hours=4)  # Longer timeout for conversations
    
    def get_or_create_context(self, session_id: str = None) -> ConversationContext:
        """Get existing context or create new one"""
        if not session_id:
            session_id = str(uuid.uuid4())[:12]
        
        # Clean expired sessions
        self._cleanup_expired_sessions()
        
        if session_id not in self.sessions:
            self.sessions[session_id] = ConversationContext(session_id)
        
        return self.sessions[session_id]
    
    def update_context(self, session_id: str, query: str, agent_used: str, 
                      response: Dict[str, Any], is_followup_question: bool = False):
        """Update conversation context"""
        if session_id in self.sessions:
            context = self.sessions[session_id]
            context.add_interaction(query, agent_used, response, is_followup_question)
    
    def should_route_to_active_agent(self, session_id: str, query: str) -> Tuple[bool, Optional[str]]:
        """Check if query should go to currently active agent"""
        if session_id not in self.sessions:
            return False, None
        
        context = self.sessions[session_id]
        return context.is_response_to_agent(query)
    
    def get_context_for_routing(self, session_id: str) -> Dict[str, Any]:
        """Get context information for intelligent routing"""
        if session_id not in self.sessions:
            return {}
        
        context = self.sessions[session_id]
        return {
            "session_id": session_id,
            "active_agent": context.active_agent,
            "expecting_response": context.expecting_response,
            "user_profile": context.user_profile,
            "conversation_summary": context.get_context_summary(),
            "last_interaction": context.conversation_history[-1] if context.conversation_history else None
        }
    
    def _cleanup_expired_sessions(self):
        """Remove expired sessions"""
        current_time = datetime.now()
        expired_sessions = [
            session_id for session_id, context in self.sessions.items()
            if current_time - context.last_updated > self.session_timeout
        ]
        
        for session_id in expired_sessions:
            del self.sessions[session_id]


# Global conversation context manager
conversation_manager = ConversationContextManager()
