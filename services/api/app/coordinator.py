"""
Coordinator service for orchestrating multiple agents
"""

from typing import Dict, List, Any
try:
    from .agents.weather_agent import WeatherAgent
    from .agents.crop_agent import CropAgent
    from .agents.finance_agent import FinanceAgent
    from .agents.policy_agent import PolicyAgent
except ImportError:
    # Handle case when running directly (not as module)
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from agents.weather_agent import WeatherAgent
    from agents.crop_agent import CropAgent
    from agents.finance_agent import FinanceAgent
    from agents.policy_agent import PolicyAgent


class Coordinator:
    def __init__(self):
        self.agents = {
            "weather": WeatherAgent(),
            "crop": CropAgent(),
            "finance": FinanceAgent(),
            "policy": PolicyAgent()
        }
    
    def process_query(self, query: str, location: str = None, crop: str = None) -> Dict[str, Any]:
        """Process query through relevant agents and synthesize response"""
        query_lower = query.lower()
        
        # Determine which agents to call
        relevant_agents = self._identify_relevant_agents(query_lower)
        
        # Get responses from agents
        agent_responses = []
        for agent_name in relevant_agents:
            if agent_name in self.agents:
                response = self.agents[agent_name].process_query(query, location, crop)
                agent_responses.append(response)
        
        # Synthesize responses
        return self._synthesize_responses(agent_responses, query)
    
    def _identify_relevant_agents(self, query: str) -> List[str]:
        """Identify which agents are relevant for the query"""
        relevant = []
        
        # Weather-related keywords - includes growing conditions
        weather_keywords = ["weather", "rain", "rainfall", "drought", "temperature", "heat", "cold", "storm", "forecast", "alert", "growing", "grow", "suitable", "conditions", "climate", "season"]
        if any(keyword in query for keyword in weather_keywords):
            relevant.append("weather")
        
        # Irrigation is weather-dependent, so include weather agent for irrigation queries
        irrigation_keywords = ["irrigation", "irrigate", "water", "watering"]
        if any(keyword in query for keyword in irrigation_keywords):
            relevant.append("weather")  # Weather is primary for irrigation decisions
            relevant.append("crop")     # Crop provides additional context
        
        # Other crop-related keywords
        crop_keywords = ["fertilizer", "npk", "pest", "disease", "plant", "sow", "transplant", "spacing"]
        if any(keyword in query for keyword in crop_keywords):
            relevant.append("crop")
        
        # Finance-related keywords
        finance_keywords = ["price", "market", "mandi", "rate", "cost", "subsidy", "loan", "credit", "bank", "finance", "money", "investment", "profit", "income"]
        if any(keyword in query for keyword in finance_keywords):
            relevant.append("finance")
        
        # Policy-related keywords
        policy_keywords = ["scheme", "policy", "government", "pm-kisan", "nabard", "eligible", "eligibility", "apply", "application", "form", "document", "insurance", "pmfby"]
        if any(keyword in query for keyword in policy_keywords):
            relevant.append("policy")
        
        # If no specific keywords, try crop and weather agents
        if not relevant:
            relevant = ["crop", "weather"]
        
        return relevant
    
    def _synthesize_responses(self, agent_responses: List[Dict[str, Any]], original_query: str) -> Dict[str, Any]:
        """Synthesize responses from multiple agents"""
        if not agent_responses:
            return {
                "answer": "I don't have specific information to answer this query.",
                "evidence": [],
                "confidence": 0.0,
                "agents_consulted": []
            }
        
        # Collect all evidence
        all_evidence = []
        all_advice = []
        total_confidence = 0.0
        agents_consulted = []
        
        highest_confidence_response = None
        max_confidence = 0.0
        
        for response in agent_responses:
            agent_name = response.get("agent", "unknown")
            agents_consulted.append(agent_name)
            
            result = response.get("result", {})
            advice = result.get("advice", "")
            if advice:
                all_advice.append(advice)
            
            evidence = response.get("evidence", [])
            all_evidence.extend(evidence)
            
            confidence = response.get("confidence", 0.0)
            total_confidence += confidence
            
            # Track the highest confidence response
            if confidence > max_confidence:
                max_confidence = confidence
                highest_confidence_response = response
        
        # Calculate average confidence
        avg_confidence = total_confidence / len(agent_responses) if agent_responses else 0.0
        
        # Synthesize answer - prioritize the highest confidence response
        if len(all_advice) == 1:
            answer = all_advice[0]
        elif highest_confidence_response and max_confidence > 0.8:
            # Use the highest confidence response as primary answer
            primary_advice = highest_confidence_response.get("result", {}).get("advice", "")
            other_advice = [advice for advice in all_advice if advice != primary_advice]
            if other_advice:
                answer = f"{primary_advice}\n\nAdditional insights: {' '.join(other_advice[:1])}"  # Limit additional insights
            else:
                answer = primary_advice
        else:
            # Combine all advice naturally
            answer = " ".join(all_advice)
        
        return {
            "answer": answer,
            "evidence": all_evidence,
            "confidence": round(avg_confidence, 3),
            "agents_consulted": agents_consulted,
            "agent_used": ", ".join(agents_consulted) if agents_consulted else "coordinator"
        }
