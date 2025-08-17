"""
Policy Agent for agricultural policy and scheme advice
"""

import json
import os
from typing import Dict, List, Any
from datetime import datetime


class PolicyAgent:
    def __init__(self):
        self.name = "policy_agent"
        self.schemes_data = self._load_schemes_data()
    
    def _load_schemes_data(self) -> Dict[str, Any]:
        """Load schemes data from JSON file"""
        try:
            # Navigate from app/agents/ to data/ directory
            current_dir = os.path.dirname(__file__)  # app/agents/
            app_dir = os.path.dirname(current_dir)   # app/
            api_dir = os.path.dirname(app_dir)       # api/
            data_file = os.path.join(api_dir, 'data', 'policy_schemes_data.json')
            with open(data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading schemes data: {e}")
            return {"schemes": []}
    
    def process_query(self, query: str, location: str = None, crop: str = None) -> Dict[str, Any]:
        """Process policy-related queries using structured data"""
        query_lower = query.lower()
        
        # Search for relevant schemes based on query keywords
        relevant_schemes = self._search_schemes(query_lower, location, crop)
        
        if not relevant_schemes:
            return self._get_general_policy_advice()
        
        # Return the most relevant scheme(s)
        return self._format_scheme_response(relevant_schemes, query_lower)
    
    def _search_schemes(self, query: str, location: str = None, crop: str = None) -> List[Dict[str, Any]]:
        """Search for relevant schemes based on query keywords"""
        relevant_schemes = []
        schemes = self.schemes_data.get("schemes", [])
        
        # Define search criteria based on query keywords
        search_criteria = {
            "pm-kisan": ["CENTRAL_PM-KISAN"],
            "pm kisan": ["CENTRAL_PM-KISAN"],
            "pension": ["CENTRAL_PM-KMY"],
            "insurance": ["CENTRAL_PMFBY"],
            "crop insurance": ["CENTRAL_PMFBY"],
            "pmfby": ["CENTRAL_PMFBY"],
            "fasal bima": ["CENTRAL_PMFBY"],
            "kisan credit card": ["CENTRAL_KCC"],
            "kcc": ["CENTRAL_KCC"],
            "credit": ["CENTRAL_KCC", "BANK_SBI_AGRI_GOLD_LOAN", "BANK_AXIS_TRACTOR_LOAN"],
            "loan": ["CENTRAL_KCC", "BANK_SBI_AGRI_GOLD_LOAN", "BANK_AXIS_TRACTOR_LOAN"],
            "gold loan": ["BANK_SBI_AGRI_GOLD_LOAN"],
            "tractor": ["BANK_AXIS_TRACTOR_LOAN"],
            "sugarcane": ["TN_SUGARCANE_INCENTIVE"],
            "organic": ["TN_ORGANIC_FARMING"],
            "mechanization": ["TN_MECHANIZATION"],
            "machinery": ["TN_MECHANIZATION"],
            "subsidy": ["TN_ORGANIC_FARMING", "TN_MECHANIZATION"],
            "itc": ["PRIVATE_ITC_MAARS"],
            "training": ["NGO_WOTR"],
            "watershed": ["NGO_WOTR"]
        }
        
        # Location-based filtering
        location_keywords = {
            "tamil nadu": "TN_",
            "tn": "TN_"
        }
        
        # Find schemes based on keywords
        matched_scheme_ids = set()
        
        # Check for specific scheme mentions
        for keyword, scheme_ids in search_criteria.items():
            if keyword in query:
                matched_scheme_ids.update(scheme_ids)
        
        # If no specific schemes found, search by general categories
        if not matched_scheme_ids:
            if any(word in query for word in ["scheme", "policy", "government", "central"]):
                # Return central government schemes
                matched_scheme_ids.update([s["id"] for s in schemes if s["category"] == "central_government"])
            elif any(word in query for word in ["bank", "banking", "finance"]):
                # Return banking schemes
                matched_scheme_ids.update([s["id"] for s in schemes if s["category"] == "banking"])
            elif location and any(loc in location.lower() for loc in ["tamil nadu", "tn"]):
                # Return state schemes for Tamil Nadu
                matched_scheme_ids.update([s["id"] for s in schemes if s["category"] == "state_government"])
        
        # Filter schemes by matched IDs
        for scheme in schemes:
            if scheme["id"] in matched_scheme_ids:
                relevant_schemes.append(scheme)
        
        # If still no matches, return top 3 central schemes
        if not relevant_schemes:
            central_schemes = [s for s in schemes if s["category"] == "central_government"]
            relevant_schemes = central_schemes[:3]
        
        return relevant_schemes
    
    def _format_scheme_response(self, schemes: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
        """Format the response with scheme information"""
        if not schemes:
            return self._get_general_policy_advice()
        
        # Determine if this is an application/eligibility query
        is_application_query = any(word in query for word in ["apply", "application", "how to", "process", "form"])
        is_eligibility_query = any(word in query for word in ["eligible", "eligibility", "qualify", "requirement"])
        
        advice_parts = []
        evidence = []
        urgency = "medium"
        
        for i, scheme in enumerate(schemes[:3], 1):  # Limit to top 3 schemes
            scheme_name = scheme["id"].replace("_", " ").title()
            
            # Add numbering and better formatting
            advice_parts.append(f"\n\n### {i}. {scheme_name}")
            
            if is_application_query:
                advice_parts.append(f"\n**📋 Application Process:**")
                for step in scheme['how_to_apply']:
                    advice_parts.append(f"\n• {step}")
                advice_parts.append(f"\n\n**🔗 Apply Online:** {scheme['application_link']}")
            elif is_eligibility_query:
                advice_parts.append(f"\n**✅ Eligibility:** {scheme['eligibility']}")
            else:
                advice_parts.append(f"\n**💰 Benefits:** {scheme['benefits']}")
                advice_parts.append(f"\n**✅ Eligibility:** {scheme['eligibility']}")
                if scheme.get('how_to_apply'):
                    advice_parts.append(f"\n**📋 How to Apply:** {scheme['how_to_apply'][0] if scheme['how_to_apply'] else 'Visit local agriculture office'}")
            
            # Create evidence from scheme data
            evidence.append({
                "source": f"{scheme['category'].replace('_', ' ').title()} - {scheme_name}",
                "excerpt": f"{scheme['objective']} | Benefits: {scheme['benefits']}",
                "date": "2024-01-01",
                "geo": "TN" if "TN_" in scheme["id"] else "India",
                "crop": "all"
            })
        
        # Enhanced main header with emoji
        main_advice = f"## 🌾 Agricultural Schemes Available ({len(schemes)} found)\n"
        if is_application_query:
            main_advice += "\n*Here's how to apply for these schemes:*"
        elif is_eligibility_query:
            main_advice += "\n*Check your eligibility below:*"
        else:
            main_advice += "\n*Here are the relevant schemes for you:*"
            
        full_advice = main_advice + "".join(advice_parts)
        
        # Add helpful footer
        if not is_application_query:
            full_advice += f"\n\n---\n\n**💡 Need help applying?** Visit your nearest agriculture office or check the official government portals for detailed application processes."
        
        if is_application_query or is_eligibility_query:
            urgency = "high"
        
        return {
            "agent": self.name,
            "result": {"advice": full_advice, "urgency": urgency},
            "evidence": evidence,
            "confidence": 0.9 if len(schemes) > 0 else 0.6
        }
    
    def _get_general_policy_advice(self) -> Dict[str, Any]:
        """Provide general policy advice when no specific schemes are found"""
        advice = ("Multiple agricultural schemes are available including PM-KISAN (₹6000/year), "
                 "PMFBY (crop insurance), KCC (credit), and state-specific schemes. "
                 "Visit your local agriculture office or check online portals for detailed information.")
        
        return {
            "agent": self.name,
            "result": {"advice": advice, "urgency": "low"},
            "evidence": [],
            "confidence": 0.6
        }
