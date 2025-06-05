from autogen_agentchat.agents import AssistantAgent
from model_client import model_client
from function_tools import (
                                store_outfit_tool, 
                                retrieve_outfit_tool, 
                                retrieve_recent_outfit_tool, 
                                store_worn_outfit_tool,
                                get_weather_tool,
                                save_outfit_feedback_tool,
                                filter_outfits_by_feedback_tool
                            )
from autogen_core.memory import MemoryContent, ListMemory
from db import sessions_collection
from bson import ObjectId
from typing import Optional, Dict, Any
import asyncio

def load_system_message(path: str) -> str:
    with open(path, "r", encoding="utf-8") as message:
        return message.read()


SYSTEM_MESSAGE = load_system_message("prompts/system_message.txt")

# Dictionary to store active agents
active_agents = {}



def create_agent(session_id: str,
                 location: Optional[Dict[str, Any]] = None) -> AssistantAgent:
    """
    Create or retrieve an agent for a specific session.

    Args:
        session_id: The ID of the chat session
        location:   Dict with "latitude" and "longitude" (may be None)
    """
    if session_id in active_agents:
        return active_agents[session_id]
    
    print(location)
    # Fetch session history
    session = sessions_collection.find_one({"_id": ObjectId(session_id)})
    memory = ListMemory()

    async def add_memory():
        if session and "messages" in session:
            for msg in sorted(session["messages"],
                              key=lambda m: m.get("timestamp", ""))[-15:]:
                await memory.add(
                    MemoryContent(
                        role=msg["role"],
                        content=msg["content"],
                        mime_type="text/plain",
                    )
                )

    # ---- Build the personalized system prompt ----
    coords_txt = ""
    if location and "latitude" in location and "longitude" in location:
        coords_txt = (
            f" (current location: "
            f"lat {location['latitude']:.6f}, "
            f"lon {location['longitude']:.6f})"
        )

    personalized_message = (
        f"You are assisting a user with username: '{session['user_id']}'"
        f"{coords_txt}.\n\n"
        f"{SYSTEM_MESSAGE}\n\n"
        "IMPORTANT: Always check the conversation history in your memory before responding. "
        "Your responses should be contextual and reference previous messages when relevant. "
        "If a user asks about something that was discussed before, use that context in your response. "
        "When responding, first check your memory for relevant previous messages and incorporate that context into your response."
    )

    # Run the async function to add memory
    asyncio.run(add_memory())

    func_tools = [
        store_outfit_tool,
        retrieve_outfit_tool,
        retrieve_recent_outfit_tool,
        store_worn_outfit_tool,
        get_weather_tool,
        save_outfit_feedback_tool,
        filter_outfits_by_feedback_tool,
    ]

    agent = AssistantAgent(
        name=f"assistant_{session_id}",
        model_client=model_client,
        tools=func_tools,
        reflect_on_tool_use=True,
        system_message=personalized_message,
        memory=[memory]
    )

    active_agents[session_id] = agent
    return agent
