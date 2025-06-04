from functools import wraps
from flask import request, jsonify
import jwt
from db import users_collection
import os


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"message": "Token is missing!"}), 401
        try:
            token = token.split(" ")[1]
            data = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=["HS256"])
            current_user = users_collection.find_one({"username": data["username"]})
            if not current_user:
                return jsonify({"message": "Invalid token!"}), 401
        except Exception as e:
            return jsonify({"message": "Invalid token!"}), 401
        return f(current_user, *args, **kwargs)

    return decorated
