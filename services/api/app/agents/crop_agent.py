r"""
Crop Agent for crop-specific agricultural advice
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

from ..llm_client import LLMClient

class CropAgent:
    def __init__(self):
        self.name = "crop_agent"
        self.llm_client = LLMClient()
    
    def process_query(self, query: str, location: str = None, crop: str = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process crop-related queries"""
        # Prefer LLM-based comprehensive crop advice
        try:
            return self._generate_llm_crop_advice(query, location, crop, context)
        except Exception:
            pass
        query_lower = query.lower()
        
        # Irrigation queries
        if any(word in query_lower for word in ["irrigation", "water", "irrigate"]):
            return self._get_irrigation_advice(location, crop)
        
        # Fertilizer queries
        elif any(word in query_lower for word in ["fertilizer", "npk", "nutrient", "fertilize"]):
            return self._get_fertilizer_advice(location, crop)
        
        # Pest control queries
        elif any(word in query_lower for word in ["pest", "insect", "disease", "control", "spray"]):
            return self._get_pest_control_advice(location, crop)
        
        # Planting queries
        elif any(word in query_lower for word in ["plant", "sow", "transplant", "spacing"]):
            return self._get_planting_advice(location, crop)
        
        # General crop advice
        else:
            # Use context_summary if provided to tailor general advice
            if context and context.get("conversation_summary"):
                base = self._get_general_crop_advice(location, crop)
                summary = context.get("conversation_summary", "")
                pref = f"### Context\n{summary}\n\n"
                base["result"]["advice"] = pref + base["result"]["advice"]
                return base
            return self._get_general_crop_advice(location, crop)

    def _generate_llm_crop_advice(self, query: str, location: Optional[str], crop: Optional[str], context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Use LLM to generate comprehensive crop advice: suitability, irrigation, fertilizer, pests, planting, best practices."""
        context_summary = context.get("conversation_summary") if context else None
        last_q = context.get("last_agent_prompt") if context else None
        last_a = context.get("last_user_answer") if context else None
        prompt = f"""
You are an expert agronomist. Provide practical, specific advice.

CONSTRAINTS:
- You have a strict output budget. Keep the response under the model's max tokens.
- Prioritize finishing each section cleanly. If running out of space, truncate sections gracefully with a concluding sentence rather than mid-sentence cuts.
- Be concise; prefer bullet points over long paragraphs.

USER QUERY: "{query}"
LOCATION: {location or 'Not specified'}
TARGET CROP: {crop or 'Not specified (recommend suitable crops)'}
{('CONTEXT SUMMARY:\n' + context_summary) if context_summary else ''}
{('Last agent prompt: ' + last_q) if last_q else ''}
{('Last user reply: ' + last_a) if last_a else ''}

REQUIREMENTS:
- If the user asks which crop is suitable for their location, recommend top 3 crops for that region with reasoning.
- Otherwise, answer their crop-related question with concise, actionable steps.

Provide relevant sections (omit irrelevant ones). Keep total length compact so it fits within the output budget:
1) Suitability/Varieties
2) Water & Irrigation
3) Soil & Fertility (NPK)
4) Planting Window & Spacing
5) Pest/Disease Management
6) Yield & Economics (high-level)
7) Best Practices & Tips
""".strip()
        advice = self.llm_client.generate_text(prompt)
        urgency = "medium"
        if any(w in advice.lower() for w in ["urgent", "immediate", "critical"]):
            urgency = "high"
        evidence = [{
            "source": "llm_agronomy",
            "excerpt": advice[:180],
            "date": datetime.now().strftime("%Y-%m-%d"),
            "geo": location or "general",
            "crop": crop or "various"
        }]
        return {
            "agent": self.name,
            "result": {"advice": advice, "urgency": urgency},
            "evidence": evidence,
            "confidence": 0.9
        }
    
    def _get_irrigation_advice(self, location: str, crop: str) -> Dict[str, Any]:
        """Provide irrigation advice"""
        evidence = []
        advice = "Follow standard irrigation practices for your crop."
        
        if crop == "wheat":
            advice = "Wheat requires irrigation at crown root, tillering, jointing, flowering, and grain filling stages."
            evidence.append({
                "source": "wheat_irrigation_guide.pdf",
                "excerpt": "Apply 60:40:40 kg/ha NPK for wheat. Split application: 50% at sowing, 25% at tillering, 25% at flowering.",
                "date": "2024-02-01",
                "geo": "Punjab",
                "crop": "wheat"
            })
        
        elif crop == "rice":
            advice = "Rice requires continuous water supply. Maintain 2-3 cm water level during vegetative stage."
            evidence.append({
                "source": "icar_rice_guide.pdf",
                "excerpt": "Rice requires 120-150 days to mature. Transplant 25-30 day old seedlings at 20x15 cm spacing.",
                "date": "2024-01-15",
                "geo": "Karnataka",
                "crop": "rice"
            })
        
        elif crop == "maize":
            advice = "Maize responds well to irrigation at knee-high, tasseling, and grain-filling stages. Avoid waterlogging."
            evidence.append({
                "source": "maize_irrigation.pdf",
                "excerpt": "Maize responds well to irrigation at knee-high, tasseling, and grain-filling stages. Avoid waterlogging.",
                "date": "2024-02-10",
                "geo": "Bihar",
                "crop": "maize"
            })
        
        return {
            "agent": self.name,
            "result": {"advice": advice, "urgency": "medium"},
            "evidence": evidence,
            "confidence": 0.8
        }
    
    def _get_fertilizer_advice(self, location: str, crop: str) -> Dict[str, Any]:
        """Provide fertilizer advice"""
        evidence = []
        advice = "Apply balanced NPK fertilizers based on soil test results."
        
        if crop == "wheat":
            advice = "Apply 60:40:40 kg/ha NPK for wheat. Split application: 50% at sowing, 25% at tillering, 25% at flowering."
            evidence.append({
                "source": "wheat_fertilizer_guide.pdf",
                "excerpt": "Apply 60:40:40 kg/ha NPK for wheat. Split application: 50% at sowing, 25% at tillering, 25% at flowering.",
                "date": "2024-02-01",
                "geo": "Punjab",
                "crop": "wheat"
            })
        
        elif crop == "pulses":
            advice = "Apply 20:40:20 kg/ha NPK for pulses. Inoculate seeds with Rhizobium for better nitrogen fixation."
            evidence.append({
                "source": "pulses_fertilizer.pdf",
                "excerpt": "Apply 20:40:20 kg/ha NPK for pulses. Inoculate seeds with Rhizobium for better nitrogen fixation.",
                "date": "2024-02-05",
                "geo": "Madhya Pradesh",
                "crop": "pulses"
            })
        
        return {
            "agent": self.name,
            "result": {"advice": advice, "urgency": "medium"},
            "evidence": evidence,
            "confidence": 0.9
        }
    
    def _get_pest_control_advice(self, location: str, crop: str) -> Dict[str, Any]:
        """Provide pest control advice"""
        evidence = []
        advice = "Monitor for pests regularly and apply recommended pesticides when threshold levels are reached."
        
        if crop == "cotton":
            advice = "Cotton bollworm control: Apply Bt cotton or spray recommended insecticides at 5-7 day intervals."
            evidence.append({
                "source": "cotton_pest_guide.pdf",
                "excerpt": "Cotton bollworm control: Apply Bt cotton or spray recommended insecticides at 5-7 day intervals.",
                "date": "2024-03-01",
                "geo": "Gujarat",
                "crop": "cotton"
            })
        
        elif crop == "wheat":
            advice = "Monitor for yellow rust in wheat during February-March. Apply fungicide if disease severity exceeds 10%."
            evidence.append({
                "source": "wheat_disease_alert.pdf",
                "excerpt": "Monitor for yellow rust in wheat during February-March. Apply fungicide if disease severity exceeds 10%.",
                "date": "2024-02-15",
                "geo": "Haryana",
                "crop": "wheat"
            })
        
        return {
            "agent": self.name,
            "result": {"advice": advice, "urgency": "high"},
            "evidence": evidence,
            "confidence": 0.85
        }
    
    def _get_planting_advice(self, location: str, crop: str) -> Dict[str, Any]:
        """Provide planting advice"""
        evidence = []
        advice = "Follow recommended planting practices for optimal crop establishment."
        
        if crop == "rice":
            advice = "Rice requires 120-150 days to mature. Transplant 25-30 day old seedlings at 20x15 cm spacing."
            evidence.append({
                "source": "icar_rice_guide.pdf",
                "excerpt": "Rice requires 120-150 days to mature. Transplant 25-30 day old seedlings at 20x15 cm spacing.",
                "date": "2024-01-15",
                "geo": "Karnataka",
                "crop": "rice"
            })
        
        elif crop == "sugarcane":
            advice = "Sugarcane requires 12-18 months. Plant in February-March or September-October. Maintain soil moisture."
            evidence.append({
                "source": "sugarcane_calendar.pdf",
                "excerpt": "Sugarcane requires 12-18 months. Plant in February-March or September-October. Maintain soil moisture.",
                "date": "2024-01-20",
                "geo": "Maharashtra",
                "crop": "sugarcane"
            })
        
        elif crop == "groundnut":
            advice = "Groundnut requires 90-120 days. Plant in June-July for kharif. Maintain proper spacing of 30x10 cm."
            evidence.append({
                "source": "groundnut_guide.pdf",
                "excerpt": "Groundnut requires 90-120 days. Plant in June-July for kharif. Maintain proper spacing of 30x10 cm.",
                "date": "2024-01-25",
                "geo": "Andhra Pradesh",
                "crop": "groundnut"
            })
        
        return {
            "agent": self.name,
            "result": {"advice": advice, "urgency": "medium"},
            "evidence": evidence,
            "confidence": 0.8
        }
    
    def _get_general_crop_advice(self, location: str, crop: str) -> Dict[str, Any]:
        """Provide general crop advice"""
        advice = "Follow recommended agricultural practices for optimal crop production and yield."
        
        return {
            "agent": self.name,
            "result": {"advice": advice, "urgency": "low"},
            "evidence": [],
            "confidence": 0.5
        }
