import os
import jwt
from datetime import datetime, timezone, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from db import users_collection, sessions_collection
from auth import token_required
from assistant import create_agent
from bson import ObjectId
import asyncio
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    required = ("username", "password", "email")
    if not all(data.get(k) for k in required):
        return jsonify({"message": "username, password & email required"}), 400

    if users_collection.find_one(
        {"$or": [{"username": data["username"]}, {"email": data["email"]}]}
    ):
        return jsonify({"message": "Username or e-mail already exists"}), 400

    hashed = generate_password_hash(data["password"])
    users_collection.insert_one(
        {
            "username": data["username"],
            "email": data["email"],
            "password": hashed,
            "created": datetime.now(timezone.utc),
        }
    )
    return jsonify({"message": "User registered successfully"}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or not data.get("username") or not data.get("password"):
        return jsonify({"message": "Missing username or password"}), 400
    user = users_collection.find_one({"username": data["username"]})
    if not user or not check_password_hash(user["password"], data["password"]):
        return jsonify({"message": "Invalid username or password"}), 401
    token = jwt.encode(
        {
            "username": user["username"],
            "exp": datetime.now(timezone.utc) + timedelta(hours=24),
        },
        app.config["SECRET_KEY"],
    )
    return jsonify({"token": token})


@app.route("/chat", methods=["POST"])
@token_required
def chat(current_user):
    data = request.get_json()
    if not data or not data.get("message"):
        return jsonify({"message": "Missing message"}), 400

    user_input = data["message"]
    session_id = data.get("session_id")

    # Create new session if none provided
    if not session_id:
        session = {
            "user_id": current_user["username"],
            "created_at": datetime.now(timezone.utc),
            "messages": [],
        }
        result = sessions_collection.insert_one(session)
        session_id = str(result.inserted_id)

    # Get or create agent for this session
    agent = create_agent(session_id, data["location"])

    # Run the agent asynchronously
    result = asyncio.run(agent.run(task=user_input))

    # Store the message in session history
    sessions_collection.update_one(
        {"_id": ObjectId(session_id)},
        {
            "$push": {
                "messages": {
                    "$each": [
                        {
                            "role": "user",
                            "content": user_input,
                            "timestamp": datetime.now(timezone.utc),
                        },
                        {
                            "role": "assistant",
                            "content": result.messages[-1].content,
                            "timestamp": datetime.now(timezone.utc),
                        },
                    ]
                }
            }
        },
    )
    print(result.messages)
    return jsonify({"response": result.messages[-1].content, "session_id": session_id})


if __name__ == "__main__":
    app.run(debug=True)
