# app.py
import sys
import subprocess
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS
from sentence_transformers import SentenceTransformer
import chromadb
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

app = Flask(__name__)
CORS(app)

# ---------- CONFIG ----------
DB_PATH = "./avietho_chroma"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-3.5-flash')   # fast and free tier friendly
# ----------------------------

# Global variables for the model and DB (lazy loaded)
embedding_model = None
chroma_client = None
collection = None

def init_model():
    global embedding_model, chroma_client, collection
    if embedding_model is None:
        embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        chroma_client = chromadb.PersistentClient(path=DB_PATH)
        collection = chroma_client.get_or_create_collection("avietho_pages")

# ----- Training endpoint (unchanged) -----
training_status = {"running": False, "message": "Not started"}

def run_training():
    global training_status, collection
    training_status["running"] = True
    training_status["message"] = "Training in progress..."
    try:
        subprocess.run([sys.executable, "train_model.py"], check=True)
        training_status["message"] = "Training completed successfully."
        # Reload the collection to pick up new data
        if chroma_client:
            collection = chroma_client.get_collection("avietho_pages")
    except subprocess.CalledProcessError as e:
        training_status["message"] = f"Training failed: {e}"
    finally:
        training_status["running"] = False

@app.route('/train', methods=['POST'])
def start_training():
    if training_status["running"]:
        return jsonify({"error": "Training already running"}), 409
    thread = threading.Thread(target=run_training)
    thread.start()
    return jsonify({"status": "Training started"}), 202

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify(training_status)

# ----- Chat endpoint -----
@app.route('/chat', methods=['POST'])
def chat():
    init_model()
    data = request.get_json()
    user_message = data.get('message', '')
    if not user_message:
        return jsonify({"reply": "Please provide a message."}), 400

    # 1. Embed the question
    question_embedding = embedding_model.encode([user_message])[0]

    # 2. Retrieve top 3 relevant chunks
    results = collection.query(
        query_embeddings=[question_embedding.tolist()],
        n_results=3,
        include=["documents", "metadatas"]
    )
    contexts = results['documents'][0]  # list of strings

    # 3. Build a prompt with the context
    context_text = "\n\n".join(contexts)
    prompt = f"""You are a helpful assistant that answers questions about Avietho, a digital marketing company.
    Use only the following context to answer the question. If you can't find the answer, say you don't know.

    Context:
    {context_text}

    Question: {user_message}

    Instructions:
    - Answer in clear, well-structured English.
    - Use proper paragraphs and, if helpful, bullet points.
    - Keep the tone professional and friendly.
    - Do **not** use any Markdown formatting (like bold `**text**` or italics `*text*`). Just plain text.
    - Preserve any list formatting from the context (like bullet points or numbered items).

    Answer:"""

    try:
        # Gemini expects a prompt (or a list of messages)
        response = model.generate_content(prompt)
        reply = response.text.strip()

        uncertainty_phrases = [
            "i don't know",
            "i do not know",
            "i couldn't find",
            "i cannot answer",
            "sorry",
            "unable to provide",
            "no information",
        ]
        if any(phrase in reply.lower() for phrase in uncertainty_phrases):
            reply += (
                "\n\n📧 For further inquiries, please email us at "
                "info@aviethodigital.com or message us on Messenger: "
                "https://m.me/AviethoDigital"
            )

    except Exception as e:
        reply = f"Error calling Gemini: {e}"

    return jsonify({"reply": reply})
    

if __name__ == '__main__':
    init_model()   # preload on startup (optional)
    app.run(debug=True, port=5000)