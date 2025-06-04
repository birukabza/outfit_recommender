from autogen_agentchat.agents import AssistantAgent
from model_client import model_client
from function_tools import store_outfit_tool, retrieve_outfit_tool
from autogen_core.memory import MemoryContent, ListMemory
from db import sessions_collection
from bson import ObjectId


def load_system_message(path: str) -> str:
    with open(path, "r", encoding="utf-8") as message:
        return message.read()


SYSTEM_MESSAGE = load_system_message("prompts/system_message.txt")

# Dictionary to store active agents
active_agents = {}


def create_agent(session_id: str) -> AssistantAgent:
    """
    Create or retrieve an agent for a specific session.
    Each session gets its own agent with its own memory.

    Args:
        session_id: The ID of the chat session
    """
    if session_id in active_agents:
        return active_agents[session_id]

    # Get session history from database
    session = sessions_collection.find_one({"_id": ObjectId(session_id)})
    memory = ListMemory()

    async def addMemory():
        if session and "messages" in session:
            sorted_messages = sorted(
                session["messages"], key=lambda m: m.get("timestamp", "")
            )
            print(sorted_messages)
            recent_messages = sorted_messages[-15:]

            for msg in recent_messages:
                memory_content = MemoryContent(
                    role=msg["role"], content=msg["content"], mime_type="text/plain"
                )
                await memory.add(memory_content)
    
    personalized_message = f"You are assisting a user with username: '{session["user_id"]}'.\n\n{SYSTEM_MESSAGE}"
    addMemory()
    # Create new agent with session-specific memory
    agent = AssistantAgent(
        name=f"assistant_{session_id}",
        model_client=model_client,
        tools=[store_outfit_tool, retrieve_outfit_tool],
        reflect_on_tool_use=True,
        system_message=personalized_message,
        memory=[memory],
    )

    # Store agent in active agents
    active_agents[session_id] = agent
    return agent
