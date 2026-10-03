import json
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
def load_crawl4ai_jsonl(file_path: str):
    docs = []
    with open(file_path, 'r') as f:
        for line in f:
            data = json.loads(line)
            # Map the crawl4ai output to LangChain Documents
            # Hint: verify the exact keys in your JSONL export
            docs.append(Document(
                page_content=data.get("content", ""),
                metadata={
                    "url": data.get("url", ""), 
                    "score": data.get("score", 0)
                }
            ))
    return docs

# Load and chunk the documents
raw_docs = load_crawl4ai_jsonl("./KB/auth_knowledge.jsonl")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
split_docs = text_splitter.split_documents(raw_docs)


from langchain_community.vectorstores import FAISS
from langchain_aws import BedrockEmbeddings

# Initialize your embedding model
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")  # Example model, replace with BedrockEmbeddings if using AWS Bedrock

# Ingest into FAISS
vectorstore = FAISS.from_documents(split_docs, embeddings)

# Hint: Save locally so you don't re-embed the same KB on every run
vectorstore.save_local("faiss_index")
# To load later: FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)