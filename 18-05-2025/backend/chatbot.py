from flask import Blueprint, jsonify, request, render_template
import random
import spacy

chatbot_bp = Blueprint('chatbot_bp', __name__)

# Load spaCy model
nlp = spacy.load("en_core_web_sm")



@chatbot_bp.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')


@chatbot_bp.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message").lower()
    doc = nlp(user_message)

    # Extract intents using simple keyword matching
    if any(token.lemma_ in ["hello", "hi", "hey"] for token in doc):
        response = random.choice(["Hello! How can I help you?", "Hey there!", "Hi! What's up?"])
    elif any(token.lemma_ in ["bye", "goodbye"] for token in doc):
        response = random.choice(["Goodbye! Have a great day!", "See you later!", "Take care!"])
    elif any(token.lemma_ in ["how", "be"] for token in doc) and "you" in user_message:
        response = random.choice(["I'm just a bot, but I'm doing great! How about you?", "I'm here to help you. How are you doing?"])
    elif any(token.lemma_ in ["thank", "thanks"] for token in doc):
        response = random.choice(["You're welcome!", "Happy to help!", "Anytime!"])
    else:
        response = "I'm not sure how to help with that, but I'm learning every day!"

    return jsonify({"reply": response})