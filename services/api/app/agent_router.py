"""
Intelligent Agent Router for determining which agent should handle a query
"""

from typing import List, Dict, Any
import json
import os

class AgentRouter:
    def __init__(self):
        self.name = "agent_router"
        self.routing_rules = self._load_routing_rules()
    
    def _load_routing_rules(self) -> Dict[str, Any]:
        """Load routing rules and agent responsibilities"""
        return {
            "agents": {
                "policy": {
                    "description": "Handles government schemes, subsidies, loans, credits, insurance, eligibility, applications, and all policy-related matters",
                    "examples": [
                        "PM-KISAN scheme details",
                        "How to apply for crop insurance",
                        "Subsidies for organic farming",
                        "Kisan Credit Card eligibility",
                        "Government loan schemes",
                        "Agricultural assistance programs",
                        "Pension schemes for farmers",
                        "Policy documents and forms"
                    ]
                },
                "finance": {
                    "description": "Handles market prices, MSP (Minimum Support Price), commodity rates, trading, and pure financial market analysis",
                    "examples": [
                        "Current wheat market price",
                        "MSP for paddy this season",
                        "Commodity trading rates",
                        "Market trends analysis",
                        "Price forecasting",
                        "Mandi rates today"
                    ]
                },
                "weather": {
                    "description": "Handles weather forecasts, climate conditions, irrigation timing, and weather-related agricultural advice",
                    "examples": [
                        "Weather forecast for next week",
                        "When should I irrigate my crops",
                        "Rainfall predictions",
                        "Temperature alerts",
                        "Drought conditions",
                        "Best planting weather"
                    ]
                },
                "crop": {
                    "description": "Handles crop cultivation advice, fertilizers, pest management, disease control, and agricultural practices",
                    "examples": [
                        "NPK recommendations for wheat",
                        "Pest control for cotton",
                        "Disease management in tomatoes",
                        "Fertilizer application timing",
                        "Crop spacing guidelines",
                        "Soil preparation methods"
                    ]
                }
            }
        }
    
    def route_query(self, query: str, location: str = None, crop: str = None) -> List[str]:
        """
        Intelligently determine which agent(s) should handle the query
        Returns a list of agent names in order of relevance
        """
        query_lower = query.lower()
        
        # Analyze query intent and content
        intent_analysis = self._analyze_query_intent(query_lower)
        
        # Determine primary and secondary agents
        relevant_agents = []
        
        # Policy Agent - Government schemes, subsidies, loans, credits, insurance, applications
        if self._is_policy_query(query_lower, intent_analysis):
            relevant_agents.append("policy")
        
        # Finance Agent - Market prices, MSP, commodity rates, trading
        if self._is_finance_query(query_lower, intent_analysis):
            relevant_agents.append("finance")
        
        # Weather Agent - Weather forecasts, climate, irrigation timing
        if self._is_weather_query(query_lower, intent_analysis):
            relevant_agents.append("weather")
        
        # Crop Agent - Cultivation, fertilizers, pest control, diseases
        if self._is_crop_query(query_lower, intent_analysis):
            relevant_agents.append("crop")
        
        # Default fallback if no specific agent identified
        if not relevant_agents:
            # For general queries, try crop and weather as they provide basic agricultural advice
            relevant_agents = ["crop", "weather"]
        
        return relevant_agents
    
    def _analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """Analyze the intent and context of the query"""
        analysis = {
            "has_application_intent": False,
            "has_eligibility_intent": False,
            "has_price_intent": False,
            "has_forecast_intent": False,
            "has_technical_intent": False,
            "mentions_government": False,
            "mentions_scheme": False,
            "mentions_market": False,
            "mentions_weather": False
        }
        
        # Application/Process intent
        application_terms = ["apply", "application", "form", "process", "procedure", "how to", "steps", "register", "enroll"]
        analysis["has_application_intent"] = any(term in query for term in application_terms)
        
        # Eligibility intent
        eligibility_terms = ["eligible", "eligibility", "qualify", "criteria", "requirement", "who can", "am i eligible"]
        analysis["has_eligibility_intent"] = any(term in query for term in eligibility_terms)
        
        # Price/Market intent
        price_terms = ["price", "rate", "cost", "msp", "market", "mandi", "selling", "trading", "value"]
        analysis["has_price_intent"] = any(term in query for term in price_terms)
        
        # Forecast/Prediction intent
        forecast_terms = ["forecast", "prediction", "future", "next", "upcoming", "tomorrow", "week", "will it"]
        analysis["has_forecast_intent"] = any(term in query for term in forecast_terms)
        
        # Technical/Cultivation intent
        technical_terms = ["fertilizer", "pest", "disease", "npk", "spray", "treatment", "cultivation", "spacing"]
        analysis["has_technical_intent"] = any(term in query for term in technical_terms)
        
        # Context mentions
        government_terms = ["government", "pm-kisan", "nabard", "ministry", "scheme", "policy", "official"]
        analysis["mentions_government"] = any(term in query for term in government_terms)
        
        scheme_terms = ["scheme", "program", "yojana", "benefit", "assistance", "support"]
        analysis["mentions_scheme"] = any(term in query for term in scheme_terms)
        
        market_terms = ["market", "mandi", "commodity", "trading", "exchange"]
        analysis["mentions_market"] = any(term in query for term in market_terms)
        
        weather_terms = ["weather", "rain", "temperature", "climate", "forecast", "storm"]
        analysis["mentions_weather"] = any(term in query for term in weather_terms)
        
        return analysis
    
    def _is_policy_query(self, query: str, intent: Dict[str, Any]) -> bool:
        """Determine if query should go to Policy Agent"""
        
        # Direct policy terms
        policy_terms = [
            "subsidy", "subsidies", "scheme", "policy", "government", "pm-kisan", "nabard",
            "loan", "credit", "kcc", "kisan credit card", "insurance", "pmfby", "fasal bima",
            "pension", "pm-kmy", "grant", "benefit", "assistance", "support", "yojana",
            "eligible", "eligibility", "apply", "application", "form", "document"
        ]
        
        if any(term in query for term in policy_terms):
            return True
        
        # Intent-based detection
        if intent["has_application_intent"] or intent["has_eligibility_intent"]:
            if intent["mentions_government"] or intent["mentions_scheme"]:
                return True
        
        # Specific scheme mentions
        specific_schemes = [
            "organic farming", "mechanization", "tractor loan", "gold loan",
            "crop insurance", "pradhan mantri", "central government", "state government"
        ]
        
        if any(scheme in query for scheme in specific_schemes):
            return True
        
        return False
    
    def _is_finance_query(self, query: str, intent: Dict[str, Any]) -> bool:
        """Determine if query should go to Finance Agent"""
        
        # Market and price specific terms
        finance_terms = [
            "market price", "msp", "minimum support price", "commodity rate", 
            "mandi rate", "trading price", "selling price", "current price",
            "price trend", "market analysis", "commodity exchange"
        ]
        
        if any(term in query for term in finance_terms):
            return True
        
        # Intent-based detection for pure market queries
        if intent["has_price_intent"] and intent["mentions_market"]:
            # Make sure it's not a loan/credit query (which should go to policy)
            policy_exclusions = ["loan", "credit", "subsidy", "scheme", "insurance"]
            if not any(term in query for term in policy_exclusions):
                return True
        
        return False
    
    def _is_weather_query(self, query: str, intent: Dict[str, Any]) -> bool:
        """Determine if query should go to Weather Agent"""
        
        weather_terms = [
            "weather", "forecast", "rain", "rainfall", "drought", "temperature",
            "heat", "cold", "storm", "climate", "season", "monsoon",
            "irrigation timing", "when to water", "watering schedule"
        ]
        
        if any(term in query for term in weather_terms):
            return True
        
        # Irrigation queries are weather-dependent
        irrigation_terms = ["irrigation", "irrigate", "water", "watering"]
        if any(term in query for term in irrigation_terms):
            return True
        
        # Growing condition queries
        condition_terms = ["growing conditions", "suitable conditions", "planting time"]
        if any(term in query for term in condition_terms):
            return True
        
        return False
    
    def _is_crop_query(self, query: str, intent: Dict[str, Any]) -> bool:
        """Determine if query should go to Crop Agent"""
        
        crop_terms = [
            "fertilizer", "npk", "pest", "disease", "plant", "sow", "transplant",
            "spacing", "cultivation", "farming practice", "soil", "seed",
            "harvest", "crop management", "plant protection", "nutrients"
        ]
        
        if any(term in query for term in crop_terms):
            return True
        
        # Technical agricultural advice
        if intent["has_technical_intent"]:
            return True
        
        return False
    
    def get_routing_explanation(self, query: str, selected_agents: List[str]) -> str:
        """Provide explanation for why specific agents were selected"""
        explanations = []
        
        for agent in selected_agents:
            agent_info = self.routing_rules["agents"].get(agent, {})
            description = agent_info.get("description", f"{agent} agent")
            explanations.append(f"• {agent.title()} Agent: {description}")
        
        return f"Query: '{query}'\nSelected agents:\n" + "\n".join(explanations)
