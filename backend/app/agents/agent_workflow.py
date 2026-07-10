import uuid
import datetime
from typing import TypedDict, List, Dict, Any, Annotated
from langgraph.graph import StateGraph, END
from sqlalchemy.orm import Session

from app.models.models import AgentInteraction, Asset
from app.config.settings import settings

# Define LangGraph workflow state
class AgentWorkflowState(TypedDict):
    workflow_id: str
    asset_id: str
    user_query: str
    conversation_history: List[Dict[str, str]] # List of {"agent": str, "message": str}
    next_node: str
    incident_severity: str # Low, Medium, High, Extreme
    metadata: Dict[str, Any]

# Helper function to append dialogues and write to the database
def record_agent_interaction(db: Session, workflow_id: str, sender: str, recipient: str, message: str, state: dict):
    interaction = AgentInteraction(
        workflow_id=workflow_id,
        sender=sender,
        recipient=recipient,
        message=message,
        agent_state=state,
        timestamp=datetime.datetime.utcnow()
    )
    db.add(interaction)
    db.commit()

# --- AGENT NODES ---

def supervisor_agent_node(state: AgentWorkflowState) -> AgentWorkflowState:
    history = state["conversation_history"]
    query = state["user_query"].lower()
    
    # Simple routing logic simulating LLM supervisor decisions
    if "weather" in query or "storm" in query or "rain" in query or "cyclone" in query:
        next_agent = "weather_agent"
    elif "drone" in query or "flyover" in query or "camera" in query:
        next_agent = "drone_agent"
    elif "repair" in query or "maintenance" in query or "fix" in query or "cost" in query:
        next_agent = "maintenance_agent"
    elif "evacuate" in query or "collapse" in query or "disaster" in query or "rupture" in query or "flood" in query:
        next_agent = "emergency_agent"
    elif "traffic" in query or "road" in query or "car" in query:
        next_agent = "traffic_agent"
    elif "finance" in query or "budget" in query:
        next_agent = "finance_agent"
    elif "citizen" in query or "public" in query or "pothole" in query:
        next_agent = "citizen_agent"
    elif "regulatory" in query or "fema" in query or "government" in query:
        next_agent = "government_agent"
    else:
        # Default chain if asset health is low
        if state["incident_severity"] in ["High", "Extreme"]:
            next_agent = "emergency_agent"
        else:
            next_agent = "infrastructure_agent"
            
    msg = f"Supervisor: Routing control to {next_agent.replace('_', ' ').title()} to address task: '{state['user_query']}'."
    history.append({"agent": "Supervisor", "message": msg})
    
    return {
        **state,
        "conversation_history": history,
        "next_node": next_agent
    }

def infrastructure_agent_node(state: AgentWorkflowState) -> AgentWorkflowState:
    history = state["conversation_history"]
    
    msg = f"Infrastructure Agent: Analyzing asset metadata for ID {state['asset_id']}. " \
          f"Historical inspection logs suggest general stress corrosion. Recommending structural integrity scan."
          
    history.append({"agent": "Infrastructure Agent", "message": msg})
    
    # Decide next step (let maintenance agent know)
    return {
        **state,
        "conversation_history": history,
        "next_node": "maintenance_agent"
    }

def weather_agent_node(state: AgentWorkflowState) -> AgentWorkflowState:
    history = state["conversation_history"]
    
    msg = "Weather Agent: Fetched live NOAA radar feeds. A heavy weather system is approaching. " \
          "Expected wind speed gusts 65 km/h, cumulative rainfall 110mm over the next 12 hours. Risk of localized washouts."
          
    history.append({"agent": "Weather Agent", "message": msg})
    
    return {
        **state,
        "conversation_history": history,
        "next_node": "drone_agent" if state["incident_severity"] == "Extreme" else "supervisor_agent"
    }

def maintenance_agent_node(state: AgentWorkflowState) -> AgentWorkflowState:
    history = state["conversation_history"]
    
    msg = "Maintenance Agent: Reviewed task backlog. Recommending immediate joint reinforcement and bolt tightening. " \
          "Estimated duration: 36 hours. Material specs: Carbon steel grade GR8. Estimated labor: 4 field technicians."
          
    history.append({"agent": "Maintenance Agent", "message": msg})
    
    return {
        **state,
        "conversation_history": history,
        "next_node": "finance_agent"
    }

def emergency_agent_node(state: AgentWorkflowState) -> AgentWorkflowState:
    history = state["conversation_history"]
    
    msg = "Emergency Agent: Extreme stress thresholds breached! Drafting evacuation protocols. " \
          "Coordinating with municipal dispatch. Requesting immediate deployment of emergency services."
          
    history.append({"agent": "Emergency Agent", "message": msg})
    
    return {
        **state,
        "conversation_history": history,
        "next_node": "traffic_agent"
    }

def drone_agent_node(state: AgentWorkflowState) -> AgentWorkflowState:
    history = state["conversation_history"]
    
    msg = "Drone Agent: Dispatching UAV Sentinel-1. Target altitude 50m. Thermal imagery feed initiated. " \
          "UAV scanning coordinates for micro-fractures. Transmission strength: 94%."
          
    history.append({"agent": "Drone Agent", "message": msg})
    
    return {
        **state,
        "conversation_history": history,
        "next_node": "supervisor_agent"
    }

def traffic_agent_node(state: AgentWorkflowState) -> AgentWorkflowState:
    history = state["conversation_history"]
    
    msg = "Traffic Agent: Rerouting transit vehicles away from risk sector. " \
          "Pre-configuring digital highway notice displays. Expecting standard bypass delay of 12-15 minutes."
          
    history.append({"agent": "Traffic Agent", "message": msg})
    
    return {
        **state,
        "conversation_history": history,
        "next_node": "government_agent"
    }

def finance_agent_node(state: AgentWorkflowState) -> AgentWorkflowState:
    history = state["conversation_history"]
    
    msg = "Finance Agent: Estimated budget allocation for repairs is $125,000. " \
          "Emergency contingency fund covers up to $250,000. General ledger status: Approved."
          
    history.append({"agent": "Finance Agent", "message": msg})
    
    return {
        **state,
        "conversation_history": history,
        "next_node": "supervisor_agent"
    }

def citizen_agent_node(state: AgentWorkflowState) -> AgentWorkflowState:
    history = state["conversation_history"]
    
    msg = "Citizen Agent: Consolidating local report tickets. Citizens reported visual concrete crack enlargement. " \
          "Informing supervisor of elevated public hazard alerts."
          
    history.append({"agent": "Citizen Agent", "message": msg})
    
    return {
        **state,
        "conversation_history": history,
        "next_node": "supervisor_agent"
    }

def government_agent_node(state: AgentWorkflowState) -> AgentWorkflowState:
    history = state["conversation_history"]
    
    msg = "Government Agent: Issuing safety declaration to the State Infrastructure Council. " \
          "Authorizing emergency maintenance contract and releasing standard community alerts."
          
    history.append({"agent": "Government Agent", "message": msg})
    
    return {
        **state,
        "conversation_history": history,
        "next_node": "end"
    }

# --- LANGGRAPH ASSEMBLY ---

def build_agents_graph():
    workflow = StateGraph(AgentWorkflowState)
    
    # Add Nodes
    workflow.add_node("supervisor_agent", supervisor_agent_node)
    workflow.add_node("infrastructure_agent", infrastructure_agent_node)
    workflow.add_node("weather_agent", weather_agent_node)
    workflow.add_node("maintenance_agent", maintenance_agent_node)
    workflow.add_node("emergency_agent", emergency_agent_node)
    workflow.add_node("drone_agent", drone_agent_node)
    workflow.add_node("traffic_agent", traffic_agent_node)
    workflow.add_node("finance_agent", finance_agent_node)
    workflow.add_node("citizen_agent", citizen_agent_node)
    workflow.add_node("government_agent", government_agent_node)
    
    # Set Entry Point
    workflow.set_entry_point("supervisor_agent")
    
    # Conditional edge routing from Supervisor
    def route_supervisor(state: AgentWorkflowState):
        return state["next_node"]
        
    workflow.add_conditional_edges(
        "supervisor_agent",
        route_supervisor,
        {
            "infrastructure_agent": "infrastructure_agent",
            "weather_agent": "weather_agent",
            "maintenance_agent": "maintenance_agent",
            "emergency_agent": "emergency_agent",
            "drone_agent": "drone_agent",
            "traffic_agent": "traffic_agent",
            "finance_agent": "finance_agent",
            "citizen_agent": "citizen_agent",
            "government_agent": "government_agent",
            "supervisor_agent": "supervisor_agent"
        }
    )
    
    # Define simple static edges linking agents back or onwards
    workflow.add_edge("infrastructure_agent", "maintenance_agent")
    workflow.add_edge("maintenance_agent", "finance_agent")
    workflow.add_edge("finance_agent", "supervisor_agent")
    
    workflow.add_edge("weather_agent", "supervisor_agent")
    workflow.add_edge("drone_agent", "supervisor_agent")
    workflow.add_edge("citizen_agent", "supervisor_agent")
    
    workflow.add_edge("emergency_agent", "traffic_agent")
    workflow.add_edge("traffic_agent", "government_agent")
    
    # End node paths
    workflow.add_node("end_node", lambda state: {**state, "next_node": "end"})
    workflow.add_edge("government_agent", "end_node")
    workflow.add_edge("end_node", END)
    
    return workflow.compile()

# Instantiate compiled workflow graph
agent_graph = build_agents_graph()

def run_agent_workflow(db: Session, asset_id: str, query: str) -> List[Dict[str, str]]:
    """
    Executes the multi-agent coordination workflow. Logs every step to the DB.
    """
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    severity = "Medium"
    if asset:
        if asset.health_score < 70.0:
            severity = "High"
        if asset.health_score < 50.0:
            severity = "Extreme"
            
    workflow_id = str(uuid.uuid4())
    
    initial_state = AgentWorkflowState(
        workflow_id=workflow_id,
        asset_id=asset_id,
        user_query=query,
        conversation_history=[],
        next_node="",
        incident_severity=severity,
        metadata={"timestamp": datetime.datetime.utcnow().isoformat()}
    )
    
    # Run the compiled Graph
    current_state = initial_state
    step = 0
    max_steps = 15
    
    # Traverse state node transitions
    node = "supervisor_agent"
    while node != END and step < max_steps:
        # Resolve node function
        if node == "supervisor_agent":
            current_state = supervisor_agent_node(current_state)
        elif node == "infrastructure_agent":
            current_state = infrastructure_agent_node(current_state)
        elif node == "weather_agent":
            current_state = weather_agent_node(current_state)
        elif node == "maintenance_agent":
            current_state = maintenance_agent_node(current_state)
        elif node == "emergency_agent":
            current_state = emergency_agent_node(current_state)
        elif node == "drone_agent":
            current_state = drone_agent_node(current_state)
        elif node == "traffic_agent":
            current_state = traffic_agent_node(current_state)
        elif node == "finance_agent":
            current_state = finance_agent_node(current_state)
        elif node == "citizen_agent":
            current_state = citizen_agent_node(current_state)
        elif node == "government_agent":
            current_state = government_agent_node(current_state)
        elif node == "end_node":
            break
            
        step += 1
        
        # Log node outputs to database
        if len(current_state["conversation_history"]) > 0:
            latest_dialogue = current_state["conversation_history"][-1]
            record_agent_interaction(
                db=db,
                workflow_id=workflow_id,
                sender=latest_dialogue["agent"],
                recipient=current_state["next_node"] or "END",
                message=latest_dialogue["message"],
                state={"step": step, "next": current_state["next_node"]}
            )
            
        node = current_state["next_node"]
        if not node or node == "end":
            break
            
    return current_state["conversation_history"]
