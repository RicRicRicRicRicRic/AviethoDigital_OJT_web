# app.py
import sys
import subprocess
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
from sentence_transformers import SentenceTransformer
import chromadb
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

# ---------- CONFIG ----------
DB_PATH = "./avietho_chroma"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
GOOGLE_API_KEY = "AIzaSyCSsvkFc3Uc6Lc7wXu_UIvoYHzTq1NW7QY"   # <-- put your real key
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
Answer:"""

    try:
        # Gemini expects a prompt (or a list of messages)
        response = model.generate_content(prompt)
        reply = response.text.strip()
    except Exception as e:
        reply = f"Error calling Gemini: {e}"

    return jsonify({"reply": reply})
    

if __name__ == '__main__':
    init_model()   # preload on startup (optional)
    app.run(debug=True, port=5000)