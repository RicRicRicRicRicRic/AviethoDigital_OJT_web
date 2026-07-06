# train_model.py
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

# ---------- CONFIG ----------
SITEMAP_URLS = [
    "https://aviethodigital.com/",
    "https://marketing.aviethodigital.com/",
]
CHUNK_SIZE = 500   # characters per chunk
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # free, small, fast
DB_PATH = "./avietho_chroma"
LOCAL_DATA_DIR = "./data" 
# ----------------------------

def get_all_links(base_url):
    """Crawl a site and return all internal page URLs (simple BFS)."""
    visited = set()
    to_visit = {base_url}
    domain = urlparse(base_url).netloc

    while to_visit:
        url = to_visit.pop()
        if url in visited:
            continue
        visited.add(url)
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            for a in soup.find_all("a", href=True):
                full_url = urljoin(url, a["href"])
                # Only keep URLs from the same domain
                if urlparse(full_url).netloc == domain and full_url not in visited:
                    to_visit.add(full_url)
            time.sleep(0.2)  # be polite
        except Exception as e:
            print(f"Skipping {url}: {e}")
    return visited

def extract_text(url):
    """Extract visible text from a page."""
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        # Remove script & style elements
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        # Get text
        text = soup.get_text(separator="\n", strip=True)
        return text
    except Exception as e:
        print(f"Failed to extract {url}: {e}")
        return ""

def chunk_text(text, size=CHUNK_SIZE):
    """Split text into overlapping chunks."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), size // 2):  # 50% overlap
        chunk = " ".join(words[i:i + size])
        if len(chunk) > 50:  # ignore tiny chunks
            chunks.append(chunk)
    return chunks

def build_index():
    print("Crawling websites...")
    all_links = set()
    for base in SITEMAP_URLS:
        links = get_all_links(base)
        all_links.update(links)
    print(f"Found {len(all_links)} pages.")

    # Extract text and chunk
    all_chunks = []
    metadata = []
    for url in all_links:
        print(f"Processing: {url}")
        text = extract_text(url)
        if text:
            chunks = chunk_text(text)
            all_chunks.extend(chunks)
            metadata.extend([{"url": url}] * len(chunks))
            
    # ---- Load local text files ----
    local_chunks_with_meta = load_local_text_files(LOCAL_DATA_DIR)
    for chunk_text_local, meta in local_chunks_with_meta:
        all_chunks.append(chunk_text_local)
        metadata.append(meta)

    print(f"Total chunks: {len(all_chunks)}")

    # Create embeddings
    print("Loading embedding model...")
    model = SentenceTransformer(EMBEDDING_MODEL)
    print("Embedding chunks...")
    embeddings = model.encode(all_chunks, show_progress_bar=True)

    # Store in Chroma – replace existing data
    print("Updating Chroma DB...")
    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_or_create_collection("avietho_pages")

    # ---- Delete all old data ----
    existing = collection.get()   # get all current IDs
    if existing['ids']:
        collection.delete(ids=existing['ids'])
        print(f"Deleted {len(existing['ids'])} old chunks.")
    # ---------------------------


    # Add new data in batches
    batch_size = 100
    for i in range(0, len(all_chunks), batch_size):
        end = i + batch_size
        # Get the actual slices
        batch_docs = all_chunks[i:end]
        batch_embeddings = embeddings[i:end]
        batch_metas = metadata[i:end]
        
        # Number of items in this batch
        batch_len = len(batch_docs)
        
        collection.add(
            ids=[f"chunk_{i + j}" for j in range(batch_len)],   # correct count
            documents=batch_docs,
            embeddings=batch_embeddings.tolist(),
            metadatas=batch_metas,
        )


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
            # Add metadata indicating the source file
            for chunk in file_chunks:
                chunks.append((chunk, {"url": f"local:{filename}"}))
            print(f"Loaded {len(file_chunks)} chunks from {filename}")
    return chunks

if __name__ == "__main__":
    build_index()