"""Handle place searches with CAPTCHA in a Flask app."""

import asyncio
import logging
import os
import random
import secrets
from datetime import datetime
from functools import wraps

import nest_asyncio
from diskcache import Cache
from flask import Flask, jsonify, render_template, request

from main import helpmefind

nest_asyncio.apply()

app = Flask(__name__)
# Set a secret key for session management
app.secret_key = secrets.token_hex(16)

# Use disk-based cache for CAPTCHA storage instead of in-memory dictionary
captcha_cache = Cache("cache/captcha")

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

    # Store the challenge and answer with an ID in disk cache
    # Set expiration to 10 minutes (600 seconds)
    captcha_cache.set(
        captcha_id,
        {
            "challenge": challenge,
            "answer": answer,
            "created_at": datetime.now().isoformat(),
        },
        expire=600,
    )

    return captcha_id, challenge


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
        captcha_data = captcha_cache.get(captcha_id)
        if captcha_data is None:
            return jsonify({"message": "Invalid or expired CAPTCHA"}), 403

        # Check if the answer is correct
        correct_answer = captcha_data["answer"]

        # Remove the used CAPTCHA regardless of whether answer is correct
        captcha_cache.delete(captcha_id)

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

        res = asyncio.run(helpmefind(query=query, location=location))
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
