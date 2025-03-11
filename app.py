"""Handle place searches with CAPTCHA in a Flask app."""

import logging
import random
import secrets
from datetime import datetime
from functools import wraps
import os
from flask import Flask, jsonify, render_template, request

from main import helpmefind

app = Flask(__name__)
# Set a secret key for session management
app.secret_key = secrets.token_hex(16)

# Dictionary to store temporary CAPTCHA challenges and their answers
captcha_store = {}

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


# Generate a CAPTCHA challenge
def generate_captcha():
    """Generate a CAPTCHA challenge."""
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    operator = random.choice(["+", "-", "*"])

    if operator == "+":
        answer = num1 + num2
    elif operator == "-":
        answer = num1 - num2
    else:  # '*'
        answer = num1 * num2

    challenge = f"{num1} {operator} {num2}"
    captcha_id = secrets.token_hex(8)

    # Store the challenge and answer with an ID
    captcha_store[captcha_id] = {
        "challenge": challenge,
        "answer": answer,
        "created_at": datetime.now(),
    }

    # Clean up old captchas periodically
    clean_old_captchas()

    return captcha_id, challenge


# Clean up captchas older than 10 minutes
def clean_old_captchas():
    """Clean up captchas older than 10 minutes."""
    now = datetime.now()
    expired_ids = [
        captcha_id
        for captcha_id, data in captcha_store.items()
        if (now - data["created_at"]).total_seconds() > 600
    ]
    for captcha_id in expired_ids:
        captcha_store.pop(captcha_id, None)


# Endpoint to get a new CAPTCHA
@app.route("/get-captcha", methods=["GET"])
def get_captcha():
    """Endpoint to get a new CAPTCHA."""
    captcha_id, challenge = generate_captcha()
    return jsonify({"captcha_id": captcha_id, "challenge": challenge})


# Middleware to check CAPTCHA validation
def require_captcha(f):
    """Check CAPTCHA validation middleware."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        """The decorated function with CAPTCHA validation."""
        # Get CAPTCHA ID and user's answer from request
        captcha_id = request.json.get("captcha_id")
        user_answer = request.json.get("captcha_answer")

        # Check if captcha_id exists and user provided an answer
        if not captcha_id or user_answer is None:
            return jsonify({"message": "CAPTCHA validation required"}), 403

        # Check if the captcha_id is valid
        if captcha_id not in captcha_store:
            return jsonify({"message": "Invalid or expired CAPTCHA"}), 403

        # Check if the answer is correct
        correct_answer = captcha_store[captcha_id]["answer"]

        # Remove the used CAPTCHA regardless of whether answer is correct
        captcha_store.pop(captcha_id, None)

        if user_answer != correct_answer:
            return jsonify({"message": "Incorrect CAPTCHA answer"}), 403

        # If we get here, CAPTCHA is valid, proceed with the actual function
        return f(*args, **kwargs)

    return decorated_function


@app.route("/")
def index():
    """Render the index page."""
    return render_template("index.html")


@app.route("/process", methods=["POST"])
@require_captcha
def process():
    """Process the place search request."""
    try:
        data = request.json
        query = data.get("query")
        location = data.get("location")

        # Validate input
        if not query or not location:
            return jsonify({"message": "Missing required parameters"}), 400

        res = helpmefind(query=query, location=location)
        return jsonify(res.dump())
    except Exception:
        # Log the exception
        logger.error("Exception occurred", exc_info=True)
        return (
            jsonify({"error": "Oops! Something went wrong. Please try again later."}),
            500,
        )


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() in ["true", "1"]
    app.run(host="0.0.0.0", debug=debug_mode)
