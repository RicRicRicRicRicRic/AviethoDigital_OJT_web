# train_model.py
import os
import re  # <-- make sure this is here and NOT overwritten later
from sentence_transformers import SentenceTransformer
import chromadb

# ---------- CONFIG ----------
CHUNK_SIZE = 1000          # max characters per chunk (section‑aware)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
DB_PATH = "./avietho_chroma"
LOCAL_DATA_DIR = "./data"
# ----------------------------

def chunk_text(text, max_chars=CHUNK_SIZE):
    """
    Split the master text into self-contained chunks.
    Each chunk is a complete section (heading + content).
    If a section exceeds max_chars, it is split further with the heading repeated.
    """
    # Import locally to avoid any accidental shadowing
    import re as _re
    raw_sections = _re.split(r'(?=^=== )', text, flags=_re.MULTILINE)
    sections = [s.strip() for s in raw_sections if s.strip()]

    chunks = []
    for section in sections:
        if len(section) <= max_chars:
            chunks.append(section)
        else:
            lines = section.split('\n', 1)
            heading = lines[0].strip()
            body = lines[1].strip() if len(lines) > 1 else ""

            paragraphs = body.split('\n\n')
            current_chunk = heading + "\n\n"
            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue
                if len(current_chunk) + len(para) + 2 > max_chars:
                    chunks.append(current_chunk.strip())
                    current_chunk = heading + "\n\n" + para + "\n\n"
                else:
                    current_chunk += para + "\n\n"
            if current_chunk.strip() != heading.strip():
                chunks.append(current_chunk.strip())
    return chunks

def load_local_text_files(directory):
    chunks = []
    if not os.path.isdir(directory):
        print(f"Local data directory '{directory}' not found – skipping.")
        return chunks
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            filepath = os.path.join(directory, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            file_chunks = chunk_text(text)
            for chunk in file_chunks:
                chunks.append((chunk, {"url": f"local:{filename}"}))
            print(f"Loaded {len(file_chunks)} chunks from {filename}")
    return chunks

def build_index():
    print("Building knowledge base from local text files...")
    all_chunks = []
    metadata = []
    local_data = load_local_text_files(LOCAL_DATA_DIR)
    for chunk_text_local, meta in local_data:
        all_chunks.append(chunk_text_local)
        metadata.append(meta)

    print(f"Total chunks: {len(all_chunks)}")
    if len(all_chunks) == 0:
        print("No data found. Please add .txt files to the './data' folder.")
        return

    print("Loading embedding model...")
    model = SentenceTransformer(EMBEDDING_MODEL)
    print("Embedding chunks...")
    embeddings = model.encode(all_chunks, show_progress_bar=True)

    print("Updating Chroma DB...")
    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_or_create_collection("avietho_pages")

    existing = collection.get()
    if existing['ids']:
        collection.delete(ids=existing['ids'])
        print(f"Deleted {len(existing['ids'])} old chunks.")

    batch_size = 100
    for i in range(0, len(all_chunks), batch_size):
        end = i + batch_size
        batch_docs = all_chunks[i:end]
        batch_embeddings = embeddings[i:end]
        batch_metas = metadata[i:end]
        batch_len = len(batch_docs)

        collection.add(
            ids=[f"chunk_{i + j}" for j in range(batch_len)],
            documents=batch_docs,
            embeddings=batch_embeddings.tolist(),
            metadatas=batch_metas,
        )
    print("Knowledge base built successfully!")

if __name__ == "__main__":
    build_index()