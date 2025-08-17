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
from datetime import datetime

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
        """Analyze the user query to understand intent and context"""
        logger.info(f"🔍 ANALYZING QUERY: '{state['query']}' | Location: {state.get('location', 'N/A')} | Crop: {state.get('crop', 'N/A')}")
        try:
            query = state["query"]
            location = state.get("location", "")
            crop = state.get("crop", "")
            
            # Use LLM to analyze query intent
            analysis_prompt = f"""
            Analyze this agricultural query and determine the best approach:
            
            Query: {query}
            Location: {location}
            Crop: {crop}
            
            Determine:
            1. Primary intent (weather, crop_management, finance, policy, or general)
            2. Urgency level (low, medium, high)
            3. Required agents (weather, crop, finance, policy)
            4. Whether this needs real-time data or can use static knowledge
            5. Any specific constraints or preferences
            
            Respond in JSON format:
            {{
                "intent": "weather|crop_management|finance|policy|general",
                "urgency": "low|medium|high", 
                "required_agents": ["weather", "crop", "finance", "policy"],
                "needs_realtime": true/false,
                "constraints": "any specific constraints",
                "confidence": 0.0-1.0
            }}
            """
            
            # Get LLM analysis using text generation
            analysis_response = self.llm_client.generate_text(analysis_prompt)
            
            try:
                analysis = json.loads(analysis_response)
            except json.JSONDecodeError:
                # Fallback analysis
                analysis = self._fallback_query_analysis(query, location, crop)
            
            # Update state with analysis
            state["user_context"] = {
                "intent": analysis.get("intent", "general"),
                "urgency": analysis.get("urgency", "medium"),
                "required_agents": analysis.get("required_agents", []),
                "needs_realtime": analysis.get("needs_realtime", False),
                "constraints": analysis.get("constraints", ""),
                "confidence": analysis.get("confidence", 0.7)
            }
            
            state["workflow_step"] = "query_analyzed"
            logger.info(f"📊 QUERY ANALYSIS RESULT: Intent={analysis.get('intent', 'general')} | Required Agents={analysis.get('required_agents', [])} | Confidence={analysis.get('confidence', 0.7)}")
            
        except Exception as e:
            logger.error(f"❌ QUERY ANALYSIS FAILED: {str(e)}")
            state["error"] = f"Query analysis failed: {str(e)}"
            state["workflow_step"] = "error"
        
        return state
    
    def _fallback_query_analysis(self, query: str, location: str, crop: str) -> Dict[str, Any]:
        """Fallback analysis when LLM is not available"""
        query_lower = query.lower()
        
        # Simple keyword-based analysis
        intent = "general"
        required_agents = []
        
        # Weather-related
        weather_keywords = ["weather", "rain", "rainfall", "drought", "temperature", "heat", "cold", "storm", "forecast", "alert", "irrigation", "water"]
        if any(keyword in query_lower for keyword in weather_keywords):
            intent = "weather"
            required_agents.append("weather")
        
        # Crop-related
        crop_keywords = ["fertilizer", "npk", "pest", "disease", "plant", "sow", "transplant", "spacing", "growth"]
        if any(keyword in query_lower for keyword in crop_keywords):
            intent = "crop_management"
            required_agents.append("crop")
        
        # Finance-related
        finance_keywords = ["price", "market", "mandi", "rate", "cost", "loan", "credit", "bank", "finance", "money", "investment", "profit"]
        if any(keyword in query_lower for keyword in finance_keywords):
            intent = "finance"
            required_agents.append("finance")
        
        # Policy-related (includes subsidies which are government schemes)
        policy_keywords = [
            "scheme", "schemes", "policy", "policies", "government", "benefit", "benefits",
            "subsidy", "subsidies", "allowance", "grant", "grants",
            "pm kisan", "pm-kisan", "pmkisan", "pradhan mantri", "pradhanmantri", 
            "pm kissan", "pm-kissan", "centrail pm", "central pm",
            "nabard", "eligible", "eligibility", "apply", "application", "registration",
            "form", "document", "documents", "how to get", "how to apply",
            "kisan credit", "crop insurance", "fasal bima", "soil health", 
            "pension", "msp", "minimum support", "enroll", "enrollment", "register"
        ]
        if any(keyword in query_lower for keyword in policy_keywords):
            intent = "policy"
            required_agents.append("policy")
        
        # Default to weather and crop if no specific intent
        if not required_agents:
            required_agents = ["weather", "crop"]
        
        return {
            "intent": intent,
            "urgency": "medium",
            "required_agents": required_agents,
            "needs_realtime": "weather" in required_agents,
            "constraints": "",
            "confidence": 0.6
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
    
    async def process_query_async(self, query: str, location: str = None, crop: str = None) -> Dict[str, Any]:
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
                "workflow_trace": result.get("workflow_step", "completed")
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
    
    def process_query(self, query: str, location: str = None, crop: str = None) -> Dict[str, Any]:
        """Synchronous wrapper for async processing"""
        logger.info(f"🔄 SYNC PROCESS QUERY CALLED: Query='{query}'")
        try:
            # Check if we're already in an event loop
            try:
                loop = asyncio.get_running_loop()
                # We're in an async context, so we need to handle this differently
                logger.info("🔄 DETECTED RUNNING EVENT LOOP: Using sync execution")
                return self._process_query_sync(query, location, crop)
            except RuntimeError:
                # No running loop, safe to use asyncio.run()
                logger.info("🔄 NO RUNNING EVENT LOOP: Using async execution")
                return asyncio.run(self.process_query_async(query, location, crop))
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
    
    def _process_query_sync(self, query: str, location: str = None, crop: str = None) -> Dict[str, Any]:
        """Synchronous version that doesn't use LangGraph workflow"""
        logger.info(f"🔄 SYNC EXECUTION: Query='{query}' | Location='{location or 'N/A'}' | Crop='{crop or 'N/A'}'")
        try:
            # Direct agent execution without LangGraph when in async context
            query_lower = query.lower()
            
            # Improved routing with fuzzy matching and comprehensive keywords
            # Policy-related (highest priority - most specific)
            policy_patterns = [
                # Schemes and subsidies
                "subsidy", "subsidies", "scheme", "schemes", "policy", "policies", 
                "government", "benefit", "benefits", "allowance", "grant", "grants",
                
                # PM-Kisan variations (fuzzy matching)
                "pm kisan", "pm-kisan", "pmkisan", "pradhan mantri", "pradhanmantri",
                "pm kissan", "pm-kissan", "centrail pm", "central pm",
                
                # Application/eligibility terms
                "apply", "application", "eligible", "eligibility", "registration",
                "form", "document", "documents", "how to get", "how to apply",
                
                # Specific schemes
                "nabard", "kisan credit", "crop insurance", "fasal bima",
                "soil health", "pension", "msp", "minimum support",
                
                # Action words for schemes
                "enroll", "enrollment", "register", "registration"
            ]
            
            # Weather-related  
            weather_patterns = [
                "weather", "rain", "rainfall", "drought", "temperature", "forecast",
                "storm", "cyclone", "humidity", "wind", "climate", "monsoon",
                "precipitation", "alert", "warning"
            ]
            
            # Crop management
            crop_patterns = [
                "fertilizer", "fertiliser", "npk", "urea", "pest", "pests", 
                "disease", "diseases", "plant", "planting", "sow", "sowing",
                "transplant", "spacing", "growth", "harvest", "harvesting",
                "irrigation", "watering", "seed", "seeds", "variety"
            ]
            
            # Finance/market related
            finance_patterns = [
                "price", "prices", "market", "mandi", "rate", "rates", "cost", 
                "costs", "loan", "loans", "credit", "bank", "banking",
                "finance", "financial", "money", "investment", "profit",
                "selling", "buying", "trade"
            ]
            
            # Check patterns in order of specificity
            if any(pattern in query_lower for pattern in policy_patterns):
                logger.info(f"📋 SYNC ROUTING: Policy agent (matched policy patterns)")
                response = self.agents["policy"].process_query(query, location, crop)
                agent_name = "policy_agent"
            elif any(pattern in query_lower for pattern in weather_patterns):
                logger.info(f"🌤️ SYNC ROUTING: Weather agent (matched weather patterns)")
                response = self.agents["weather"].process_query(query, location, crop)
                agent_name = "weather_agent"
            elif any(pattern in query_lower for pattern in finance_patterns):
                logger.info(f"💰 SYNC ROUTING: Finance agent (matched finance patterns)")
                response = self.agents["finance"].process_query(query, location, crop)
                agent_name = "finance_agent"
            elif any(pattern in query_lower for pattern in crop_patterns):
                logger.info(f"🌱 SYNC ROUTING: Crop agent (matched crop patterns)")
                response = self.agents["crop"].process_query(query, location, crop)
                agent_name = "crop_agent"
            else:
                # Default to policy agent for application/general questions
                logger.info("📋 SYNC ROUTING: Default to policy agent (general agricultural query)")
                response = self.agents["policy"].process_query(query, location, crop)
                agent_name = "policy_agent"
            
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
                "workflow_trace": "sync_execution"
            }
            
            logger.info(f"✅ SYNC EXECUTION SUCCESS: Agent={agent_name} | Confidence={final_result['confidence']}")
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
