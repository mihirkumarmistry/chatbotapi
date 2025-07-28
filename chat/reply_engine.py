import random
import re
import requests
from chat.hotel_policy import HOTEL_POLICY
from chatbotapi.settings import AI_API

responses = {
    "greetings": [
        "Welcome to Grand Stay Hotel! How can I assist you with your booking today?",
        "Hello there! I'm here to help you with any hotel-related questions. What would you like to know?",
        "Hi! Ready to check in to great service. How may I assist you today?",
        "Greetings from Grand Stay Hotel. Let me know how I can help you with reservations or policies!",
    ],
    "help": [
        "I can help you with hotel booking questions like:\n• Cancellation policies\n• Check-in/check-out times\n• Parking and pet rules\n• Room occupancy\n• Payment and deposits\n\nWhat would you like to ask?",
        "I'm here to assist you with anything related to your stay. Do you need help with check-in details, cancellation, or amenities?",
        "I can provide answers about our hotel's policies, rates, services, and more. Just ask!",
    ],
    "general": [
        "That's a great question! Could you tell me more so I can give you the best information?",
        "I'm happy to help. Could you clarify your question or let me know which part of your stay you're asking about?",
        "I’d love to assist! Are you asking about room features, policies, or something else?",
        "To help you better, could you please provide a bit more detail on your query?",
    ],
    "thanks": [
        "You're very welcome! If you need help with anything else about your stay or booking, just ask.",
        "Glad I could help! Have a wonderful stay at Grand Stay Hotel!",
        "You're welcome! Let me know if you have more questions about your reservation or hotel services.",
        "Happy to assist! Don't hesitate to ask more about our hotel policies or amenities.",
    ],
}

generate_ai = f"{AI_API}api/generate"
ask_ai = f"{AI_API}api/ask"


def get_random_response(category):
    try:
        return random.choice(responses[category])
    except Exception:
        return "Oops! I don't know how to respond to that yet."


def generate_reply(message: str) -> dict:
    message = message.lower()

    # General replies
    if re.search(r"\b(hello|hi|hey|greetings|good morning|good evening)\b", message):
        return {
            "type": "general",
            "message": get_random_response("greetings"),
            "source": "rule-based",
        }
    elif re.search(r"\b(help|assist|support)\b", message):
        return {
            "type": "general",
            "message": get_random_response("help"),
            "source": "rule-based",
        }
    elif re.search(r"\b(thank|thanks|appreciate)\b", message):
        return {
            "type": "general",
            "message": get_random_response("thanks"),
            "source": "rule-based",
        }
    elif "how are you" in message:
        return {
            "type": "general",
            "message": "I'm doing great! How about you?",
            "source": "rule-based",
        }
    elif "what is your name" in message:
        return {
            "type": "general",
            "message": "I'm your AI Assistant! What can I do for you?",
            "source": "rule-based",
        }
    elif "bye" in message:
        return {
            "type": "general",
            "message": "See you later! 👋",
            "source": "rule-based",
        }

    # Else, fallback to AI reply
    return handle_ai_reply(message)


def handle_ai_reply(question: str) -> dict:
    """Uses the AI model to answer the user's question based on static hotel policy"""
    prompt = f"""You are a friendly hotel assistant. Answer the question naturally and helpfully as if you're chatting with a guest. Use the policy below for facts, but do not mention or reference the document or the policy in your answer.
        Hotel Policy: {HOTEL_POLICY}
        Guest Question: {question}"""

    try:
        response = requests.post(
            generate_ai,
            json={"model": "mistral", "prompt": prompt, "stream": False}, 
        )
        ai_reply = response.json().get("response", "").strip()
        return {
            "type": "ai",
            "message": ai_reply or "Sorry, I couldn't find an answer to that.",
            "source": "static-policy",
        }
    except Exception as e:
        return {
            "type": "ai",
            "message": f"⚠️ AI model error: {str(e)}",
            "source": "error",
        }
