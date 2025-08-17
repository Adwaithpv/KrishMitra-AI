# LangGraph Supervisor Architecture

## Overview

The Agentic Agri Advisor has been restructured to use a **LangGraph-based supervisor architecture** that provides intelligent orchestration, better decision-making, and enhanced coordination between specialized agents.

## Architecture Comparison

### Before: Simple Coordinator
```
User Query → Coordinator → Keyword Matching → Agent Selection → Response Synthesis
```

### After: LangGraph Supervisor
```
User Query → Supervisor → LLM Analysis → Intelligent Routing → Agent Execution → Response Synthesis → Validation
```

## Key Components

### 1. Supervisor Agent (`supervisor.py`)
The main orchestrator that manages the entire workflow using LangGraph's state machine approach.

**Features:**
- **LLM-powered query analysis** for intent understanding
- **Intelligent agent routing** based on query context
- **Stateful workflow management** with checkpointing
- **Response synthesis and validation**
- **Error handling and fallback mechanisms**

### 2. Workflow Nodes

#### `analyze_query`
- Uses LLM to analyze user intent and context
- Determines required agents and urgency level
- Identifies if real-time data is needed
- Provides fallback keyword-based analysis

#### `route_to_agents`
- Manages agent execution order
- Tracks which agents have been executed
- Determines next agent to call
- Handles multi-agent coordination

#### `execute_[agent]_agent`
- Individual execution nodes for each agent type
- Maintains state consistency
- Handles agent-specific errors
- Collects responses for synthesis

#### `synthesize_response`
- Combines multiple agent responses
- Prioritizes information based on relevance
- Maintains conversational tone
- Calculates overall confidence

#### `validate_response`
- Quality assurance for final responses
- Safety checks for agricultural advice
- Confidence level validation
- Response improvement if needed

## Workflow States

```python
class AgentState(TypedDict):
    query: str                    # Original user query
    location: str                 # User location
    crop: str                     # User's crop
    user_context: Dict[str, Any]  # LLM analysis results
    agent_decisions: List[Dict]   # Routing decisions
    agent_responses: List[Dict]   # Agent outputs
    final_answer: str             # Synthesized response
    evidence: List[Dict]          # Supporting evidence
    confidence: float             # Overall confidence
    workflow_step: str            # Current workflow state
    error: str                    # Error information
```

## Workflow Graph

```
start → analyze_query → route_to_agents → [agent_execution] → synthesize_response → validate_response → end
                ↓              ↓                    ↓                ↓
            intent_analysis  agent_routing    parallel_execution  quality_check
```

## Benefits of LangGraph Architecture

### 1. **Intelligent Decision Making**
- LLM-powered query analysis instead of simple keyword matching
- Context-aware agent selection
- Dynamic routing based on query complexity

### 2. **Stateful Execution**
- Maintains conversation context across workflow steps
- Checkpointing for long-running operations
- Ability to resume interrupted workflows

### 3. **Better Error Handling**
- Graceful degradation when agents fail
- Fallback mechanisms at each step
- Detailed error tracking and reporting

### 4. **Enhanced Coordination**
- Sequential and parallel agent execution
- Response synthesis with conflict resolution
- Validation and quality assurance

### 5. **Observability**
- Detailed workflow traces
- Agent usage statistics
- Performance monitoring
- Debug information for each step

## API Endpoints

### New Supervisor Endpoint
```
GET /supervisor?text=<query>&location=<location>&crop=<crop>
```

**Response:**
```json
{
  "query": "What's the weather like for rice farming?",
  "location": "Karnataka",
  "crop": "rice",
  "response": {
    "answer": "Based on current weather conditions...",
    "confidence": 0.85,
    "evidence": [...],
    "agents_consulted": ["weather_agent", "crop_agent"]
  },
  "workflow_trace": "completed",
  "agents_consulted": ["weather_agent", "crop_agent"],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Legacy Compatibility
The `/agents` endpoint continues to work but now uses the supervisor internally.

## Configuration

### Environment Variables
```bash
# LangGraph configuration
LANGGRAPH_DEBUG=true  # Enable debug mode
LANGGRAPH_CHECKPOINT_DIR=/tmp/checkpoints  # Checkpoint storage

# LLM configuration (existing)
GEMINI_API_KEY=your_key
LOCAL_MODEL=microsoft/DialoGPT-small
```

### Supervisor Configuration
```python
# In supervisor.py
class SupervisorAgent:
    def __init__(self):
        self.agents = {
            "weather": WeatherAgent(),
            "crop": CropAgent(),
            "finance": FinanceAgent(),
            "policy": PolicyAgent()
        }
        self.llm_client = LLMClient()
        self.graph = self._build_workflow()
```

## Testing

### Test Script
```bash
# Run the comprehensive test suite
python scripts/test_supervisor.py
```

### Test Categories
1. **Weather Queries** - Real-time weather data integration
2. **Crop Management** - Agricultural best practices
3. **Finance Queries** - Market prices and subsidies
4. **Policy Queries** - Government schemes and eligibility
5. **Complex Multi-Agent** - Queries requiring multiple agents

### Performance Metrics
- **Success Rate**: Percentage of successful queries
- **Average Confidence**: Overall response confidence
- **Agent Usage**: Which agents are most frequently used
- **Response Time**: End-to-end processing time
- **Workflow Traces**: Detailed execution paths

## Migration Guide

### From Coordinator to Supervisor

1. **Update imports:**
```python
# Old
from .coordinator import Coordinator

# New
from .supervisor import SupervisorAgent
```

2. **Update function calls:**
```python
# Old
coordinator = Coordinator()
response = coordinator.process_query(query, location, crop)

# New
supervisor = SupervisorAgent()
response = supervisor.process_query(query, location, crop)
```

3. **Handle new response format:**
```python
# New fields available
workflow_trace = response.get("workflow_trace", "unknown")
agents_consulted = response.get("agents_consulted", [])
```

### Backward Compatibility
- All existing endpoints continue to work
- Response format is compatible with existing clients
- Gradual migration possible

## Future Enhancements

### 1. **Advanced Routing**
- Machine learning-based agent selection
- User preference learning
- Context-aware routing

### 2. **Parallel Execution**
- Concurrent agent execution for complex queries
- Load balancing across agents
- Resource optimization

### 3. **Enhanced Validation**
- Domain-specific validation rules
- Safety checks for agricultural advice
- Compliance with regulatory requirements

### 4. **Workflow Persistence**
- Long-running conversation support
- Workflow resumption capabilities
- Conversation history management

### 5. **Monitoring and Analytics**
- Real-time workflow monitoring
- Performance analytics
- Agent effectiveness metrics

## Troubleshooting

### Common Issues

1. **LangGraph Import Errors**
```bash
pip install langgraph==0.2.16 langchain==0.2.16
```

2. **Workflow Timeout**
- Increase timeout in test scripts
- Check agent response times
- Monitor system resources

3. **Agent Failures**
- Check individual agent health
- Verify API keys and external services
- Review error logs

### Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Health Checks
```bash
# Check supervisor health
curl http://localhost:8000/supervisor?text=test

# Check detailed health
curl http://localhost:8000/health/detailed
```

## Conclusion

The LangGraph supervisor architecture provides a robust, scalable, and intelligent foundation for the Agentic Agri Advisor. It enhances the system's ability to understand user queries, coordinate multiple specialized agents, and deliver high-quality, evidence-based agricultural advice.

The architecture maintains backward compatibility while providing significant improvements in decision-making, error handling, and system observability.
