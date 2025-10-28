"""
LangGraph Workflow
Wires up all nodes and edges into a compiled graph
"""
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.mongodb import MongoDBSaver
from langchain_openai import ChatOpenAI
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.agent.models import AgentState
from app.agent.supervisor import supervisor_router
from app.agent.workers.classify_intent import classify_intent_worker
from app.agent.workers.slot_filler import slot_filler_worker
from app.agent.workers.order_lookup import order_lookup_worker
from app.agent.workers.confirm_details import confirm_details_worker
from app.agent.workers.policy_check import policy_check_worker
from app.agent.workers.decide_action import decide_action_worker
from app.agent.workers.process_return import process_return_worker
from app.agent.workers.process_refund import process_refund_worker
from app.agent.workers.email import email_worker
from app.agent.workers.show_order_status import show_order_status_worker
from app.agent.workers.finalize import finalize_worker


def create_agent_graph(llm: ChatOpenAI, db: AsyncIOMotorDatabase, checkpointer: MongoDBSaver):
    """
    Create and compile the LangGraph workflow with MongoDB checkpointing
    
    Args:
        llm: Language model instance
        db: MongoDB database instance (async)
        checkpointer: MongoDBSaver instance (global, reused)
        
    Returns:
        Compiled graph with checkpointing
    """
    # Create wrapper functions that properly await async workers
    async def classify_intent_node(state: AgentState):
        print(f"[GRAPH] Executing classify_intent_node")
        print(f"[GRAPH] State received: intent={state.get('intent')}, order_number={state.get('order_number')}, messages_count={len(state.get('messages', []))}")
        result = await classify_intent_worker(state, llm)
        print(f"[GRAPH] classify_intent result: intent={result.get('intent')}")
        return result
    
    async def slot_filler_node(state: AgentState):
        print(f"[GRAPH] Executing slot_filler_node")
        print(f"[GRAPH] State received: intent={state.get('intent')}, order_number={state.get('order_number')}, messages_count={len(state.get('messages', []))}")
        result = await slot_filler_worker(state, llm)
        print(f"[GRAPH] slot_filler result: order_number={result.get('order_number')}")
        return result
    
    async def order_lookup_node(state: AgentState):
        print(f"[GRAPH] Executing order_lookup_node")
        result = await order_lookup_worker(state, db)
        print(f"[GRAPH] order_lookup result: has_order={result.get('order') is not None}")
        return result
    
    async def confirm_details_node(state: AgentState):
        print(f"[GRAPH] Executing confirm_details_node")
        result = await confirm_details_worker(state)
        print(f"[GRAPH] confirm_details result: confirmed={result.get('user_confirmed_order')}")
        return result
    
    async def policy_check_node(state: AgentState):
        print(f"[GRAPH] Executing policy_check_node")
        result = await policy_check_worker(state)
        print(f"[GRAPH] policy_check result: eligibility set")
        return result
    
    async def decide_action_node(state: AgentState):
        print(f"[GRAPH] Executing decide_action_node")
        result = await decide_action_worker(state)
        print(f"[GRAPH] decide_action result: action={result.get('desired_action')}")
        return result
    
    async def process_return_node(state: AgentState):
        print(f"[GRAPH] Executing process_return_node")
        result = await process_return_worker(state, db)
        print(f"[GRAPH] process_return result: ticket={result.get('action_ticket', {}).get('id')}")
        return result
    
    async def process_refund_node(state: AgentState):
        print(f"[GRAPH] Executing process_refund_node")
        result = await process_refund_worker(state, db)
        print(f"[GRAPH] process_refund result: ticket={result.get('action_ticket', {}).get('id')}")
        return result
    
    async def email_node(state: AgentState):
        print(f"[GRAPH] Executing email_node")
        result = await email_worker(state)
        print(f"[GRAPH] email result: status={result.get('email_status')}")
        return result
    
    async def show_order_status_node(state: AgentState):
        print(f"[GRAPH] Executing show_order_status_node")
        result = await show_order_status_worker(state)
        print(f"[GRAPH] show_order_status complete")
        return result
    
    async def finalize_node(state: AgentState):
        print(f"[GRAPH] Executing finalize_node")
        result = await finalize_worker(state)
        print(f"[GRAPH] finalize result keys: {result.keys()}")
        print(f"[GRAPH] conversation_complete in result: {result.get('conversation_complete')}")
        print(f"[GRAPH] finalize complete - should END now")
        return result
    
    # Create the state graph
    workflow = StateGraph(AgentState)
    
    # Add worker nodes
    workflow.add_node("classify_intent", classify_intent_node)
    workflow.add_node("slot_filler", slot_filler_node)
    workflow.add_node("order_lookup", order_lookup_node)
    workflow.add_node("confirm_details", confirm_details_node)
    workflow.add_node("policy_check", policy_check_node)
    workflow.add_node("decide_action", decide_action_node)
    workflow.add_node("process_return", process_return_node)
    workflow.add_node("process_refund", process_refund_node)
    workflow.add_node("email", email_node)
    workflow.add_node("show_order_status", show_order_status_node)
    workflow.add_node("finalize", finalize_node)
    
    # Set the entry point
    workflow.set_entry_point("classify_intent")
    
    # Add conditional edges from each node back to supervisor routing
    workflow.add_conditional_edges(
        "classify_intent",
        supervisor_router,
        {
            "classify_intent": "classify_intent",
            "slot_filler": "slot_filler",
            "order_lookup": "order_lookup",
            "confirm_details": "confirm_details",
            "policy_check": "policy_check",
            "decide_action": "decide_action",
            "process_return": "process_return",
            "process_refund": "process_refund",
            "email": "email",
            "show_order_status": "show_order_status",
            "finalize": "finalize",
            "__end__": END
        }
    )
    
    workflow.add_conditional_edges(
        "slot_filler",
        supervisor_router,
        {
            "classify_intent": "classify_intent",
            "slot_filler": "slot_filler",
            "order_lookup": "order_lookup",
            "confirm_details": "confirm_details",
            "policy_check": "policy_check",
            "decide_action": "decide_action",
            "process_return": "process_return",
            "process_refund": "process_refund",
            "email": "email",
            "show_order_status": "show_order_status",
            "finalize": "finalize",
            "__end__": END
        }
    )
    
    workflow.add_conditional_edges(
        "order_lookup",
        supervisor_router,
        {
            "classify_intent": "classify_intent",
            "slot_filler": "slot_filler",
            "order_lookup": "order_lookup",
            "confirm_details": "confirm_details",
            "policy_check": "policy_check",
            "decide_action": "decide_action",
            "process_return": "process_return",
            "process_refund": "process_refund",
            "email": "email",
            "show_order_status": "show_order_status",
            "finalize": "finalize",
            "__end__": END
        }
    )
    
    workflow.add_conditional_edges(
        "confirm_details",
        supervisor_router,
        {
            "classify_intent": "classify_intent",
            "slot_filler": "slot_filler",
            "order_lookup": "order_lookup",
            "confirm_details": "confirm_details",
            "policy_check": "policy_check",
            "decide_action": "decide_action",
            "process_return": "process_return",
            "process_refund": "process_refund",
            "email": "email",
            "show_order_status": "show_order_status",
            "finalize": "finalize",
            "__end__": END
        }
    )
    
    workflow.add_conditional_edges(
        "policy_check",
        supervisor_router,
        {
            "classify_intent": "classify_intent",
            "slot_filler": "slot_filler",
            "order_lookup": "order_lookup",
            "confirm_details": "confirm_details",
            "policy_check": "policy_check",
            "decide_action": "decide_action",
            "process_return": "process_return",
            "process_refund": "process_refund",
            "email": "email",
            "show_order_status": "show_order_status",
            "finalize": "finalize",
            "__end__": END
        }
    )
    
    workflow.add_conditional_edges(
        "decide_action",
        supervisor_router,
        {
            "classify_intent": "classify_intent",
            "slot_filler": "slot_filler",
            "order_lookup": "order_lookup",
            "confirm_details": "confirm_details",
            "policy_check": "policy_check",
            "decide_action": "decide_action",
            "process_return": "process_return",
            "process_refund": "process_refund",
            "email": "email",
            "show_order_status": "show_order_status",
            "finalize": "finalize",
            "__end__": END
        }
    )
    
    workflow.add_conditional_edges(
        "process_return",
        supervisor_router,
        {
            "classify_intent": "classify_intent",
            "slot_filler": "slot_filler",
            "order_lookup": "order_lookup",
            "confirm_details": "confirm_details",
            "policy_check": "policy_check",
            "decide_action": "decide_action",
            "process_return": "process_return",
            "process_refund": "process_refund",
            "email": "email",
            "show_order_status": "show_order_status",
            "finalize": "finalize",
            "__end__": END
        }
    )
    
    workflow.add_conditional_edges(
        "process_refund",
        supervisor_router,
        {
            "classify_intent": "classify_intent",
            "slot_filler": "slot_filler",
            "order_lookup": "order_lookup",
            "confirm_details": "confirm_details",
            "policy_check": "policy_check",
            "decide_action": "decide_action",
            "process_return": "process_return",
            "process_refund": "process_refund",
            "email": "email",
            "show_order_status": "show_order_status",
            "finalize": "finalize",
            "__end__": END
        }
    )
    
    workflow.add_conditional_edges(
        "email",
        supervisor_router,
        {
            "classify_intent": "classify_intent",
            "slot_filler": "slot_filler",
            "order_lookup": "order_lookup",
            "confirm_details": "confirm_details",
            "policy_check": "policy_check",
            "decide_action": "decide_action",
            "process_return": "process_return",
            "process_refund": "process_refund",
            "email": "email",
            "show_order_status": "show_order_status",
            "finalize": "finalize",
            "__end__": END
        }
    )
    
    workflow.add_conditional_edges(
        "show_order_status",
        supervisor_router,
        {
            "classify_intent": "classify_intent",
            "slot_filler": "slot_filler",
            "order_lookup": "order_lookup",
            "confirm_details": "confirm_details",
            "policy_check": "policy_check",
            "decide_action": "decide_action",
            "process_return": "process_return",
            "process_refund": "process_refund",
            "email": "email",
            "show_order_status": "show_order_status",
            "finalize": "finalize",
            "__end__": END
        }
    )
    
    # Finalize ends the workflow
    workflow.add_edge("finalize", END)
    
    # Compile with the provided checkpointer (global instance)
    print("[GRAPH] Compiling graph with checkpointer")
    return workflow.compile(checkpointer=checkpointer)
