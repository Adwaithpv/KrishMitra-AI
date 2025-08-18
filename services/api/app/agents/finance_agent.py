"""
Enhanced Finance Agent for agricultural financial advice and optimization
Provides crop pricing, market analysis, and personalized financial optimization
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import os
import re
from ..llm_client import LLMClient
from ..finance_session import finance_session_manager


class FinanceAgent:
    def __init__(self):
        self.name = "finance_agent"
        self.crop_prices = self._load_crop_prices()
        self.financial_parameters = self._get_financial_parameters_template()
        self.llm_client = LLMClient()
    
    def _load_crop_prices(self) -> Dict[str, Any]:
        """Load crop price data (placeholder until you add real data)"""
        # Default price data - you can replace this with your actual data source
        return {
            "wheat": {
                "current_price": 2100,
                "currency": "INR/quintal",
                "trend": "stable",
                "market_locations": ["Punjab", "Haryana", "UP"],
                "peak_season": "April-May",
                "min_price": 2000,
                "max_price": 2200,
                "demand": "high"
            },
            "rice": {
                "current_price": 2400,
                "currency": "INR/quintal", 
                "trend": "increasing",
                "market_locations": ["Punjab", "Tamil Nadu", "Andhra Pradesh"],
                "peak_season": "October-November",
                "min_price": 2200,
                "max_price": 2600,
                "demand": "very_high"
            },
            "cotton": {
                "current_price": 6500,
                "currency": "INR/quintal",
                "trend": "increasing",
                "market_locations": ["Gujarat", "Maharashtra", "Telangana"],
                "peak_season": "December-February",
                "min_price": 6000,
                "max_price": 7000,
                "demand": "high"
            },
            "sugarcane": {
                "current_price": 350,
                "currency": "INR/quintal",
                "trend": "stable",
                "market_locations": ["UP", "Maharashtra", "Karnataka"],
                "peak_season": "December-March",
                "min_price": 320,
                "max_price": 380,
                "demand": "stable"
            }
        }
    
    def _get_financial_parameters_template(self) -> Dict[str, Any]:
        """Define financial parameters needed for optimization"""
        return {
            "farm_details": {
                "land_size_acres": {"type": "float", "required": True, "description": "Total cultivable land in acres"},
                "irrigation_type": {"type": "select", "options": ["rainfed", "drip", "sprinkler", "flood"], "description": "Primary irrigation method"},
                "soil_type": {"type": "select", "options": ["sandy", "loamy", "clay", "black_cotton"], "description": "Predominant soil type"}
            },
            "current_expenses": {
                "seed_cost": {"type": "float", "description": "Annual seed expenses (INR)"},
                "fertilizer_cost": {"type": "float", "description": "Annual fertilizer expenses (INR)"},
                "water_cost": {"type": "float", "description": "Annual irrigation/water expenses (INR)"},
                "labor_cost": {"type": "float", "description": "Annual labor expenses (INR)"},
                "machinery_cost": {"type": "float", "description": "Annual machinery/equipment expenses (INR)"},
                "other_costs": {"type": "float", "description": "Other annual farming expenses (INR)"}
            },
            "current_yield": {
                "annual_production": {"type": "float", "description": "Current annual production (quintals)"},
                "selling_price": {"type": "float", "description": "Average selling price received (INR/quintal)"},
                "post_harvest_losses": {"type": "float", "description": "Estimated post-harvest losses (%)"}
            }
        }
    
    def _extract_financial_data_from_query(self, query: str) -> Dict[str, Any]:
        """Extract financial parameters from user query using pattern matching"""
        extracted_data = {}
        
        # Extract land size
        land_patterns = [
            r'(\d+(?:\.\d+)?)\s*acres?',
            r'(\d+(?:\.\d+)?)\s*hectares?',
            r'land.{0,20}(\d+(?:\.\d+)?)',
        ]
        for pattern in land_patterns:
            match = re.search(pattern, query.lower())
            if match:
                size = float(match.group(1))
                if 'hectare' in query.lower():
                    size = size * 2.47  # Convert hectares to acres
                extracted_data['land_size_acres'] = size
                break
        
        # Enhanced cost patterns with more variations
        cost_patterns = {
            'fertilizer_cost': [
                r'spend\s+(?:rs\.?\s*|₹\s*)?(\d+)\s+on\s+fertilizer[s]?',
                r'fertilizer[s]?\s+(?:cost[s]?\s+)?(?:rs\.?\s*|₹\s*)?(\d+)',
                r'(\d+)\s+(?:rs\.?\s*|₹\s*)?(?:for|on)\s+fertilizer[s]?',
                r'fertilizer[s]?\s+(?:expense[s]?\s+)?(?:rs\.?\s*|₹\s*)?(\d+)',
                r'(\d+)\s+rupees?\s+fertilizer[s]?'
            ],
            'water_cost': [
                r'spend\s+(?:rs\.?\s*|₹\s*)?(\d+)\s+on\s+(?:water|irrigation)',
                r'(?:water|irrigation)\s+(?:cost[s]?\s+)?(?:rs\.?\s*|₹\s*)?(\d+)',
                r'(\d+)\s+(?:rs\.?\s*|₹\s*)?(?:for|on)\s+(?:water|irrigation)',
                r'(?:water|irrigation)\s+(?:expense[s]?\s+)?(?:rs\.?\s*|₹\s*)?(\d+)',
                r'(\d+)\s+rupees?\s+(?:water|irrigation)'
            ],
            'seed_cost': [
                r'spend\s+(?:rs\.?\s*|₹\s*)?(\d+)\s+on\s+seed[s]?',
                r'seed[s]?\s+(?:cost[s]?\s+)?(?:rs\.?\s*|₹\s*)?(\d+)',
                r'(\d+)\s+(?:rs\.?\s*|₹\s*)?(?:for|on)\s+seed[s]?',
                r'seed[s]?\s+(?:expense[s]?\s+)?(?:rs\.?\s*|₹\s*)?(\d+)'
            ],
            'labor_cost': [
                r'spend\s+(?:rs\.?\s*|₹\s*)?(\d+)\s+on\s+labo[u]?r',
                r'labo[u]?r\s+(?:cost[s]?\s+)?(?:rs\.?\s*|₹\s*)?(\d+)',
                r'(\d+)\s+(?:rs\.?\s*|₹\s*)?(?:for|on)\s+labo[u]?r',
                r'labo[u]?r\s+(?:expense[s]?\s+)?(?:rs\.?\s*|₹\s*)?(\d+)',
                r'worker[s]?\s+(?:cost[s]?\s+)?(?:rs\.?\s*|₹\s*)?(\d+)'
            ],
            'machinery_cost': [
                r'spend\s+(?:rs\.?\s*|₹\s*)?(\d+)\s+on\s+(?:machiner[y]?|equipment|tractor)',
                r'(?:machiner[y]?|equipment|tractor)\s+(?:cost[s]?\s+)?(?:rs\.?\s*|₹\s*)?(\d+)',
                r'(\d+)\s+(?:rs\.?\s*|₹\s*)?(?:for|on)\s+(?:machiner[y]?|equipment|tractor)',
                r'(?:machiner[y]?|equipment|tractor)\s+(?:expense[s]?\s+)?(?:rs\.?\s*|₹\s*)?(\d+)'
            ]
        }
        
        for cost_type, patterns in cost_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, query.lower())
                if match:
                    extracted_data[cost_type] = float(match.group(1))
                    break
        
        # Detect total annual spend in Indian formats (e.g., 10 lakhs, 1.5 crore, 200k per year)
        total_spend_patterns = [
            r'(?:spend|spending|expense[s]?|cost|expenditure)\s*(?:around|about|nearly)?\s*(?:of\s*)?(\d+(?:\.\d+)?)\s*(lakhs?|lacs?|crores?|cr|crore|k|thousand)\b.*?(?:per\s*(?:year|annum)|annually)?',
            r'(?:spend|spending|expense[s]?|cost|expenditure)\s*(?:around|about|nearly)?\s*(?:of\s*)?(?:rs\.?\s*|₹\s*)?(\d+(?:\.\d+)?)(?!\s*(?:acres?|hectares?))\b.*?(?:per\s*(?:year|annum)|annually)'
        ]
        unit_multipliers = {
            "lakh": 100000,
            "lakhs": 100000,
            "lac": 100000,
            "lacs": 100000,
            "crore": 10000000,
            "crores": 10000000,
            "cr": 10000000,
            "k": 1000,
            "thousand": 1000,
        }
        for pattern in total_spend_patterns:
            m = re.search(pattern, query.lower())
            if m:
                amount = float(m.group(1))
                unit_match = re.search(r'(lakhs?|lacs?|crores?|cr|crore|k|thousand)', query.lower())
                if unit_match:
                    unit = unit_match.group(1)
                    mult = unit_multipliers.get(unit, 1)
                    amount = amount * mult
                extracted_data['total_annual_spend'] = float(amount)
                break
        
        # Extract production/yield
        yield_patterns = [
            r'yield\s+(?:of\s+)?(\d+(?:\.\d+)?)',
            r'production\s+(?:of\s+)?(\d+(?:\.\d+)?)',
            r'harvest\s+(?:of\s+)?(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s+quintals?',
            r'produce[s]?\s+(\d+(?:\.\d+)?)',
            r'get\s+(\d+(?:\.\d+)?)\s+quintals?',
            r'(\d+(?:\.\d+)?)\s+(?:quintal|qt|qtl)'
        ]
        for pattern in yield_patterns:
            match = re.search(pattern, query.lower())
            if match:
                extracted_data['annual_production'] = float(match.group(1))
                break
        
        return extracted_data
    
    def _generate_intelligent_financial_strategy(self, query: str, location: str, crop: str, extracted_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> str:
        """Use Gemini LLM to generate intelligent financial advice and strategies, with conversation context"""
        
        # Prepare comprehensive context for Gemini
        context_prompt = f"""
You are an expert agricultural financial advisor. Provide detailed, actionable financial advice and strategies for a farmer.

FARM PROFILE:
- Location: {location or 'Not specified'}
- Primary Crop: {crop or 'Not specified'}
- Query: {query}

FINANCIAL PARAMETERS DETECTED:
"""
        
        # Add conversation context if available
        if context and isinstance(context, dict):
            summary = context.get("conversation_summary")
            last_q = context.get("last_agent_prompt")
            last_a = context.get("last_user_answer")
            pending = context.get("pending_questions") or []
            if summary or last_q or last_a or pending:
                context_prompt += "\nCONVERSATION CONTEXT:\n"
                if summary:
                    context_prompt += f"- Summary: {summary}\n"
                if last_q:
                    context_prompt += f"- Last agent prompt: {last_q}\n"
                if last_a:
                    context_prompt += f"- Last user reply: {last_a}\n"
                if pending:
                    context_prompt += f"- Pending questions: {', '.join(pending[:3])}\n"

        # Add extracted financial data
        if extracted_data:
            for key, value in extracted_data.items():
                readable_key = key.replace('_', ' ').title()
                if 'cost' in key:
                    context_prompt += f"- {readable_key}: ₹{value:,.0f} annually\n"
                elif key == 'land_size_acres':
                    context_prompt += f"- {readable_key}: {value} acres\n"
                elif key == 'annual_production':
                    context_prompt += f"- {readable_key}: {value} quintals\n"
                elif key == 'total_annual_spend':
                    context_prompt += f"- Total Annual Spend: ₹{value:,.0f}\n"
                else:
                    context_prompt += f"- {readable_key}: {value}\n"
        else:
            context_prompt += "- No specific financial parameters provided\n"
        
        # Add crop price context if available
        if crop and crop.lower() in self.crop_prices:
            price_data = self.crop_prices[crop.lower()]
            context_prompt += f"""
CURRENT MARKET CONDITIONS FOR {crop.upper()}:
- Current Price: ₹{price_data['current_price']} per quintal
- Market Trend: {price_data['trend']}
- Demand Level: {price_data['demand']}
- Peak Season: {price_data['peak_season']}
"""
        
        # Add specific guidance for different query types
        if any(word in query.lower() for word in ["optimize", "reduce cost", "efficiency"]):
            context_prompt += """
FOCUS AREAS FOR OPTIMIZATION:
1. Cost reduction strategies specific to the farm size and current expenses
2. Input efficiency improvements (fertilizer, water, labor optimization)
3. Technology adoption recommendations with ROI analysis
4. Operational improvements and process optimization
5. Timing strategies for input procurement and sales
"""
        elif any(word in query.lower() for word in ["profit", "income", "revenue"]):
            context_prompt += """
FOCUS AREAS FOR PROFIT MAXIMIZATION:
1. Revenue enhancement strategies (pricing, quality, timing)
2. Value addition opportunities (processing, packaging, branding)
3. Market diversification and direct sales channels
4. Crop diversification and rotation strategies
5. Risk management for stable income
"""
        elif any(word in query.lower() for word in ["investment", "expansion", "growth"]):
            context_prompt += """
FOCUS AREAS FOR INVESTMENT & GROWTH:
1. Investment prioritization based on current financial position
2. Equipment and infrastructure recommendations
3. Financing options and capital structure optimization
4. Scalability analysis and expansion planning
5. Risk assessment for new investments
"""
        
        context_prompt += """
REQUIREMENTS FOR YOUR RESPONSE:
1. Provide specific, actionable strategies (not generic advice)
2. Include quantified benefits where possible (percentages, amounts)
3. Consider the farmer's current financial position and constraints
4. Prioritize recommendations by impact and feasibility
5. Include implementation timelines and steps
6. Address both short-term (1 year) and medium-term (3-5 years) strategies
7. Consider local market conditions and regional factors
8. Provide specific financial metrics to track progress

CONSTRAINTS:
- Keep the response within the model's output budget to avoid truncation.
- If space is running low, summarize remaining items succinctly and end with a brief conclusion.

Format your response with clear headings and bullet points for easy reading.
Use emojis sparingly and appropriately.
Ensure all advice is practical and implementable for the given farm profile.
"""
        
        # Generate intelligent advice using Gemini
        try:
            intelligent_advice = self.llm_client.generate_text(context_prompt)
            return intelligent_advice
        except Exception as e:
            # Fallback to structured advice if LLM fails
            return self._generate_fallback_structured_advice(extracted_data, crop)
    
    def _generate_fallback_structured_advice(self, extracted_data: Dict[str, Any], crop: str) -> str:
        """Generate structured advice when LLM is not available"""
        advice = "## 💼 Financial Strategy Recommendations\n\n"
        
        if extracted_data:
            advice += "### 📊 Based on Your Farm Profile\n"
            
            # Cost optimization
            total_costs = sum(value for key, value in extracted_data.items() if 'cost' in key)
            if total_costs > 0:
                advice += f"**Current Annual Input Costs:** ₹{total_costs:,.0f}\n"
                advice += f"**Optimization Target:** 15-20% reduction (₹{total_costs * 0.175:,.0f} savings)\n\n"
            
            # Specific recommendations based on data
            if 'fertilizer_cost' in extracted_data and extracted_data['fertilizer_cost'] > 25000:
                advice += "**🧪 Fertilizer Strategy:** Implement soil testing and precision application\n"
            
            if 'water_cost' in extracted_data and extracted_data['water_cost'] > 40000:
                advice += "**💧 Water Management:** Consider drip irrigation for significant savings\n"
            
            # Yield optimization
            if 'land_size_acres' in extracted_data and 'annual_production' in extracted_data:
                land_size = extracted_data['land_size_acres']
                production = extracted_data['annual_production']
                if land_size > 0:
                    yield_per_acre = production / land_size
                    advice += f"**📈 Productivity:** Current {yield_per_acre:.1f} quintals/acre\n"
        
        advice += "\n### 💡 Key Focus Areas\n"
        advice += "• Input cost optimization through efficient resource management\n"
        advice += "• Market timing strategies for better prices\n"
        advice += "• Technology adoption for productivity improvements\n"
        advice += "• Financial planning and cash flow management\n"
        
        return advice
    
    def _needs_follow_up_questions(self, extracted_data: Dict[str, Any], query: str) -> bool:
        """Determine if we need follow-up questions for better analysis"""
        print(f"DEBUG: _needs_follow_up_questions called with extracted_data = {extracted_data}")
        
        # Define critical parameters for comprehensive analysis
        critical_params = ['land_size_acres', 'annual_production']
        cost_params = ['fertilizer_cost', 'water_cost', 'labor_cost', 'seed_cost', 'machinery_cost']
        
        # Check if we have basic farm information
        has_basic_info = any(param in extracted_data for param in critical_params)
        has_cost_info = any(param in extracted_data for param in cost_params)
        
        # Count how many parameters we have
        total_params = len(extracted_data)
        cost_params_count = sum(1 for param in cost_params if param in extracted_data)
        
        # If we have sufficient data (4+ parameters including basic info), no need for follow-up
        if total_params >= 4 and has_basic_info and cost_params_count >= 2:
            return False
        
        # If no critical information is available, we need follow-up questions
        if not has_basic_info and not has_cost_info:
            return True
        
        # If asking for optimization/improvement but missing sufficient data
        optimization_keywords = ["optimize", "improve", "reduce cost", "efficiency", "better returns"]
        if any(keyword in query.lower() for keyword in optimization_keywords):
            # Need at least farm size + 2 cost parameters for good optimization advice
            if not has_basic_info or cost_params_count < 2:
                return True
        
        # If asking for profit analysis but missing production/revenue data
        profit_keywords = ["profit", "income", "revenue", "maximize"]
        if any(keyword in query.lower() for keyword in profit_keywords):
            if 'annual_production' not in extracted_data and 'land_size_acres' not in extracted_data:
                return True
        
        # If asking for general advice/help but have very limited data
        general_keywords = ["advice", "help", "strategy", "planning", "financial changes"]
        if any(keyword in query.lower() for keyword in general_keywords):
            if total_params < 2:
                return True
        
        return False
    
    def _generate_follow_up_questions(self, query: str, location: str, crop: str, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate intelligent follow-up questions to gather missing parameters"""
        
        # Create context for intelligent question generation
        questions_prompt = f"""
You are an expert agricultural financial advisor. A farmer has asked: "{query}"

CURRENT INFORMATION AVAILABLE:
- Location: {location or 'Not specified'}
- Crop: {crop or 'Not specified'}
- Extracted Parameters: {', '.join(extracted_data.keys()) if extracted_data else 'None'}

CONTEXT: The farmer wants financial advice but we need more specific information to provide personalized, actionable recommendations.

Generate 3-5 intelligent follow-up questions to gather the most important missing financial parameters. Focus on:

1. Farm scale (land size, production capacity)
2. Current expenses (fertilizers, seeds, water/irrigation, labor, machinery)
3. Current performance (yield, income, market prices received)
4. Infrastructure and technology (irrigation type, machinery usage, storage facilities)
5. Financial goals (specific improvement areas, investment capacity)

Make the questions:
- Specific and practical
- Easy to answer with numbers
- Relevant to Indian agriculture
- Focused on the most impactful financial parameters

Format as a numbered list of clear, direct questions.
"""
        
        try:
            # Use Gemini to generate intelligent questions
            ai_questions = self.llm_client.generate_text(questions_prompt)
            questions_text = ai_questions
        except Exception as e:
            # Fallback to structured questions based on what's missing
            questions_text = self._generate_fallback_questions(extracted_data, query)
        
        # Build the response
        main_header = "## 🤔 Let me help you with personalized financial advice!\n\n"
        context_section = f"I understand you want to **{self._extract_goal_from_query(query)}**. "
        context_section += "To provide the most effective recommendations, I need a few more details about your farm.\n\n"
        
        questions_section = "### 📊 Please share the following information:\n\n"
        questions_section += questions_text
        
        footer_section = "\n\n### 💡 Why these details matter:\n"
        footer_section += "• **Farm size & production:** Helps determine scale-appropriate strategies\n"
        footer_section += "• **Current expenses:** Identifies optimization opportunities\n"
        footer_section += "• **Technology usage:** Assesses upgrade potential and ROI\n"
        footer_section += "• **Financial goals:** Ensures recommendations align with your priorities\n\n"
        footer_section += "**📝 You can provide this information in your next message, and I'll generate a comprehensive financial strategy tailored specifically for your farm!**"
        
        full_response = main_header + context_section + questions_section + footer_section
        
        return {
            "agent": self.name,
            "result": {"advice": full_response, "urgency": "medium"},
            "evidence": [{
                "source": "Interactive Financial Analysis",
                "excerpt": "Follow-up questions generated to gather comprehensive farm financial data",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "geo": location or "General",
                "crop": crop or "all"
            }],
            "confidence": 0.9
        }
    
    def _extract_goal_from_query(self, query: str) -> str:
        """Extract the farmer's main goal from their query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["optimize", "reduce cost", "efficiency"]):
            return "optimize costs and improve efficiency"
        elif any(word in query_lower for word in ["profit", "income", "revenue", "maximize"]):
            return "increase profits and revenue"
        elif any(word in query_lower for word in ["yield", "production", "improve"]):
            return "improve yield and productivity"
        elif any(word in query_lower for word in ["investment", "expansion", "grow"]):
            return "plan investments and growth"
        elif any(word in query_lower for word in ["advice", "help", "strategy"]):
            return "get comprehensive financial advice"
        else:
            return "improve your farm's financial performance"
    
    def _generate_fallback_questions(self, extracted_data: Dict[str, Any], query: str) -> str:
        """Generate structured follow-up questions when AI is not available"""
        questions = []
        
        # Basic farm information
        if 'land_size_acres' not in extracted_data:
            questions.append("**1. Farm Size:** How many acres of land do you cultivate?")
        
        # Production information
        if 'annual_production' not in extracted_data:
            questions.append(f"**{len(questions)+1}. Annual Production:** What is your current annual yield/production (in quintals)?")
        
        # Cost information
        missing_costs = []
        cost_mapping = {
            'fertilizer_cost': 'fertilizers and nutrients',
            'water_cost': 'irrigation and water',
            'seed_cost': 'seeds',
            'labor_cost': 'labor',
            'machinery_cost': 'machinery and equipment'
        }
        
        for cost_param, description in cost_mapping.items():
            if cost_param not in extracted_data:
                missing_costs.append(description)
        
        if missing_costs:
            questions.append(f"**{len(questions)+1}. Annual Expenses:** What do you spend annually on: {', '.join(missing_costs[:3])}?")
        
        # Technology and infrastructure
        questions.append(f"**{len(questions)+1}. Irrigation & Technology:** What type of irrigation do you use? Do you own tractors or other heavy machinery?")
        
        # Financial goals
        questions.append(f"**{len(questions)+1}. Investment Capacity:** What is your budget for improvements or new investments?")
        
        return '\n'.join(questions)
    
    def process_query(self, query: str, location: str = None, crop: str = None, session_id: str = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process finance-related queries with enhanced capabilities, conversation context, and session-based data collection"""
        
        # Get or create session for this user
        print(f"DEBUG: Starting session management with session_id = {session_id}")
        if not session_id:
            session_id = finance_session_manager.get_or_create_session()
            print(f"DEBUG: Created new session_id = {session_id}")
        else:
            # Ensure session exists, create if it doesn't
            session_id = finance_session_manager.get_or_create_session(session_id)
            print(f"DEBUG: Ensured session exists: {session_id}")
        
        query_lower = query.lower()
        
        # Extract financial data from query
        extracted_data = self._extract_financial_data_from_query(query)
        # Merge last short answer from context for follow-ups
        if context and isinstance(context, dict):
            last_ans = context.get("last_user_answer")
            if last_ans and last_ans != query and len(query.strip().split()) <= 4:
                prev_data = self._extract_financial_data_from_query(last_ans)
                for k, v in prev_data.items():
                    extracted_data.setdefault(k, v)
        
        # Try to update session with new data
        try:
            update_success = finance_session_manager.update_session_data(session_id, query, extracted_data)
        except Exception as e:
            print(f"Warning: Session update failed: {e}")
            update_success = False
        
        # Get accumulated session data
        try:
            session = finance_session_manager.get_session_data(session_id)
            if session:
                all_financial_data = session["financial_data"]
                form_completed = session["form_completed"]
            else:
                # Fallback if session doesn't work
                all_financial_data = extracted_data
                form_completed = False
        except Exception as e:
            print(f"Warning: Session retrieval failed: {e}")
            # Complete fallback
            all_financial_data = extracted_data
            form_completed = False
        
        # Check if this is a query that would benefit from follow-up questions
        needs_detailed_analysis = any(word in query_lower for word in [
            "optimize", "improve", "increase yield", "profit", "efficiency", "expenses", 
            "cost reduction", "advice", "help", "strategy", "planning", "financial changes",
            "better returns", "maximize", "minimize costs", "grow business", "expansion"
        ])
        
        print(f"DEBUG: needs_detailed_analysis = {needs_detailed_analysis}")
        print(f"DEBUG: form_completed = {form_completed}")
        print(f"DEBUG: session_id = {session_id}")

        # Market price queries should return pricing even if prior finance data exists
        if any(word in query_lower for word in ["price", "market", "mandi", "rate", "selling", "sell"]):
            inferred_crop = crop
            if not inferred_crop:
                for c in ["wheat", "rice", "cotton", "maize", "pulses", "sugarcane", "groundnut"]:
                    if c in query_lower:
                        inferred_crop = c
                        break
            return self._get_enhanced_market_price_advice(query, location, inferred_crop)
        
        # Farm financial optimization queries with potential follow-ups
        if needs_detailed_analysis:
            # For optimization queries, ALWAYS provide immediate advice first
            immediate_advice = self._get_general_optimization_advice(query, location, crop, session_id, context=context)
            
            # Only try to add form if we have a working session
            if session_id and form_completed is False:
                try:
                    form_response = finance_session_manager.generate_finance_form(session_id, query)
                    if isinstance(form_response, dict) and "form_data" in form_response.get("result", {}):
                        immediate_advice["result"]["form_data"] = form_response["result"]["form_data"]
                        immediate_advice["result"]["advice"] += "\n\n---\n\n**💡 For personalized recommendations, please provide your farm details above.**"
                except Exception as e:
                    print(f"Warning: Form generation failed: {e}")
                    # Still return the optimization advice even if form fails
            
            return immediate_advice
        
        # If user provided financial details (even without keywords), generate personalized optimization
        significant_keys = ['land_size_acres','annual_production','fertilizer_cost','water_cost','labor_cost','seed_cost','machinery_cost','total_annual_spend']
        if any(k in all_financial_data for k in significant_keys):
            response = self._get_financial_optimization_advice(query, location, crop, all_financial_data, context=context)
            if isinstance(response, dict):
                response["session_id"] = session_id
            return response
        
        # Enhanced market price queries
        elif any(word in query_lower for word in ["price", "market", "mandi", "rate", "selling", "sell"]):
            return self._get_enhanced_market_price_advice(query, location, crop)
        
        # Farm economics analysis
        elif any(word in query_lower for word in ["income", "revenue", "profit", "economics", "budget", "financial analysis"]):
            if not form_completed and len(all_financial_data) < 3:
                return finance_session_manager.generate_finance_form(session_id, query)
            else:
                response = self._get_farm_economics_advice(query, location, crop, all_financial_data, context=context)
                if isinstance(response, dict):
                    response["session_id"] = session_id
                return response
        
        # Credit and financing queries
        elif any(word in query_lower for word in ["credit", "loan", "bank", "finance", "money", "investment", "capital", "funding"]):
            return self._get_credit_advice(location, crop)
        
        # General financial advice
        else:
            return self._get_general_finance_advice(location, crop)
    
    def _get_enhanced_market_price_advice(self, query: str, location: str, crop: str) -> Dict[str, Any]:
        """Provide enhanced market price advice with detailed market analysis"""
        
        if not crop or crop.lower() not in self.crop_prices:
            return self._get_general_price_advice()
        
        price_data = self.crop_prices[crop.lower()]
        evidence = []
        
        # Build comprehensive price analysis
        main_header = f"## 💰 {crop.title()} Market Analysis\n\n"
        
        # Current pricing section
        price_section = f"### 📊 Current Market Prices\n"
        price_section += f"**Current Price:** ₹{price_data['current_price']:,} {price_data['currency']}\n"
        price_section += f"**Market Trend:** {price_data['trend'].title()} 📈\n"
        price_section += f"**Price Range:** ₹{price_data['min_price']:,} - ₹{price_data['max_price']:,}\n"
        price_section += f"**Market Demand:** {price_data['demand'].replace('_', ' ').title()}\n\n"
        
        # Regional market information
        regional_section = f"### 🌍 Regional Markets\n"
        regional_section += f"**Best Markets:** {', '.join(price_data['market_locations'])}\n"
        regional_section += f"**Peak Selling Season:** {price_data['peak_season']}\n\n"
        
        # Selling recommendations
        selling_section = f"### 💡 Selling Recommendations\n"
        if price_data['trend'] == 'increasing':
            selling_section += "🔥 **Recommendation:** HOLD - Prices are trending upward. Consider waiting for peak season.\n"
            urgency = "low"
        elif price_data['trend'] == 'stable':
            selling_section += "⚖️ **Recommendation:** SELL NOW - Stable prices suggest good time to sell.\n"
            urgency = "medium"
        else:
            selling_section += "⚡ **Recommendation:** SELL IMMEDIATELY - Prices may decline further.\n"
            urgency = "high"
        
        # Market timing advice
        timing_section = f"\n### ⏰ Timing Strategy\n"
        if "peak" in query.lower() or "when" in query.lower():
            timing_section += f"**Peak Season:** {price_data['peak_season']}\n"
            timing_section += f"**Strategy:** Plan harvesting and storage to align with peak pricing periods.\n"
        
        # Quality and grading tips
        quality_section = f"\n### ✅ Quality Enhancement Tips\n"
        quality_section += "• Ensure proper drying and storage to get premium prices\n"
        quality_section += "• Grade your produce - higher grades command 10-15% premium\n"
        quality_section += "• Consider direct marketing to avoid middleman margins\n"
        
        full_advice = main_header + price_section + regional_section + selling_section + timing_section + quality_section
        
        # Add evidence
        evidence.extend([
            {
                "source": f"Agricultural Market Intelligence - {crop.title()}",
                "excerpt": f"Current market price: ₹{price_data['current_price']} per quintal with {price_data['trend']} trend",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "geo": location or "National",
                "crop": crop
            },
            {
                "source": "Market Demand Analysis",
                "excerpt": f"{price_data['demand'].replace('_', ' ').title()} demand in {', '.join(price_data['market_locations'])} markets",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "geo": "Multi-state",
                "crop": crop
            }
        ])
        
        return {
            "agent": self.name,
            "result": {"advice": full_advice, "urgency": urgency},
            "evidence": evidence,
            "confidence": 0.9
        }
    
    def _get_financial_optimization_advice(self, query: str, location: str, crop: str, extracted_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Provide personalized financial optimization advice using AI-powered analysis"""
        
        # Generate intelligent strategy using Gemini LLM
        main_header = f"## 🚀 AI-Powered Financial Strategy for {crop.title() if crop else 'Your Farm'}\n\n"
        
        # Parameter analysis section
        param_section = self._analyze_provided_parameters(extracted_data)
        
        # Generate intelligent financial strategy using Gemini
        ai_strategy_section = self._generate_intelligent_financial_strategy(query, location, crop, extracted_data, context=context)
        
        # Add practical implementation section
        implementation_section = "\n\n### 📋 Implementation Checklist\n"
        implementation_section += "**Immediate Actions (Next 30 days):**\n"
        implementation_section += "• Conduct detailed cost analysis of current operations\n"
        implementation_section += "• Research and compare input suppliers for better rates\n"
        implementation_section += "• Evaluate current yield vs. regional benchmarks\n\n"
        
        implementation_section += "**Short-term Goals (3-6 months):**\n"
        implementation_section += "• Implement identified cost reduction strategies\n"
        implementation_section += "• Upgrade critical equipment or infrastructure\n"
        implementation_section += "• Establish better market connections and pricing strategies\n\n"
        
        implementation_section += "**Medium-term Vision (1-3 years):**\n"
        implementation_section += "• Scale successful optimization strategies\n"
        implementation_section += "• Diversify income streams and reduce risk exposure\n"
        implementation_section += "• Build financial reserves and investment capacity\n"
        
        # Only add missing information prompt if we actually need more data
        total_params = len(extracted_data)
        if total_params < 4:  # Only show missing info prompt if we have less than 4 parameters
            missing_info_section = self._get_missing_info_prompt(extracted_data)
            full_advice = main_header + param_section + "\n" + ai_strategy_section + implementation_section + "\n" + missing_info_section
        else:
            # We have comprehensive data, no need for missing info section
            full_advice = main_header + param_section + "\n" + ai_strategy_section + implementation_section
        
        # Generate evidence
        evidence = [
            {
                "source": "Farm Financial Analysis",
                "excerpt": f"Analysis based on extracted parameters: {', '.join(extracted_data.keys())}",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "geo": location or "Farm-specific",
                "crop": crop or "all"
            },
            {
                "source": "Agricultural Economics Research",
                "excerpt": "Optimization strategies based on best practices in agricultural financial management",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "geo": "Research-based",
                "crop": crop or "all"
            }
        ]
        
        return {
            "agent": self.name,
            "result": {"advice": full_advice, "urgency": "high"},
            "evidence": evidence,
            "confidence": 0.85
        }
    
    def _get_credit_advice(self, location: str, crop: str) -> Dict[str, Any]:
        """Provide financial credit and banking advice"""
        advice = """## 🏦 Agricultural Credit & Banking Solutions

### 💳 Kisan Credit Card (KCC)
**Financial Benefits:**
• Credit limit up to ₹3 lakh for crop production
• Flexible repayment based on harvest cycles
• Competitive interest rates for agricultural credit
• Multi-purpose credit facility (crop, equipment, working capital)

**Financial Requirements:**
• Land ownership documents or lease agreements
• Bank account with credit history
• Income proof and repayment capacity assessment

### 🏦 Commercial Banking Options
• **Term Loans:** For equipment, infrastructure, and long-term investments
• **Working Capital:** Seasonal financing for crop cycles
• **Equipment Financing:** Tractors, machinery, and technology upgrades
• **Gold Loans:** Quick liquidity against gold assets

### 💰 Alternative Financing
• **Cooperative Banks:** Regional agricultural credit institutions
• **Microfinance:** Small-scale financing for inputs and equipment
• **Equipment Leasing:** Rent-to-own for expensive farm machinery
• **Invoice Financing:** Credit against crop contracts and advance sales

### 📊 Credit Optimization Strategies
• **Credit Score Management:** Maintain payment history for better rates
• **Collateral Utilization:** Leverage land and assets for lower interest rates
• **Loan Restructuring:** Negotiate terms based on cash flow patterns
• **Multiple Bank Relationships:** Compare rates and maintain options"""
        
        evidence = [
            {
                "source": "Reserve Bank of India - Agricultural Credit Guidelines",
                "excerpt": "Priority sector lending guidelines for agricultural credit facilities",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "geo": "National",
                "crop": "all"
            },
            {
                "source": "Banking Sector Analysis - Agricultural Finance",
                "excerpt": "Commercial banking options and interest rate analysis for agricultural enterprises",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "geo": "National", 
                "crop": "all"
            }
        ]
        
        return {
            "agent": self.name,
            "result": {"advice": advice, "urgency": "medium"},
            "evidence": evidence,
            "confidence": 0.9
        }
    
    def _analyze_provided_parameters(self, extracted_data: Dict[str, Any]) -> str:
        """Analyze the parameters provided by the user"""
        if not extracted_data:
            return "### 📋 Current Analysis\n*No specific financial parameters detected in your query.*\n\n"
        
        section = "### 📋 Current Parameters Detected\n"
        
        if 'land_size_acres' in extracted_data:
            section += f"**🏞️ Farm Size:** {extracted_data['land_size_acres']} acres\n"
        
        if 'total_annual_spend' in extracted_data:
            section += f"**💰 Total Annual Spend:** ₹{extracted_data['total_annual_spend']:,.0f}\n"
        
        for cost_type, value in extracted_data.items():
            if 'cost' in cost_type:
                section += f"**💰 {cost_type.replace('_', ' ').title()}:** ₹{value:,.0f} annually\n"
        
        if 'annual_production' in extracted_data:
            section += f"**📦 Current Production:** {extracted_data['annual_production']} quintals\n"
        
        section += "\n"
        return section
    
    def _generate_optimization_recommendations(self, extracted_data: Dict[str, Any], crop: str) -> str:
        """Generate specific optimization recommendations"""
        section = "### 🎯 Optimization Recommendations\n"
        
        # Cost reduction strategies
        if any('cost' in key for key in extracted_data.keys()):
            section += "#### 💡 Cost Reduction Strategies\n"
            
            if 'fertilizer_cost' in extracted_data:
                section += f"• **Fertilizer Optimization:** Consider soil testing to reduce over-fertilization\n"
                section += f"• **Organic Alternatives:** Integrate organic fertilizers to reduce chemical dependency\n"
            
            if 'water_cost' in extracted_data:
                section += f"• **Water Efficiency:** Implement drip irrigation to reduce water costs by 30-50%\n"
                section += f"• **Rainwater Harvesting:** Capture rainwater to reduce irrigation expenses\n"
            
            if 'labor_cost' in extracted_data:
                section += f"• **Mechanization:** Consider small machinery for repetitive tasks\n"
                section += f"• **Labor Optimization:** Plan activities to minimize peak labor requirements\n"
        
        # Yield improvement strategies
        if 'land_size_acres' in extracted_data or 'annual_production' in extracted_data:
            section += "\n#### 📈 Yield Enhancement\n"
            section += f"• **High-Yield Varieties:** Adopt improved seeds for 20-30% yield increase\n"
            section += f"• **Precision Farming:** Use technology for optimal input application\n"
            section += f"• **Intercropping:** Maximize land utilization with compatible crops\n"
        
        section += "\n"
        return section
    
    def _get_investment_priorities(self, extracted_data: Dict[str, Any], crop: str) -> str:
        """Suggest investment priorities based on current situation"""
        section = "### 💼 Investment Priorities\n"
        
        priorities = []
        
        # Determine priorities based on data
        if 'water_cost' in extracted_data and extracted_data['water_cost'] > 50000:
            priorities.append(("🚰 Drip Irrigation System", "High", "₹2-3 lakh", "30-50% water savings"))
        
        if 'fertilizer_cost' in extracted_data and extracted_data['fertilizer_cost'] > 30000:
            priorities.append(("🧪 Soil Testing & Nutrient Management", "High", "₹5,000-10,000", "20-30% fertilizer savings"))
        
        if 'land_size_acres' in extracted_data and extracted_data['land_size_acres'] > 5:
            priorities.append(("🚜 Farm Mechanization", "Medium", "₹1-5 lakh", "Reduced labor dependency"))
        
        priorities.append(("📱 Farm Management Software", "Medium", "₹10,000-25,000", "Better record keeping"))
        priorities.append(("🏪 Storage Infrastructure", "Low", "₹50,000-2 lakh", "Reduced post-harvest losses"))
        
        for priority, level, cost, benefit in priorities:
            section += f"**{priority}**\n"
            section += f"- *Priority:* {level}\n"
            section += f"- *Investment:* {cost}\n"
            section += f"- *Expected Benefit:* {benefit}\n\n"
        
        return section
    
    def _get_roi_analysis(self, extracted_data: Dict[str, Any], crop: str) -> str:
        """Provide ROI analysis and projections"""
        section = "### 📊 ROI Analysis\n"
        
        if 'land_size_acres' in extracted_data and 'annual_production' in extracted_data:
            land_size = extracted_data['land_size_acres']
            production = extracted_data['annual_production']
            if land_size > 0:
                yield_per_acre = production / land_size
                
                section += f"**Current Productivity:** {yield_per_acre:.1f} quintals/acre\n"
                
                # Benchmark against standards
                benchmarks = {"wheat": 20, "rice": 25, "cotton": 15, "sugarcane": 350}
                if crop and crop.lower() in benchmarks:
                    benchmark = benchmarks[crop.lower()]
                    if yield_per_acre < benchmark * 0.8:
                        section += f"**Improvement Potential:** Your yield is below average. Target: {benchmark} quintals/acre\n"
                        section += f"**Potential Increase:** {((benchmark - yield_per_acre) / yield_per_acre * 100):.0f}% improvement possible\n"
        
        # Calculate potential savings
        total_costs = sum(value for key, value in extracted_data.items() if 'cost' in key)
        if total_costs == 0 and 'total_annual_spend' in extracted_data:
            total_costs = extracted_data['total_annual_spend']
        if total_costs > 0:
            section += f"**Current Annual Costs:** ₹{total_costs:,.0f}\n"
            section += f"**Potential Savings (15-25%):** ₹{total_costs * 0.2:,.0f} annually\n"
        
        section += "\n"
        return section
    
    def _get_missing_info_prompt(self, extracted_data: Dict[str, Any]) -> str:
        """Suggest what additional information would help provide better advice"""
        section = "### 📝 For Better Analysis, Please Share:\n"
        
        missing = []
        required_params = ['land_size_acres', 'fertilizer_cost', 'water_cost', 'labor_cost', 'annual_production']
        
        for param in required_params:
            if param not in extracted_data:
                readable_name = param.replace('_', ' ').title()
                missing.append(readable_name)
        
        if missing:
            section += "For more personalized advice, please share:\n"
            for item in missing[:5]:  # Limit to top 5
                section += f"• {item}\n"
            
            section += f"\n💡 **Tip:** You can ask questions like: *'I have 5 acres, spend ₹30,000 on fertilizers annually, how can I optimize costs?'*\n"
        else:
            section += "✅ **Complete Analysis:** All key parameters detected for comprehensive optimization!\n"
        
        return section
    
    def _get_farm_economics_advice(self, query: str, location: str, crop: str, extracted_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Provide AI-powered farm economics analysis"""
        
        # Create comprehensive prompt for farm economics analysis
        economics_prompt = f"""
You are an expert agricultural economist. Provide comprehensive farm economics analysis and recommendations.

FARM PROFILE:
- Location: {location or 'Not specified'}
- Primary Crop: {crop or 'Not specified'}
- Query: {query}

FINANCIAL DATA:
"""
        
        if context and context.get("conversation_summary"):
            economics_prompt += f"\nCONTEXT SUMMARY:\n{context.get('conversation_summary')}\n"

        if extracted_data:
            for key, value in extracted_data.items():
                readable_key = key.replace('_', ' ').title()
                if 'cost' in key:
                    economics_prompt += f"- {readable_key}: ₹{value:,.0f} annually\n"
                elif key == 'land_size_acres':
                    economics_prompt += f"- {readable_key}: {value} acres\n"
                elif key == 'annual_production':
                    economics_prompt += f"- {readable_key}: {value} quintals\n"
        else:
            economics_prompt += "- No specific financial parameters provided\n"
        
        economics_prompt += f"""
ANALYSIS REQUIREMENTS:
1. Calculate and explain key financial metrics (ROI, profit margins, cost per unit)
2. Provide budget planning guidelines specific to the farm profile
3. Assess financial health and identify improvement areas
4. Risk analysis and mitigation strategies
5. Cash flow management recommendations
6. Benchmarking against industry standards
7. Financial planning for different scenarios (good/bad seasons)

Provide specific, actionable economic insights with quantified recommendations where possible.
Include both current financial analysis and strategic planning guidance.
Format with clear sections and bullet points for easy reading.
"""
        
        try:
            # Generate AI-powered economics analysis
            ai_economics_analysis = self.llm_client.generate_text(economics_prompt)
            main_header = f"## 📈 AI-Powered Farm Economics Analysis\n\n"
            full_advice = main_header + ai_economics_analysis
        except Exception as e:
            # Fallback to structured analysis
            main_header = f"## 📈 Farm Economics Analysis\n\n"
            
            # Basic economics principles
            economics_section = "### 💰 Financial Health Check\n"
            economics_section += "**Key Metrics to Track:**\n"
            economics_section += "• **Cost per Quintal:** Total expenses ÷ Production\n"
            economics_section += "• **Profit Margin:** (Revenue - Costs) ÷ Revenue × 100\n"
            economics_section += "• **Return on Investment:** Annual Profit ÷ Total Investment × 100\n"
            economics_section += "• **Break-even Point:** Fixed costs ÷ (Price per unit - Variable cost per unit)\n\n"
            
            # Budgeting advice
            budget_section = "### 📊 Farm Budgeting\n"
            budget_section += "**Monthly Planning:**\n"
            budget_section += "• Allocate 40-50% for inputs (seeds, fertilizers, labor)\n"
            budget_section += "• Reserve 20-30% for operational expenses\n"
            budget_section += "• Save 15-20% for equipment and infrastructure\n"
            budget_section += "• Keep 10-15% as emergency fund\n\n"
            
            # Risk management
            risk_section = "### 🛡️ Financial Risk Management\n"
            risk_section += "• **Market Risk:** Diversify crops and use forward contracts to hedge price volatility\n"
            risk_section += "• **Credit Risk:** Maintain good credit history and have backup financing options\n"
            risk_section += "• **Operational Risk:** Build emergency fund for equipment failures and unexpected costs\n"
            risk_section += "• **Liquidity Risk:** Maintain cash reserves equal to 3-6 months of operating expenses\n"
            risk_section += "• **Interest Rate Risk:** Consider fixed vs. variable rate loans based on market conditions\n"
            
            full_advice = main_header + economics_section + budget_section + risk_section
        
        evidence = [
            {
                "source": "Agricultural Economics Guidelines",
                "excerpt": "Best practices for farm financial management and budgeting",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "geo": location or "General",
                "crop": crop or "all"
            }
        ]
        
        return {
            "agent": self.name,
            "result": {"advice": full_advice, "urgency": "medium"},
            "evidence": evidence,
            "confidence": 0.8
        }
    
    def _get_general_price_advice(self) -> Dict[str, Any]:
        """Provide general price advice when specific crop data is not available"""
        advice = """## 💰 General Market Price Guidance

### 📊 Price Discovery
• **Check Multiple Sources:** Compare prices from different mandis and markets
• **Online Platforms:** Use eNAM, AgMarkNet for transparent pricing
• **Direct Marketing:** Explore farmer producer organizations (FPOs)

### ⏰ Timing Strategy
• **Harvest Timing:** Avoid immediate post-harvest sales when prices are low
• **Storage Options:** Invest in proper storage to wait for better prices
• **Market Calendar:** Learn seasonal price patterns for your crops

### 💡 Price Optimization Tips
• **Quality Grading:** Higher grade crops command premium prices
• **Value Addition:** Process crops for better margins where possible
• **Contract Farming:** Consider pre-agreed prices with buyers"""
        
        return {
            "agent": self.name,
            "result": {"advice": advice, "urgency": "medium"},
            "evidence": [],
            "confidence": 0.7
        }
    

    
    def _get_general_optimization_advice(self, query: str, location: str, crop: str, session_id: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Provide general financial optimization advice when detailed data isn't available"""
        print(f"DEBUG: _get_general_optimization_advice called with session_id = {session_id}")
        
        optimization_advice = f"""## 💰 Farm Financial Optimization Strategy

**Based on your request for optimizing spendings and improving profits, here's actionable guidance:**

### 🎯 **Immediate Cost Optimization Steps**

**1. Input Cost Analysis & Reduction:**
• **Fertilizer Optimization**: Conduct soil testing to apply exact NPK requirements (can save 15-25%)
• **Water Management**: Implement drip irrigation or precision watering (save 30-50% water costs)
• **Bulk Purchasing**: Join farmer groups for bulk buying of seeds, fertilizers (save 10-15%)
• **Seasonal Planning**: Buy inputs during off-season when prices are lower

**2. Revenue Enhancement Strategies:**
• **Quality Improvement**: Focus on produce quality to get premium prices (10-20% higher)
• **Direct Marketing**: Sell directly to consumers/retailers, bypass middlemen (increase margins by 20-30%)
• **Value Addition**: Basic processing, grading, packaging can increase profits by 25-40%
• **Market Timing**: Store produce when possible to sell during price peaks

### 📊 **Profitability Improvement Framework**

**Cost Structure Optimization:**
- Reduce input costs by 15-20% through efficient usage
- Minimize post-harvest losses (currently avg 20-25% in India)
- Optimize labor costs through mechanization where feasible

**Revenue Maximization:**
- Diversify crops to spread risk and capture different market windows
- Explore contract farming for price certainty
- Implement intercropping for additional income streams

### 💡 **Financial Management Best Practices**

**Record Keeping & Analysis:**
• Maintain detailed records of all inputs and outputs
• Calculate per-acre profitability for each crop
• Track ROI on different farming practices
• Monitor cash flow patterns

**Investment Prioritization:**
• Focus on investments with highest ROI first
• Consider rental/sharing of expensive equipment
• Invest in soil health for long-term productivity gains

### 🚀 **Next Steps for Optimization**

1. **Immediate (This Month):**
   - Start maintaining detailed financial records
   - Get soil testing done for precise fertilizer application
   - Research local market prices and timing

2. **Short-term (3-6 months):**
   - Implement one major cost-saving measure (irrigation/fertilizer optimization)
   - Explore direct marketing opportunities
   - Join or form farmer producer groups

3. **Long-term (1+ years):**
   - Consider crop diversification based on market analysis
   - Invest in value addition capabilities
   - Build financial reserves for price volatility

### 📈 **Expected Impact**
With systematic implementation, you can expect:
- **15-25% reduction in input costs**
- **20-35% increase in net profits**
- **Better cash flow management**
- **Reduced financial risks**

---

💡 **For personalized recommendations, please provide your farm size, current crops, and approximate annual spending on inputs. This will help create a specific optimization plan for your farm.**"""

        advice_text = optimization_advice
        if context and context.get("conversation_summary"):
            advice_text = f"### Context\n{context.get('conversation_summary')}\n\n" + advice_text
        return {
            "agent": "finance_agent",
            "result": {
                "advice": advice_text,
                "urgency": "medium"
            },
            "evidence": [],
            "confidence": 0.8,
            "session_id": session_id
        }
    
    def _get_general_finance_advice(self, location: str, crop: str) -> Dict[str, Any]:
        """Provide AI-powered general financial advice"""
        
        # Create comprehensive prompt for general financial guidance
        general_finance_prompt = f"""
You are an expert agricultural financial advisor. Provide comprehensive financial management guidance for a farmer.

FARM CONTEXT:
- Location: {location or 'Not specified'}
- Primary Crop: {crop or 'Not specified'}
- Scenario: General financial guidance request (no specific parameters provided)

GUIDANCE REQUIREMENTS:
1. Financial planning and record-keeping best practices
2. Budget management and cash flow optimization
3. Revenue diversification and income maximization strategies
4. Cost management and efficiency improvements
5. Banking and credit management
6. Investment planning and capital allocation
7. Risk management and financial security
8. Technology adoption for financial management
9. Market analysis and pricing strategies
10. Long-term financial sustainability

Provide practical, actionable advice that a farmer can implement immediately.
Include specific recommendations for financial tools, metrics to track, and implementation steps.
Consider regional agricultural practices and market conditions.
Format with clear sections and bullet points for easy reading.
"""
        
        try:
            # Generate AI-powered general financial advice
            ai_finance_advice = self.llm_client.generate_text(general_finance_prompt)
            main_header = f"## 💼 AI-Powered Financial Management Strategy\n\n"
            full_advice = main_header + ai_finance_advice
        except Exception as e:
            # Fallback to structured advice
            full_advice = """## 💼 Agricultural Financial Management

### 📈 Financial Planning & Analysis
• **Record Keeping:** Maintain detailed income and expense records using digital tools
• **Budget Planning:** Create annual and seasonal budgets with variance analysis
• **Cash Flow Management:** Plan for seasonal income variations and working capital needs
• **Financial Ratios:** Track key metrics like debt-to-equity, current ratio, and ROI

### 💰 Revenue Optimization & Diversification
• **Crop Portfolio:** Diversify crops to spread market and weather risks
• **Value Addition:** Process and package crops for higher profit margins
• **Direct Marketing:** Eliminate middlemen through direct sales and online platforms
• **Contract Farming:** Secure prices through forward contracts and buy-back agreements

### 🏦 Financial Services & Banking
• **Business Banking:** Separate personal and farm finances with dedicated accounts
• **Credit Management:** Build and maintain strong credit profile for better rates
• **Investment Planning:** Plan for equipment upgrades and infrastructure development
• **Risk Management:** Use financial instruments to hedge against price volatility

### 📊 Cost Management Strategies
• **Input Cost Analysis:** Regular review of fertilizer, seed, and labor expenses
• **Economies of Scale:** Group purchasing and shared equipment to reduce costs
• **Technology Investment:** ROI analysis for farm automation and precision agriculture
• **Working Capital Optimization:** Manage inventory and accounts receivable efficiently"""
        
        return {
            "agent": self.name,
            "result": {"advice": full_advice, "urgency": "low"},
            "evidence": [],
            "confidence": 0.9 if "AI-Powered" in full_advice else 0.8
        }
