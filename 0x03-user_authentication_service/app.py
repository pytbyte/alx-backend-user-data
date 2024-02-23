#!/usr/bin/env python3
"""Authentication feature for Flask app.
"""
from flask import Flask, abort, jsonify, redirect, request

from auth import Auth

app = Flask(__name__)
AUTH = Auth()


@app.route("/", methods=["GET"], strict_slashes=False)
def index() -> str:
    """ Home page.
    """
    return jsonify({"message": "Bienvenue"})


@app.route("/users", methods=["POST"], strict_slashes=False)
def users() -> str:
    """Creates a user
    Return:
        - created user.
    """
    data = request.form()
    email = data['email']
    password = data['password']

    try:
        AUTH.register_user(email, password)
        return jsonify({"email": email, "message": "user created"})
    except ValueError:
        return jsonify({"message": "email already registered"}), 400


@app.route("/sessions", methods=["POST"], strict_slashes=False)
def login() -> str:
    """initiate session
    Return:
        - logged in user
    """
    data = request.form()
    email = data['email']
    password = data['password']

    if (AUTH.valid_login(email, password)):
        session_id = AUTH.create_session(email)
        response = jsonify({"email": email, "message": "logged in"})
        response.set_cookie("session_id", session_id)
        return response
    else:
        abort(401)


@app.route("/sessions", methods=["DELETE"], strict_slashes=False)
def logout() -> str:
    """end user session
    Return:
        - end session redirect home
    """
    session_id = request.cookies.get("session_id")
    current_user = AUTH.get_user_from_session_id(session_id)
    if current_user:
        AUTH.destroy_session(current_user.id)
        return redirect("/")
    else:
        abort(403)


@app.route("/profile", methods=["GET"], strict_slashes=False)
def profile() -> str:
    """Retrieves a user's profile
    Return:
        - user's emails as payload
    """
    session_id = request.cookies.get("session_id")
    user = AUTH.get_user_from_session_id(session_id)
    if user:
        return jsonify({"email": user.email}), 200
    else:
        abort(403)


@app.route("/reset_password", methods=["POST"], strict_slashes=False)
def get_reset_password_token() -> str:
    """Creates a user's reset password token
    Return:
        - user's email and reset token
    """
    data = request.form()
    email = data['email']
    try:
        reset_token = AUTH.get_reset_password_token(email)
        return jsonify({"email": email, "reset_token": reset_token})
    except ValueError:
        abort(403)


@app.route("/reset_password", methods=["PUT"], strict_slashes=False)
def update() -> str:
    """password update
    Return:
        - user's email and messsage as payload
    """
    data = request.form()
    email = data['email']
    new_password = data['new_password']
    reset_token = request.form.get("reset_token")

    try:
        AUTH.update_password(reset_token, new_password)
        return jsonify({"email": email, "message": "Password updated"})
    except ValueError:
        abort(403)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")
