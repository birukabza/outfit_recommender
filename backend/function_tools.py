from autogen_core.tools import FunctionTool
from datetime import datetime, timezone
from pymongo.errors import PyMongoError
from db import outfit_collection


def store_user_outfit(username: str, outfit: list) -> str:
    """
    Store a user's uploaded outfit to MongoDB.

    Parameters:
    - username: unique identifier of the user
    - outfit: list of clothing items (e.g., [{"type": "hoodie", "color": "red"}])

    Returns:
    - Confirmation string
    """
    if not isinstance(outfit, list) or not outfit:
        return "No valid outfit data provided."

    try:
        data = {
            "username": username,
            "outfit": outfit,
            "timestamp": datetime.now(timezone.utc),
        }
        outfit_collection.insert_one(data)
        return "✅ Outfit saved successfully! You’ve got style 😎"

    except PyMongoError as e:
        return (
            "⚠️ Sorry, I couldn't save your outfit right now — looks like I'm having trouble connecting to the database. Please try again later!"
            + e
        )


def retrieve_user_outfit(username: str) -> str:
    """
    retrieves user's outfit
    Args:
        username (str): user's unique Identifier
    Returns:
        dict: dictionary of user outfits
    """

    try:
        outfits = list(
            outfit_collection.find({"username": username}).sort("timestamp", -1)
        )

        if not outfits:
            return "👕 You haven't saved any outfits yet. Try adding one and I'll keep track for you!"

        # Format the outfit list
        response = f"Here are your saved outfits, {username}:\n\n"
        for idx, item in enumerate(outfits, start=1):
            response += f"🧥 Outfit {idx}:\n"
            for piece in item["outfit"]:
                desc = f" - {piece.get('color', 'unknown')} {piece.get('type', 'item')}"
                if "style" in piece:
                    desc += f" ({piece['style']})"
                response += desc + "\n"
            time = item.get("timestamp")
            if time:
                if time.tzinfo is None:
                    time = time.replace(tzinfo=timezone.utc)

            if isinstance(time, datetime):
                response += f"   ⏱️ Saved on {time.strftime('%Y-%m-%d %H:%M')}\n"

            response += "\n"

        return response.strip()

    except Exception as e:
        return "⚠️ Hmm, I couldn't fetch your outfits right now — the database might be down. Please try again soon!"


retrieve_outfit_tool = FunctionTool(
    name="retrieve_user_outfit",
    func=retrieve_user_outfit,
    description="Retrieve already stored outfits of the given user",
)


store_outfit_tool = FunctionTool(
    name="store_user_outfit",
    func=store_user_outfit,
    description="Store the uploaded outfit in MongoDB for a given user.",
)
