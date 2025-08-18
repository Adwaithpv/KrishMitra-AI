"""
Finance Session Manager for persistent user data collection
Manages financial information across multiple interactions
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import os
import uuid


class FinanceSessionManager:
    """Manages user financial data sessions"""
    
    def __init__(self):
        self.sessions = {}  # In-memory storage (can be replaced with Redis/DB)
        self.session_timeout = timedelta(hours=2)  # Sessions expire after 2 hours
        
    def get_or_create_session(self, user_id: str = None) -> str:
        """Get existing session or create new one"""
        if not user_id:
            user_id = str(uuid.uuid4())[:8]  # Generate session ID
        
        if user_id not in self.sessions:
            self.sessions[user_id] = {
                "created_at": datetime.now(),
                "last_updated": datetime.now(),
                "financial_data": {},
                "conversation_history": [],
                "form_completed": False,
                "missing_fields": []
            }
        
        return user_id
    
    def update_session_data(self, session_id: str, query: str, extracted_data: Dict[str, Any]):
        """Update session with new financial data"""
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        
        # Update financial data
        session["financial_data"].update(extracted_data)
        
        # Add to conversation history
        session["conversation_history"].append({
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "extracted_data": extracted_data
        })
        
        session["last_updated"] = datetime.now()
        
        # Check if form is completed
        session["form_completed"] = self._check_form_completion(session["financial_data"])
        session["missing_fields"] = self._get_missing_fields(session["financial_data"])
        
        return True
    
    def get_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        # Check if session expired
        if datetime.now() - session["last_updated"] > self.session_timeout:
            del self.sessions[session_id]
            return None
        
        return session
    
    def _check_form_completion(self, financial_data: Dict[str, Any]) -> bool:
        """Check if we have enough data for comprehensive analysis"""
        required_fields = [
            "land_size_acres",
            "annual_production",
            "fertilizer_cost",
            "water_cost"
        ]
        
        return all(field in financial_data for field in required_fields)
    
    def _get_missing_fields(self, financial_data: Dict[str, Any]) -> List[str]:
        """Get list of missing critical fields"""
        all_fields = {
            "land_size_acres": "Farm size (acres)",
            "annual_production": "Annual production (quintals)",
            "fertilizer_cost": "Annual fertilizer cost (INR)",
            "water_cost": "Annual water/irrigation cost (INR)",
            "labor_cost": "Annual labor cost (INR)",
            "seed_cost": "Annual seed cost (INR)",
            "machinery_cost": "Annual machinery cost (INR)",
            "selling_price": "Average selling price (INR/quintal)",
            "irrigation_type": "Irrigation method",
            "soil_type": "Soil type"
        }
        
        missing = []
        for field, description in all_fields.items():
            if field not in financial_data:
                missing.append({"field": field, "description": description})
        
        return missing
    
    def generate_finance_form(self, session_id: str, query: str) -> Dict[str, Any]:
        """Generate interactive finance form"""
        session = self.get_session_data(session_id)
        if not session:
            return self._error_response("Session not found")
        
        current_data = session["financial_data"]
        missing_fields = session["missing_fields"]
        
        # Create form HTML/JSON structure
        form_data = {
            "session_id": session_id,
            "form_type": "financial_information",
            "title": "🌾 Farm Financial Information Form",
            "description": "Please fill in your farm details to get personalized financial advice",
            "current_data": current_data,
            "fields": [
                {
                    "id": "land_size_acres",
                    "label": "Farm Size (acres)",
                    "type": "number",
                    "required": True,
                    "placeholder": "e.g., 5.5",
                    "value": current_data.get("land_size_acres", ""),
                    "help": "Total cultivable land area"
                },
                {
                    "id": "annual_production",
                    "label": "Annual Production (quintals)",
                    "type": "number", 
                    "required": True,
                    "placeholder": "e.g., 120",
                    "value": current_data.get("annual_production", ""),
                    "help": "Total annual crop production"
                },
                {
                    "id": "fertilizer_cost",
                    "label": "Annual Fertilizer Cost (₹)",
                    "type": "number",
                    "required": True,
                    "placeholder": "e.g., 30000",
                    "value": current_data.get("fertilizer_cost", ""),
                    "help": "Total yearly fertilizer expenses"
                },
                {
                    "id": "water_cost",
                    "label": "Annual Water/Irrigation Cost (₹)",
                    "type": "number",
                    "required": True,
                    "placeholder": "e.g., 25000",
                    "value": current_data.get("water_cost", ""),
                    "help": "Irrigation, electricity, water charges"
                },
                {
                    "id": "labor_cost",
                    "label": "Annual Labor Cost (₹)",
                    "type": "number",
                    "required": False,
                    "placeholder": "e.g., 40000",
                    "value": current_data.get("labor_cost", ""),
                    "help": "Hired labor and family labor costs"
                },
                {
                    "id": "seed_cost",
                    "label": "Annual Seed Cost (₹)",
                    "type": "number",
                    "required": False,
                    "placeholder": "e.g., 8000",
                    "value": current_data.get("seed_cost", ""),
                    "help": "Seeds, saplings, planting material"
                },
                {
                    "id": "machinery_cost",
                    "label": "Annual Machinery Cost (₹)",
                    "type": "number",
                    "required": False,
                    "placeholder": "e.g., 15000",
                    "value": current_data.get("machinery_cost", ""),
                    "help": "Tractor, equipment, maintenance costs"
                },
                {
                    "id": "selling_price",
                    "label": "Average Selling Price (₹/quintal)",
                    "type": "number",
                    "required": False,
                    "placeholder": "e.g., 2100",
                    "value": current_data.get("selling_price", ""),
                    "help": "Price you typically receive for your crop"
                },
                {
                    "id": "irrigation_type",
                    "label": "Irrigation Method",
                    "type": "select",
                    "required": False,
                    "options": [
                        {"value": "rainfed", "label": "Rainfed"},
                        {"value": "flood", "label": "Flood Irrigation"},
                        {"value": "drip", "label": "Drip Irrigation"},
                        {"value": "sprinkler", "label": "Sprinkler"}
                    ],
                    "value": current_data.get("irrigation_type", ""),
                    "help": "Primary irrigation method used"
                },
                {
                    "id": "soil_type",
                    "label": "Soil Type",
                    "type": "select",
                    "required": False,
                    "options": [
                        {"value": "sandy", "label": "Sandy Soil"},
                        {"value": "loamy", "label": "Loamy Soil"},
                        {"value": "clay", "label": "Clay Soil"},
                        {"value": "black_cotton", "label": "Black Cotton Soil"}
                    ],
                    "value": current_data.get("soil_type", ""),
                    "help": "Predominant soil type on your farm"
                }
            ],
            "completion_percentage": self._calculate_completion_percentage(current_data),
            "missing_critical_fields": len([f for f in missing_fields if f["field"] in ["land_size_acres", "annual_production", "fertilizer_cost", "water_cost"]]),
            "next_action": "submit_form" if session["form_completed"] else "continue_filling"
        }
        
        return {
            "agent": "finance_agent",
            "result": {
                "advice": self._format_form_response(form_data, query),
                "urgency": "medium",
                "form_data": form_data
            },
            "evidence": [{
                "source": "Interactive Financial Form",
                "excerpt": f"Collecting financial data - {form_data['completion_percentage']}% complete",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "geo": "user_session",
                "crop": "general"
            }],
            "confidence": 0.9
        }
    
    def _calculate_completion_percentage(self, financial_data: Dict[str, Any]) -> int:
        """Calculate form completion percentage"""
        total_fields = 10  # Total form fields
        filled_fields = len([v for v in financial_data.values() if v is not None and v != ""])
        return min(100, int((filled_fields / total_fields) * 100))
    
    def _format_form_response(self, form_data: Dict[str, Any], query: str) -> str:
        """Format the form as a user-friendly response"""
        completion = form_data["completion_percentage"]
        missing_critical = form_data["missing_critical_fields"]
        
        if completion >= 80:
            header = "## 🎉 Great! Your farm information is nearly complete!\n\n"
        elif completion >= 50:
            header = "## 📊 You're halfway there! Let's complete your farm profile.\n\n"
        else:
            header = "## 🌾 Let's build your farm financial profile step by step.\n\n"
        
        current_data_section = ""
        if form_data["current_data"]:
            current_data_section = "### ✅ Information Already Provided:\n"
            for field, value in form_data["current_data"].items():
                label = self._get_field_label(field)
                if value:
                    current_data_section += f"• **{label}:** {value}\n"
            current_data_section += "\n"
        
        if missing_critical > 0:
            missing_section = f"### 📝 Critical Information Needed ({missing_critical} remaining):\n\n"
            critical_fields = ["land_size_acres", "annual_production", "fertilizer_cost", "water_cost"]
            for field in critical_fields:
                if field not in form_data["current_data"] or not form_data["current_data"][field]:
                    label = self._get_field_label(field)
                    help_text = self._get_field_help(field)
                    missing_section += f"**{label}:** {help_text}\n\n"
        else:
            missing_section = "### 🎯 All critical information collected! Analyzing your data...\n\n"
        
        instructions = "### 💡 How to provide information:\n"
        instructions += "Simply tell me: *\"My farm is 5 acres, I spend ₹30,000 on fertilizers and ₹25,000 on water annually, and I produce 120 quintals per year.\"*\n\n"
        instructions += "I'll automatically extract and save this information for your financial analysis!"
        
        return header + current_data_section + missing_section + instructions
    
    def _get_field_label(self, field: str) -> str:
        """Get user-friendly field label"""
        labels = {
            "land_size_acres": "Farm Size",
            "annual_production": "Annual Production",
            "fertilizer_cost": "Fertilizer Cost",
            "water_cost": "Water/Irrigation Cost",
            "labor_cost": "Labor Cost",
            "seed_cost": "Seed Cost",
            "machinery_cost": "Machinery Cost",
            "selling_price": "Selling Price",
            "irrigation_type": "Irrigation Method",
            "soil_type": "Soil Type"
        }
        return labels.get(field, field.replace("_", " ").title())
    
    def _get_field_help(self, field: str) -> str:
        """Get field help text"""
        help_texts = {
            "land_size_acres": "How many acres do you cultivate?",
            "annual_production": "What's your total yearly production in quintals?",
            "fertilizer_cost": "How much do you spend on fertilizers per year?",
            "water_cost": "Annual irrigation and water expenses?",
            "labor_cost": "Yearly labor costs including hired and family labor",
            "seed_cost": "Annual expenses on seeds and planting material",
            "machinery_cost": "Tractor, equipment, and maintenance costs per year",
            "selling_price": "Average price you receive per quintal",
            "irrigation_type": "Your primary irrigation method",
            "soil_type": "Main soil type on your farm"
        }
        return help_texts.get(field, "Please provide this information")
    
    def _error_response(self, message: str) -> Dict[str, Any]:
        """Generate error response"""
        return {
            "agent": "finance_agent",
            "result": {"advice": f"Error: {message}", "urgency": "low"},
            "evidence": [],
            "confidence": 0.0
        }


# Global session manager instance
finance_session_manager = FinanceSessionManager()
