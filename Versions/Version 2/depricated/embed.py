# embed_web_kb.py
import json
import os
import re
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions

load_dotenv()

CHROMA_DB_KEY = os.getenv('CHROMA_DB')
ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name='all-MiniLM-L6-v2'
)

def semantic_chunk(text: str, max_chars: int = 800) -> list[str]:
    """
    Split by markdown headings first, then by paragraph.
    Respects semantic boundaries rather than cutting mid-sentence.
    """
    # Split on markdown headings (## or ###)
    sections = re.split(r'\n(?=#{1,3} )', text)
    
    chunks = []
    for section in sections:
        if len(section) <= max_chars:
            if section.strip():
                chunks.append(section.strip())
        else:
            # Section too long — split by paragraph
            paragraphs = section.split('\n\n')
            current = ""
            for para in paragraphs:
                if len(current) + len(para) <= max_chars:
                    current += para + "\n\n"
                else:
                    if current.strip():
                        chunks.append(current.strip())
                    current = para + "\n\n"
            if current.strip():
                chunks.append(current.strip())
    
    return [c for c in chunks if len(c) > 50]  # filter tiny fragments


def load_and_embed(jsonl_path: str, collection_name: str):
    client = chromadb.CloudClient(
        api_key=CHROMA_DB_KEY,
        tenant='e5b49720-5aa8-4df7-bd60-0e8ea24aeda7',
        database='ticketing',
    )

    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=ef,
        metadata={'hnsw:space': 'cosine'}
    )

    documents, metadatas, ids = [], [], []
    doc_index = 0

    with open(jsonl_path, 'r') as f:
        for line in f:
            page = json.loads(line.strip())
            
            url     = page.get('url', '')
            content = page.get('content', '')
            score   = page.get('score', 0.0)

            # Skip low-relevance pages
            if score < 0.5:
                continue

            chunks = semantic_chunk(content)

            for i, chunk in enumerate(chunks):
                documents.append(chunk)
                metadatas.append({
                    "url"       : url,
                    "chunk_id"  : i,
                    "page_score": score,
                    "source"    : "web_crawl"
                })
                ids.append(f"web_{doc_index}_{i}")
            
            doc_index += 1

    # Batch upsert (ChromaDB handles deduplication)
    if documents:
        collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Embedded {len(documents)} chunks from {doc_index} pages")


if __name__ == "__main__":
    load_and_embed("./KB/auth_knowledge.jsonl", "WebKB-collection")