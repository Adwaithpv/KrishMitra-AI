"""
LangGraph-based Supervisor for Agentic Agri Advisor
Orchestrates multiple specialized agents with intelligent routing and synthesis
"""

from typing import Dict, List, Any, TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
import json
import asyncio
import logging
import re
from datetime import datetime
from .conversation_context import conversation_manager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import existing agents
try:
    from .agents.weather_agent import WeatherAgent
    from .agents.crop_agent import CropAgent
    from .agents.finance_agent import FinanceAgent
    from .agents.policy_agent import PolicyAgent
    from .llm_client import LLMClient
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from agents.weather_agent import WeatherAgent
    from agents.crop_agent import CropAgent
    from agents.finance_agent import FinanceAgent
    from agents.policy_agent import PolicyAgent
    from llm_client import LLMClient


class AgentState(TypedDict):
    """State for the agent workflow"""
    query: str
    location: str
    crop: str
    user_context: Dict[str, Any]
    agent_decisions: List[Dict[str, Any]]
    agent_responses: List[Dict[str, Any]]
    final_answer: str
    evidence: List[Dict[str, Any]]
    confidence: float
    workflow_step: str
    error: str


class SupervisorAgent:
    """Main supervisor agent that coordinates all other agents"""
    
    def __init__(self):
        logger.info("🔧 Initializing SupervisorAgent...")
        self.agents = {
            "weather": WeatherAgent(),
            "crop": CropAgent(),
            "finance": FinanceAgent(),
            "policy": PolicyAgent()
        }
        logger.info(f"✅ Loaded {len(self.agents)} agents: {list(self.agents.keys())}")
        self.llm_client = LLMClient()
        logger.info("🔧 Building LangGraph workflow...")
        self.graph = self._build_workflow()
        logger.info("✅ SupervisorAgent initialization complete")
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        logger.info("🔧 Building LangGraph workflow...")
        
        # Create the state graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_query", self._analyze_query)
        workflow.add_node("route_to_agents", self._route_to_agents)
        workflow.add_node("execute_weather_agent", self._execute_weather_agent)
        workflow.add_node("execute_crop_agent", self._execute_crop_agent)
        workflow.add_node("execute_finance_agent", self._execute_finance_agent)
        workflow.add_node("execute_policy_agent", self._execute_policy_agent)
        workflow.add_node("synthesize_response", self._synthesize_response)
        workflow.add_node("validate_response", self._validate_response)
        
        # Define the workflow
        workflow.set_entry_point("analyze_query")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "analyze_query",
            self._should_route_to_agents,
            {
                "route": "route_to_agents",
                "direct_answer": "synthesize_response",
                "error": END
            }
        )
        
        workflow.add_conditional_edges(
            "route_to_agents",
            self._determine_agent_execution,
            {
                "weather": "execute_weather_agent",
                "crop": "execute_crop_agent", 
                "finance": "execute_finance_agent",
                "policy": "execute_policy_agent",
                "multiple": "execute_weather_agent",  # Start with weather, then others
                "synthesize": "synthesize_response"
            }
        )
        
        # Add edges from agent executions back to routing
        workflow.add_edge("execute_weather_agent", "route_to_agents")
        workflow.add_edge("execute_crop_agent", "route_to_agents")
        workflow.add_edge("execute_finance_agent", "route_to_agents")
        workflow.add_edge("execute_policy_agent", "route_to_agents")
        
        # Final synthesis and validation
        workflow.add_edge("synthesize_response", "validate_response")
        workflow.add_edge("validate_response", END)
        
        compiled_workflow = workflow.compile(checkpointer=MemorySaver())
        logger.info("✅ LangGraph workflow built and compiled successfully")
        return compiled_workflow
    
    def _analyze_query(self, state: AgentState) -> AgentState:
        """Analyze the user query using pure LLM intelligence"""
        logger.info(f"🔍 ANALYZING QUERY: '{state['query']}' | Location: {state.get('location', 'N/A')} | Crop: {state.get('crop', 'N/A')}")
        try:
            query = state["query"]
            location = state.get("location", "")
            crop = state.get("crop", "")
            
            # Use pure LLM analysis - no keywords, only intelligence
            analysis = self._llm_query_analysis(query, location, crop)
            
            # Update state with analysis
            state["user_context"] = {
                "intent": analysis.get("intent", "general"),
                "urgency": analysis.get("urgency", "medium"),
                "required_agents": analysis.get("required_agents", []),
                "needs_realtime": analysis.get("needs_realtime", False),
                "constraints": analysis.get("constraints", ""),
                "confidence": analysis.get("confidence", 0.7),
                "reasoning": analysis.get("reasoning", ""),
                "primary_goal": analysis.get("primary_goal", "")
            }
            
            state["workflow_step"] = "query_analyzed"
            logger.info(f"📊 QUERY ANALYSIS RESULT: Intent={analysis.get('intent', 'general')} | Required Agents={analysis.get('required_agents', [])} | Confidence={analysis.get('confidence', 0.7)}")
            
        except Exception as e:
            logger.error(f"❌ QUERY ANALYSIS FAILED: {str(e)}")
            state["error"] = f"Query analysis failed: {str(e)}"
            state["workflow_step"] = "error"
        
        return state
    
    def _llm_query_analysis(self, query: str, location: str, crop: str, context_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """Pure LLM-based query analysis - no keywords, only intelligent understanding"""
        
        # Prepare context section
        context_section = ""
        if context_info:
            context_section = f"""
CONVERSATION CONTEXT:
- Session: {context_info.get('session_id', 'new')}
- Previous Agent: {context_info.get('active_agent', 'none')}
- User Profile: {context_info.get('user_profile', {})}
- Summary: {context_info.get('conversation_summary', 'No previous context')}
"""
        
        analysis_prompt = f"""You are an expert agricultural advisor analyst. Analyze this farmer's query and determine the intent, urgency, and which specialized agents should handle it.

QUERY: "{query}"
LOCATION: {location or "Not specified"}
CROP: {crop or "Not specified"}
{context_section}

AVAILABLE AGENTS:
1. WEATHER AGENT - Weather forecasts, climate conditions, rainfall, drought, temperature, irrigation timing, seasonal planning
2. CROP AGENT - Crop selection, varieties, planting, cultivation, fertilizers, pest control, diseases, farming techniques, soil management
3. FINANCE AGENT - Market prices, costs, profits, loans, banking, investments, ROI calculations, financial optimization, farm economics, spending analysis
4. POLICY AGENT - Government schemes, subsidies, eligibility, applications, PM-Kisan, insurance, policies, regulatory compliance

ANALYSIS INSTRUCTIONS:
- Understand the INTENT behind the query, not just keywords
- Consider the farmer's actual need and desired outcome
- Determine urgency level: low, medium, high, urgent
- Select 1-2 most relevant agents (usually just 1)
- Focus on what the farmer really wants to achieve

RESPOND WITH EXACTLY THIS JSON FORMAT:
{{
    "intent": "financial_optimization",
    "urgency": "medium", 
    "required_agents": ["finance"],
    "needs_realtime": false,
    "constraints": "Requires farm financial data",
    "confidence": 0.9,
    "reasoning": "Farmer is seeking financial advice to optimize farm costs and improve profitability",
    "primary_goal": "Cost optimization and financial improvement"
}}"""

        try:
            logger.info("🧠 QUERYING LLM FOR INTELLIGENT QUERY ANALYSIS...")
            llm_response = self.llm_client.generate_text(analysis_prompt)
            
            # Clean and parse JSON response
            cleaned_json = self._clean_json_response(llm_response)
            analysis_result = json.loads(cleaned_json)
            
            logger.info(f"🧠 LLM ANALYSIS: Intent='{analysis_result.get('intent')}' | Agents={analysis_result.get('required_agents')} | Confidence={analysis_result.get('confidence')}")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ LLM QUERY ANALYSIS FAILED: {str(e)}")
            # Emergency fallback - route to crop agent with low confidence
            return {
                "intent": "general_agricultural",
                "urgency": "medium",
                "required_agents": ["crop"],
                "needs_realtime": False,
                "constraints": "LLM analysis unavailable",
                "confidence": 0.3,
                "reasoning": "Fallback routing due to LLM unavailability",
                "primary_goal": "General agricultural assistance"
            }
    
    def _should_route_to_agents(self, state: AgentState) -> Literal["route", "direct_answer", "error"]:
        """Determine if we should route to agents or provide direct answer"""
        if state.get("error"):
            logger.warning("⚠️ ROUTING DECISION: Error detected, ending workflow")
            return "error"
        
        context = state.get("user_context", {})
        required_agents = context.get("required_agents", [])
        
        if not required_agents:
            logger.info("🔄 ROUTING DECISION: No agents required, going to direct answer")
            return "direct_answer"
        
        logger.info(f"🔄 ROUTING DECISION: Routing to {len(required_agents)} agents: {required_agents}")
        return "route"
    
    def _route_to_agents(self, state: AgentState) -> AgentState:
        """Route the query to appropriate agents"""
        logger.info("🔄 ROUTING TO AGENTS...")
        try:
            context = state.get("user_context", {})
            required_agents = context.get("required_agents", [])
            executed_agents = [resp.get("agent") for resp in state.get("agent_responses", [])]
            
            logger.info(f"📋 AGENT STATUS: Required={required_agents} | Executed={executed_agents}")
            
            # Determine which agents still need to be executed
            # The agent responses contain 'agent' field with values like 'weather_agent', 'policy_agent'
            # We need to match against the base agent names
            executed_agent_names = []
            for resp in state.get("agent_responses", []):
                agent_name = resp.get("agent", "")
                if agent_name.endswith("_agent"):
                    executed_agent_names.append(agent_name[:-6])  # Remove '_agent' suffix
                else:
                    executed_agent_names.append(agent_name)
            
            pending_agents = [agent for agent in required_agents if agent not in executed_agent_names]
            logger.info(f"⏳ PENDING AGENTS: {pending_agents}")
            
            if not pending_agents:
                # All agents have been executed, move to synthesis
                logger.info("✅ ALL AGENTS EXECUTED: Moving to synthesis")
                state["workflow_step"] = "all_agents_executed"
                return state
            
            # Decide which agent to execute next
            if "weather" in pending_agents:
                logger.info("🌤️ NEXT AGENT: Weather agent")
                state["workflow_step"] = "executing_weather"
                return state
            elif "crop" in pending_agents:
                logger.info("🌱 NEXT AGENT: Crop agent")
                state["workflow_step"] = "executing_crop"
                return state
            elif "finance" in pending_agents:
                logger.info("💰 NEXT AGENT: Finance agent")
                state["workflow_step"] = "executing_finance"
                return state
            elif "policy" in pending_agents:
                logger.info("📋 NEXT AGENT: Policy agent")
                state["workflow_step"] = "executing_policy"
                return state
            else:
                logger.info("🔄 NEXT STEP: Moving to synthesis")
                state["workflow_step"] = "synthesizing"
                return state
                
        except Exception as e:
            logger.error(f"❌ AGENT ROUTING FAILED: {str(e)}")
            state["error"] = f"Agent routing failed: {str(e)}"
            state["workflow_step"] = "error"
        
        return state
    
    def _determine_agent_execution(self, state: AgentState) -> Literal["weather", "crop", "finance", "policy", "multiple", "synthesize"]:
        """Determine which agent to execute next"""
        workflow_step = state.get("workflow_step", "")
        logger.info(f"🎯 DETERMINING EXECUTION: Current step = '{workflow_step}'")
        
        if workflow_step == "executing_weather":
            logger.info("🌤️ EXECUTION DECISION: Weather agent")
            return "weather"
        elif workflow_step == "executing_crop":
            logger.info("🌱 EXECUTION DECISION: Crop agent")
            return "crop"
        elif workflow_step == "executing_finance":
            logger.info("💰 EXECUTION DECISION: Finance agent")
            return "finance"
        elif workflow_step == "executing_policy":
            logger.info("📋 EXECUTION DECISION: Policy agent")
            return "policy"
        elif workflow_step == "all_agents_executed":
            logger.info("🔄 EXECUTION DECISION: Synthesize responses")
            return "synthesize"
        else:
            logger.info("🔄 EXECUTION DECISION: Default to synthesize")
            return "synthesize"
    
    def _execute_weather_agent(self, state: AgentState) -> AgentState:
        """Execute the weather agent"""
        logger.info("🌤️ EXECUTING WEATHER AGENT...")
        try:
            logger.info(f"🌤️ Weather Agent Input: Query='{state['query']}' | Location='{state.get('location', 'N/A')}' | Crop='{state.get('crop', 'N/A')}'")
            
            response = self.agents["weather"].process_query(
                state["query"], 
                state.get("location"), 
                state.get("crop")
            )
            
            logger.info(f"🌤️ Weather Agent Response: {response.get('answer', 'No answer')[:100]}... | Confidence: {response.get('confidence', 0.0)}")
            
            agent_responses = state.get("agent_responses", [])
            agent_responses.append(response)
            state["agent_responses"] = agent_responses
            
            state["workflow_step"] = "weather_executed"
            logger.info("✅ Weather agent execution completed")
            
        except Exception as e:
            logger.error(f"❌ WEATHER AGENT FAILED: {str(e)}")
            state["error"] = f"Weather agent failed: {str(e)}"
            state["workflow_step"] = "error"
        
        return state
    
    def _execute_crop_agent(self, state: AgentState) -> AgentState:
        """Execute the crop agent"""
        logger.info("🌱 EXECUTING CROP AGENT...")
        try:
            logger.info(f"🌱 Crop Agent Input: Query='{state['query']}' | Location='{state.get('location', 'N/A')}' | Crop='{state.get('crop', 'N/A')}'")
            
            response = self.agents["crop"].process_query(
                state["query"], 
                state.get("location"), 
                state.get("crop")
            )
            
            logger.info(f"🌱 Crop Agent Response: {response.get('answer', 'No answer')[:100]}... | Confidence: {response.get('confidence', 0.0)}")
            
            agent_responses = state.get("agent_responses", [])
            agent_responses.append(response)
            state["agent_responses"] = agent_responses
            
            state["workflow_step"] = "crop_executed"
            logger.info("✅ Crop agent execution completed")
            
        except Exception as e:
            logger.error(f"❌ CROP AGENT FAILED: {str(e)}")
            state["error"] = f"Crop agent failed: {str(e)}"
            state["workflow_step"] = "error"
        
        return state
    
    def _execute_finance_agent(self, state: AgentState) -> AgentState:
        """Execute the finance agent"""
        logger.info("💰 EXECUTING FINANCE AGENT...")
        try:
            logger.info(f"💰 Finance Agent Input: Query='{state['query']}' | Location='{state.get('location', 'N/A')}' | Crop='{state.get('crop', 'N/A')}'")
            
            response = self.agents["finance"].process_query(
                state["query"], 
                state.get("location"), 
                state.get("crop")
            )
            
            logger.info(f"💰 Finance Agent Response: {response.get('answer', 'No answer')[:100]}... | Confidence: {response.get('confidence', 0.0)}")
            
            agent_responses = state.get("agent_responses", [])
            agent_responses.append(response)
            state["agent_responses"] = agent_responses
            
            state["workflow_step"] = "finance_executed"
            logger.info("✅ Finance agent execution completed")
            
        except Exception as e:
            logger.error(f"❌ FINANCE AGENT FAILED: {str(e)}")
            state["error"] = f"Finance agent failed: {str(e)}"
            state["workflow_step"] = "error"
        
        return state
    
    def _execute_policy_agent(self, state: AgentState) -> AgentState:
        """Execute the policy agent"""
        logger.info("📋 EXECUTING POLICY AGENT...")
        try:
            logger.info(f"📋 Policy Agent Input: Query='{state['query']}' | Location='{state.get('location', 'N/A')}' | Crop='{state.get('crop', 'N/A')}'")
            
            response = self.agents["policy"].process_query(
                state["query"], 
                state.get("location"), 
                state.get("crop")
            )
            
            logger.info(f"📋 Policy Agent Response: {response.get('answer', 'No answer')[:100]}... | Confidence: {response.get('confidence', 0.0)}")
            
            agent_responses = state.get("agent_responses", [])
            agent_responses.append(response)
            state["agent_responses"] = agent_responses
            
            state["workflow_step"] = "policy_executed"
            logger.info("✅ Policy agent execution completed")
            
        except Exception as e:
            logger.error(f"❌ POLICY AGENT FAILED: {str(e)}")
            state["error"] = f"Policy agent failed: {str(e)}"
            state["workflow_step"] = "error"
        
        return state
    
    def _synthesize_response(self, state: AgentState) -> AgentState:
        """Synthesize responses from all agents into a coherent answer"""
        logger.info("🔄 SYNTHESIZING RESPONSES...")
        try:
            agent_responses = state.get("agent_responses", [])
            context = state.get("user_context", {})
            logger.info(f"📊 SYNTHESIS INPUT: {len(agent_responses)} agent responses | Context: {context.get('intent', 'unknown')}")
            
            if not agent_responses:
                # No agent responses, generate a general answer
                logger.info("⚠️ NO AGENT RESPONSES: Generating general answer")
                synthesis_prompt = f"""
                The user asked: {state['query']}
                Location: {state.get('location', 'Not specified')}
                Crop: {state.get('crop', 'Not specified')}
                
                No specific agent responses were available. Provide a helpful, general agricultural advice response.
                """
                
                final_answer = self.llm_client.generate_text(synthesis_prompt)
                confidence = 0.3
                evidence = []
                
            else:
                # Synthesize multiple agent responses
                logger.info(f"🔄 SYNTHESIZING {len(agent_responses)} AGENT RESPONSES...")
                
                # For single agent responses, try to use the agent's direct response first
                if len(agent_responses) == 1:
                    single_response = agent_responses[0]
                    # Try to get the answer from various response formats
                    agent_answer = (
                        single_response.get('answer') or 
                        single_response.get('result', {}).get('advice') or
                        single_response.get('response') or
                        ""
                    )
                    
                    if agent_answer and agent_answer != "No answer":
                        # Use the agent's direct response if it's good
                        final_answer = agent_answer
                        logger.info("✅ USING DIRECT AGENT RESPONSE")
                    else:
                        # Fall back to LLM synthesis
                        synthesis_prompt = f"""
                        Based on the agent response, provide a helpful answer to: {state['query']}
                        
                        Agent Response: {json.dumps(single_response, indent=2)}
                        Location: {state.get('location', 'Not specified')}
                        Crop: {state.get('crop', 'Not specified')}
                        """
                        final_answer = self.llm_client.generate_text(synthesis_prompt)
                else:
                    # Multiple agent responses - need LLM synthesis
                    synthesis_prompt = f"""
                    Synthesize the following agent responses into a coherent, helpful answer:
                    
                    Original Query: {state['query']}
                    Location: {state.get('location', 'Not specified')}
                    Crop: {state.get('crop', 'Not specified')}
                    
                    Agent Responses:
                    {json.dumps(agent_responses, indent=2)}
                    
                    Create a comprehensive answer that:
                    1. Addresses the user's query directly
                    2. Combines insights from all relevant agents
                    3. Prioritizes the most relevant information
                    4. Provides actionable advice
                    5. Maintains a natural, conversational tone
                    
                    Format the response as a clear, structured answer.
                    """
                    
                    final_answer = self.llm_client.generate_text(synthesis_prompt)
                
                # Calculate confidence based on agent responses
                confidences = [resp.get("confidence", 0.0) for resp in agent_responses]
                confidence = sum(confidences) / len(confidences) if confidences else 0.5
                
                # Collect all evidence
                evidence = []
                for resp in agent_responses:
                    evidence.extend(resp.get("evidence", []))
            
            state["final_answer"] = final_answer
            state["confidence"] = round(confidence, 3)
            state["evidence"] = evidence
            state["workflow_step"] = "synthesized"
            logger.info(f"✅ SYNTHESIS COMPLETE: Confidence={confidence} | Evidence count={len(evidence)}")
            
        except Exception as e:
            logger.error(f"❌ RESPONSE SYNTHESIS FAILED: {str(e)}")
            state["error"] = f"Response synthesis failed: {str(e)}"
            state["workflow_step"] = "error"
        
        return state
    
    def _validate_response(self, state: AgentState) -> AgentState:
        """Validate the final response for quality and safety"""
        logger.info("🔍 VALIDATING RESPONSE...")
        try:
            final_answer = state.get("final_answer", "")
            confidence = state.get("confidence", 0.0)
            logger.info(f"🔍 VALIDATION INPUT: Answer length={len(final_answer)} | Confidence={confidence}")
            
            # Basic validation checks
            validation_prompt = f"""
            Validate this agricultural advice response:
            
            Query: {state['query']}
            Answer: {final_answer}
            Confidence: {confidence}
            
            Check for:
            1. Relevance to the query
            2. Safety of recommendations
            3. Completeness of information
            4. Appropriate confidence level
            
            Respond with JSON:
            {{
                "is_valid": true/false,
                "issues": ["list of issues if any"],
                "suggested_improvements": ["list of improvements"],
                "final_confidence": 0.0-1.0
            }}
            """
            
            validation_response = self.llm_client.generate_text(validation_prompt)
            
            try:
                validation = json.loads(validation_response)
            except json.JSONDecodeError:
                # Fallback validation
                validation = {
                    "is_valid": True,
                    "issues": [],
                    "suggested_improvements": [],
                    "final_confidence": confidence
                }
            
            # Apply validation results
            if not validation.get("is_valid", True):
                # If invalid, try to improve the response
                improvement_prompt = f"""
                Improve this agricultural advice response:
                
                Original Query: {state['query']}
                Current Answer: {final_answer}
                Issues: {validation.get('issues', [])}
                
                Provide an improved, safer, and more relevant response.
                """
                
                improved_answer = self.llm_client.generate_text(improvement_prompt)
                state["final_answer"] = improved_answer
            
            # Update confidence based on validation
            state["confidence"] = validation.get("final_confidence", confidence)
            state["workflow_step"] = "validated"
            logger.info(f"✅ VALIDATION COMPLETE: Final confidence={state['confidence']} | Valid={validation.get('is_valid', True)}")
            
        except Exception as e:
            logger.error(f"❌ RESPONSE VALIDATION FAILED: {str(e)}")
            state["error"] = f"Response validation failed: {str(e)}"
            state["workflow_step"] = "error"
        
        return state
    
    def _clean_json_response(self, response: str) -> str:
        """Clean and extract JSON from LLM response"""
        # Remove common prefixes/suffixes that LLMs add
        response = response.strip()
        
        # Remove markdown code blocks
        if response.startswith('```json'):
            response = response[7:]
        if response.startswith('```'):
            response = response[3:]
        if response.endswith('```'):
            response = response[:-3]
        
        # Find JSON boundaries
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        
        if json_start != -1 and json_end > json_start:
            return response[json_start:json_end].strip()
        
        return response.strip()
    
    def _llm_based_agent_selection(self, query: str, location: str = None, crop: str = None) -> tuple[str, Dict[str, Any]]:
        """Use LLM to intelligently select and execute the best agent"""
        try:
            # Create a comprehensive prompt for agent selection
            agent_selection_prompt = f"""You are an intelligent agricultural advisor router. Analyze this query and determine which specialized agent should handle it.

QUERY: "{query}"
LOCATION: {location or "Not specified"}
CROP: {crop or "Not specified"}

AVAILABLE AGENTS:
1. WEATHER AGENT - Handles weather forecasts, climate conditions, rainfall, drought, temperature, irrigation timing based on weather
2. CROP AGENT - Handles crop selection, varieties, planting, cultivation, fertilizers, pest control, diseases, farming techniques
3. FINANCE AGENT - Handles market prices, costs, profits, loans, banking, investments, ROI calculations
4. POLICY AGENT - Handles government schemes, subsidies, eligibility, applications, PM-Kisan, insurance, policies

INSTRUCTIONS:
- Analyze the query and select the MOST appropriate agent
- Choose only ONE agent: weather, crop, finance, or policy
- Respond with ONLY valid JSON, no additional text

RESPOND WITH EXACTLY THIS JSON FORMAT:
{{
    "selected_agent": "crop",
    "reasoning": "Query is about crop selection which requires agricultural expertise",
    "confidence": 0.9,
    "query_type": "crop_selection",
    "priority_info": "Regional crop varieties and suitability"
}}"""
            
            logger.info("🤖 QUERYING LLM FOR AGENT SELECTION...")
            llm_response = self.llm_client.generate_text(agent_selection_prompt)
            
            logger.info(f"🔍 RAW LLM RESPONSE: {llm_response[:200]}...")  # Log first 200 chars for debugging
            
            try:
                # Clean the JSON response
                cleaned_json = self._clean_json_response(llm_response)
                logger.info(f"🔍 CLEANED JSON: {cleaned_json}")
                
                selection_result = json.loads(cleaned_json)
                
                selected_agent = selection_result.get("selected_agent", "crop")
                reasoning = selection_result.get("reasoning", "LLM selection")
                confidence = selection_result.get("confidence", 0.8)
                
                logger.info(f"🤖 LLM SELECTION: {selected_agent} | Reasoning: {reasoning} | Confidence: {confidence}")
                
                # Execute the selected agent
                if selected_agent == "weather":
                    response = self.agents["weather"].process_query(query, location, crop)
                    agent_name = "weather_agent"
                elif selected_agent == "finance":
                    response = self.agents["finance"].process_query(query, location, crop)
                    agent_name = "finance_agent"
                elif selected_agent == "policy":
                    response = self.agents["policy"].process_query(query, location, crop)
                    agent_name = "policy_agent"
                else:  # Default to crop agent
                    response = self.agents["crop"].process_query(query, location, crop)
                    agent_name = "crop_agent"
                
                # Add LLM routing metadata to response
                if isinstance(response, dict):
                    response["llm_routing"] = {
                        "reasoning": reasoning,
                        "confidence": confidence,
                        "query_type": selection_result.get("query_type", "agricultural")
                    }
                
                return agent_name, response
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"⚠️ LLM response JSON parsing failed: {str(e)}")
                logger.warning(f"⚠️ Raw response: {llm_response}")
                return None, None
                
        except Exception as e:
            logger.error(f"❌ LLM AGENT SELECTION FAILED: {str(e)}")
            return None, None
    
    def _pure_llm_agent_selection(self, query: str, location: str = None, crop: str = None, session_id: str = None) -> tuple[str, Dict[str, Any]]:
        """Pure LLM-based agent selection - no keywords, only intelligent understanding"""
        logger.info("🧠 USING PURE LLM AGENT SELECTION")
        
        # Get conversation context for better routing
        context_info = conversation_manager.get_context_for_routing(session_id) if session_id else {}
        
        # Use LLM to analyze and select the best agent
        analysis = self._llm_query_analysis(query, location, crop, context_info)
        required_agents = analysis.get("required_agents", ["crop"])
        reasoning = analysis.get("reasoning", "LLM intelligent selection")
        
        logger.info(f"🧠 LLM REASONING: {reasoning}")
        
        # Select the first (most relevant) agent based on LLM analysis
        selected_agent = required_agents[0] if required_agents else "crop"
        
        # Execute the selected agent with session awareness
        if selected_agent == "weather":
            response = self.agents["weather"].process_query(query, location, crop)
            agent_name = "weather_agent"
        elif selected_agent == "finance":
            # Pass session_id to finance agent for session management
            if hasattr(self.agents["finance"], 'process_query'):
                import inspect
                sig = inspect.signature(self.agents["finance"].process_query)
                if 'session_id' in sig.parameters:
                    response = self.agents["finance"].process_query(query, location, crop, session_id)
                else:
                    response = self.agents["finance"].process_query(query, location, crop)
            else:
                response = self.agents["finance"].process_query(query, location, crop)
            agent_name = "finance_agent"
        elif selected_agent == "policy":
            response = self.agents["policy"].process_query(query, location, crop)
            agent_name = "policy_agent"
        else:  # Default to crop
            response = self.agents["crop"].process_query(query, location, crop)
            agent_name = "crop_agent"
        
        # Add LLM routing metadata
        if isinstance(response, dict):
            response["llm_routing"] = {
                "reasoning": reasoning,
                "confidence": analysis.get("confidence", 0.8),
                "intent": analysis.get("intent", "general"),
                "primary_goal": analysis.get("primary_goal", "Agricultural assistance"),
                "session_id": session_id
            }
        
        logger.info(f"🧠 LLM SELECTION: {agent_name} | Reasoning: {reasoning[:50]}...")
        return agent_name, response
    
    def _route_to_active_agent(self, active_agent: str, query: str, location: str = None, crop: str = None, session_id: str = None) -> tuple[str, Dict[str, Any]]:
        """Route query directly to the active agent in conversation"""
        logger.info(f"🎯 ROUTING TO ACTIVE AGENT: {active_agent}")
        
        try:
            # Extract base agent name (remove _agent suffix if present)
            agent_key = active_agent.replace("_agent", "") if active_agent.endswith("_agent") else active_agent
            
            if agent_key in self.agents:
                # For finance agent, pass session_id to maintain session state
                if agent_key == "finance" and hasattr(self.agents[agent_key], 'process_query'):
                    # Check if process_query accepts session_id parameter
                    import inspect
                    sig = inspect.signature(self.agents[agent_key].process_query)
                    if 'session_id' in sig.parameters:
                        response = self.agents[agent_key].process_query(query, location, crop, session_id)
                    else:
                        response = self.agents[agent_key].process_query(query, location, crop)
                else:
                    response = self.agents[agent_key].process_query(query, location, crop)
                
                agent_name = f"{agent_key}_agent"
                return agent_name, response
            else:
                logger.error(f"❌ Unknown agent: {agent_key}")
                return self._pure_llm_agent_selection(query, location, crop, session_id)
                
        except Exception as e:
            logger.error(f"❌ ACTIVE AGENT ROUTING FAILED: {str(e)}")
            return self._pure_llm_agent_selection(query, location, crop, session_id)
    
    def _response_has_followup_questions(self, response: Dict[str, Any]) -> bool:
        """Check if agent response contains follow-up questions"""
        answer = response.get("result", {}).get("advice", "")
        if not answer:
            answer = response.get("answer", "")
        
        # Look for question indicators
        question_indicators = [
            "please share", "please provide", "need more", "can you tell",
            "what is your", "how much", "how many", "which type",
            "📊 Please share", "information:", "details:", "form_data"
        ]
        
        # Also check for form data (finance agent forms)
        has_form = "form_data" in response.get("result", {})
        
        return has_form or any(indicator in answer.lower() for indicator in question_indicators)
    
    def _llm_based_agent_selection(self, query: str, location: str = None, crop: str = None, session_id: str = None) -> tuple[str, Dict[str, Any]]:
        """Enhanced LLM-based agent selection with conversation context"""
        try:
            # Get conversation context for better routing
            context_info = conversation_manager.get_context_for_routing(session_id) if session_id else {}
            
            # Create enhanced prompt with conversation context
            context_section = ""
            if context_info:
                context_section = f"""
CONVERSATION CONTEXT:
- Session: {context_info.get('session_id', 'new')}
- Previous Agent: {context_info.get('active_agent', 'none')}
- User Profile: {context_info.get('user_profile', {})}
- Summary: {context_info.get('conversation_summary', 'No previous context')}
"""
            
            agent_selection_prompt = f"""You are an intelligent agricultural advisor router. Analyze this query and determine which specialized agent should handle it.

QUERY: "{query}"
LOCATION: {location or "Not specified"}
CROP: {crop or "Not specified"}
{context_section}

AVAILABLE AGENTS:
1. WEATHER AGENT - Handles weather forecasts, climate conditions, rainfall, drought, temperature, irrigation timing based on weather
2. CROP AGENT - Handles crop selection, varieties, planting, cultivation, fertilizers, pest control, diseases, farming techniques  
3. FINANCE AGENT - Handles market prices, costs, profits, loans, banking, investments, ROI calculations, financial optimization, cost analysis, spending optimization, farm economics
4. POLICY AGENT - Handles government schemes, subsidies, eligibility, applications, PM-Kisan, insurance, policies

CRITICAL ROUTING RULES:
- If query contains financial amounts, spending data, costs, or asks for financial optimization → FINANCE AGENT
- If user provides farm size + costs/spending/expenses → FINANCE AGENT (they want cost optimization)
- If query mentions "spend", "cost", "expense", "optimize", "profit", "investment" → FINANCE AGENT
- If query asks "how much", "what is cost", "reduce cost", "save money" → FINANCE AGENT
- Only route to CROP AGENT for pure agricultural techniques without financial focus

EXAMPLES:
- "My farm is 5 acres, I spend ₹30,000 on fertilizers" → FINANCE (contains spending data)
- "How can I reduce my farming costs?" → FINANCE (cost optimization)
- "What fertilizer should I use for wheat?" → CROP (technical farming)
- "Which crop is suitable for my region?" → CROP (technical farming)

INSTRUCTIONS:
- Analyze the query and select the MOST appropriate agent
- Consider conversation context if available  
- Prioritize FINANCE AGENT when financial data or optimization is mentioned
- Choose only ONE agent: weather, crop, finance, or policy
- Respond with ONLY valid JSON, no additional text

RESPOND WITH EXACTLY THIS JSON FORMAT:
{{
    "selected_agent": "finance",
    "reasoning": "Query contains financial data and spending information requiring cost optimization analysis",
    "confidence": 0.9,
    "query_type": "financial_optimization",
    "priority_info": "Farm cost analysis and optimization"
}}"""
            
            logger.info("🤖 QUERYING LLM FOR CONTEXT-AWARE AGENT SELECTION...")
            llm_response = self.llm_client.generate_text(agent_selection_prompt)
            
            logger.info(f"🔍 RAW LLM RESPONSE: {llm_response[:200]}...")
            
            try:
                cleaned_json = self._clean_json_response(llm_response)
                logger.info(f"🔍 CLEANED JSON: {cleaned_json}")
                
                selection_result = json.loads(cleaned_json)
                
                selected_agent = selection_result.get("selected_agent", "crop")
                reasoning = selection_result.get("reasoning", "LLM selection")
                confidence = selection_result.get("confidence", 0.8)
                
                logger.info(f"🤖 LLM SELECTION: {selected_agent} | Reasoning: {reasoning} | Confidence: {confidence}")
                
                # Execute the selected agent with session awareness
                return self._execute_selected_agent(selected_agent, query, location, crop, session_id, selection_result)
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"⚠️ LLM response JSON parsing failed: {str(e)}")
                logger.warning(f"⚠️ Raw response: {llm_response}")
                return None, None
                
        except Exception as e:
            logger.error(f"❌ LLM AGENT SELECTION FAILED: {str(e)}")
            return None, None
    
    def _execute_selected_agent(self, selected_agent: str, query: str, location: str, crop: str, session_id: str, selection_result: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
        """Execute the selected agent with session awareness"""
        reasoning = selection_result.get("reasoning", "LLM selection")
        confidence = selection_result.get("confidence", 0.8)
        
        # Execute the selected agent
        if selected_agent == "weather":
            response = self.agents["weather"].process_query(query, location, crop)
            agent_name = "weather_agent"
        elif selected_agent == "finance":
            # Pass session_id to finance agent for session management
            if hasattr(self.agents["finance"], 'process_query'):
                import inspect
                sig = inspect.signature(self.agents["finance"].process_query)
                if 'session_id' in sig.parameters:
                    response = self.agents["finance"].process_query(query, location, crop, session_id)
                else:
                    response = self.agents["finance"].process_query(query, location, crop)
            else:
                response = self.agents["finance"].process_query(query, location, crop)
            agent_name = "finance_agent"
        elif selected_agent == "policy":
            response = self.agents["policy"].process_query(query, location, crop)
            agent_name = "policy_agent"
        else:  # Default to crop agent
            response = self.agents["crop"].process_query(query, location, crop)
            agent_name = "crop_agent"
        
        # Add LLM routing metadata to response
        if isinstance(response, dict):
            response["llm_routing"] = {
                "reasoning": reasoning,
                "confidence": confidence,
                "query_type": selection_result.get("query_type", "agricultural"),
                "session_id": session_id
            }
        
        return agent_name, response
    

    
    async def process_query_async(self, query: str, location: str = None, crop: str = None, session_id: str = None) -> Dict[str, Any]:
        """Process a query through the supervisor workflow"""
        logger.info(f"🚀 STARTING SUPERVISOR WORKFLOW: Query='{query}' | Location='{location or 'N/A'}' | Crop='{crop or 'N/A'}'")
        try:
            # Initialize state
            initial_state = AgentState(
                query=query,
                location=location or "",
                crop=crop or "",
                user_context={},
                agent_decisions=[],
                agent_responses=[],
                final_answer="",
                evidence=[],
                confidence=0.0,
                workflow_step="started",
                error=""
            )
            
            # Execute the workflow
            config = {"configurable": {"thread_id": f"query_{datetime.now().timestamp()}"}}
            logger.info("🔄 EXECUTING LANGRAPH WORKFLOW...")
            result = await self.graph.ainvoke(initial_state, config)
            logger.info("✅ LANGRAPH WORKFLOW COMPLETED")
            
            # Extract final result
            if result.get("error"):
                logger.error(f"❌ WORKFLOW ERROR: {result['error']}")
                return {
                    "answer": f"I encountered an error processing your query: {result['error']}",
                    "evidence": [],
                    "confidence": 0.0,
                    "agents_consulted": [],
                    "agent_used": "supervisor",
                    "workflow_trace": result.get("workflow_step", "unknown")
                }
            
            final_result = {
                "answer": result.get("final_answer", "No answer generated"),
                "evidence": result.get("evidence", []),
                "confidence": result.get("confidence", 0.0),
                "agents_consulted": [resp.get("agent") for resp in result.get("agent_responses", [])],
                "agent_used": "supervisor",
                "workflow_trace": result.get("workflow_step", "completed"),
                "session_id": session_id if 'session_id' in locals() else None,
                "conversation_context": conversation_manager.get_context_for_routing(session_id) if 'session_id' in locals() and session_id else None
            }
            logger.info(f"🎉 SUPERVISOR WORKFLOW SUCCESS: Agents consulted={final_result['agents_consulted']} | Confidence={final_result['confidence']} | Workflow trace={final_result['workflow_trace']}")
            return final_result
            
        except Exception as e:
            logger.error(f"❌ SUPERVISOR WORKFLOW FAILED: {str(e)}")
            return {
                "answer": f"I encountered an error: {str(e)}",
                "evidence": [],
                "confidence": 0.0,
                "agents_consulted": [],
                "agent_used": "supervisor",
                "workflow_trace": "error"
            }
    
    def process_query(self, query: str, location: str = None, crop: str = None, session_id: str = None) -> Dict[str, Any]:
        """Synchronous wrapper for async processing with conversation context"""
        logger.info(f"🔄 SYNC PROCESS QUERY CALLED: Query='{query}' | Session='{session_id or 'new'}'")
        try:
            # Always use conversation-aware sync execution when session_id is provided
            if session_id:
                logger.info("🔄 SESSION PROVIDED: Using conversation-aware sync execution")
                return self._process_query_sync(query, location, crop, session_id)
            
            # Check if we're already in an event loop for non-session queries
            try:
                loop = asyncio.get_running_loop()
                # We're in an async context, so we need to handle this differently
                logger.info("🔄 DETECTED RUNNING EVENT LOOP: Using sync execution")
                return self._process_query_sync(query, location, crop, session_id)
            except RuntimeError:
                # No running loop, safe to use asyncio.run()
                logger.info("🔄 NO RUNNING EVENT LOOP: Using async execution")
                return asyncio.run(self.process_query_async(query, location, crop, session_id))
        except Exception as e:
            logger.error(f"❌ SYNC PROCESS QUERY FAILED: {str(e)}")
            return {
                "answer": f"I encountered an error: {str(e)}",
                "evidence": [],
                "confidence": 0.0,
                "agents_consulted": [],
                "agent_used": "supervisor",
                "workflow_trace": "error"
            }
    
    def _process_query_sync(self, query: str, location: str = None, crop: str = None, session_id: str = None) -> Dict[str, Any]:
        """Synchronous version with conversation-aware routing"""
        logger.info(f"🔄 SYNC EXECUTION with CONVERSATION CONTEXT: Query='{query}' | Location='{location or 'N/A'}' | Crop='{crop or 'N/A'}' | Session='{session_id or 'new'}'")
        
        try:
            # Get or create conversation context
            if not session_id:
                session_id = f"session_{datetime.now().timestamp()}"
            
            context = conversation_manager.get_or_create_context(session_id)
            
            # Check if this is a response to an active agent conversation
            is_response_to_agent, active_agent = conversation_manager.should_route_to_active_agent(session_id, query)
            
            if is_response_to_agent and active_agent:
                logger.info(f"💬 CONTINUING CONVERSATION with {active_agent}")
                # Route directly to the active agent without re-analysis
                agent_name, response = self._route_to_active_agent(active_agent, query, location, crop, session_id)
            else:
                logger.info(f"🧠 NEW CONVERSATION: Using pure LLM intelligent routing")
                # Use pure LLM for intelligent agent selection - no keywords
                agent_name, response = self._pure_llm_agent_selection(query, location, crop, session_id)
            
            # Update conversation context
            is_followup_question = self._response_has_followup_questions(response)
            conversation_manager.update_context(session_id, query, agent_name, response, is_followup_question)
            
            # Extract answer from various response formats
            answer = (
                response.get('answer') or 
                response.get('result', {}).get('advice') or
                "I'm sorry, I couldn't generate a specific answer for your query."
            )
            
            final_result = {
                "answer": answer,
                "evidence": response.get("evidence", []),
                "confidence": response.get("confidence", 0.7),
                "agents_consulted": [agent_name],
                "agent_used": "supervisor_sync",
                "workflow_trace": "sync_execution",
                "session_id": session_id,
                "conversation_context": conversation_manager.get_context_for_routing(session_id) if session_id else None
            }
            
            logger.info(f"✅ SYNC EXECUTION SUCCESS: Agent={agent_name} | Session={session_id} | Confidence={final_result['confidence']}")
            return final_result
            
        except Exception as e:
            logger.error(f"❌ SYNC EXECUTION FAILED: {str(e)}")
            return {
                "answer": f"I encountered an error: {str(e)}",
                "evidence": [],
                "confidence": 0.0,
                "agents_consulted": [],
                "agent_used": "supervisor_sync",
                "workflow_trace": "sync_error"
            }
