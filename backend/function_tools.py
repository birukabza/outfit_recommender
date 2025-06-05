from autogen_core.tools import FunctionTool
from datetime import datetime, timezone, timedelta
from pymongo.errors import PyMongoError
from db import outfit_collection
from db import recent_outfits_collection


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

def store_worn_outfits(username: str, outfits: list, date: datetime = None) -> str:
    """
    Store worn outfits for a user in the recent_outfits_collection.

    Parameters:
    - username: unique identifier of the user
    - outfits: list of outfits (each outfit is a list of clothing items)
               e.g., [[{"type": "shirt", "color": "blue"}], [{"type": "pants", "color": "black"}]]
    - date: datetime object representing the date the outfits were worn (defaults to now)

    Returns:
    - Confirmation string
    """

    if not isinstance(outfits, list) or not outfits:
        return "❌ No valid outfit data provided to store."

    try:
        timestamp = date or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        documents = [
            {
                "username": username,
                "outfit": outfits,
                "timestamp": timestamp,
            }
        ]

        if not documents:
            return "⚠️ All provided outfits were invalid. Nothing was saved."

        recent_outfits_collection.insert_one(documents)

        return f"✅ {len(documents)} worn outfit(s) saved for {username} on {timestamp.strftime('%Y-%m-%d')}."

    except PyMongoError as e:
        return "⚠️ Couldn't save your worn outfits due to a database error. Please try again later."


def retrieve_recent_outfits(username: str, days: int = 10) -> str:
    """
    Retrieve a user's outfits stored in the recent_outfits_collection within the past `days`.

    Parameters:
    - username: unique identifier of the user
    - days: number of past days to look back (default is 10)

    Returns:
    - A string description of recent outfits
    """
    try:
        threshold_date = datetime.now(timezone.utc) - timedelta(days=days)
        recent_outfits = list(
            recent_outfits_collection.find({
                "username": username,
                "timestamp": {"$gte": threshold_date}
            }).sort("timestamp", -1)
        )

        if not recent_outfits:
            return f"🧾 No outfits found in the last {days} days for user '{username}'."

        response = f"🕒 Outfits you've saved in the last {days} days, {username}:\n\n"
        for idx, item in enumerate(recent_outfits, start=1):
            response += f"🧥 Recent Outfit {idx}:\n"
            for piece in item["outfit"]:
                desc = f" - {piece.get('color', 'unknown')} {piece.get('type', 'item')}"
                if "style" in piece:
                    desc += f" ({piece['style']})"
                response += desc + "\n"
            time = item.get("timestamp")
            if isinstance(time, datetime):
                if time.tzinfo is None:
                    time = time.replace(tzinfo=timezone.utc)
                response += f"   ⏱️ Saved on {time.strftime('%Y-%m-%d %H:%M')}\n"

            response += "\n"

        return response.strip()

    except Exception as e:
        return "⚠️ Sorry, couldn't retrieve your recent outfits. Please check again soon!"

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

store_worn_outfit_tool = FunctionTool(
    name="store_worn_outfits",
    func=store_worn_outfits,
    description="Stores the user's worn outfit"
)

retrieve_recent_outfit_tool = FunctionTool(
    name="retrieve_recent_outfit",
    func=retrieve_recent_outfits,
    description="Retrieves the recent outfits worn by the user"
)