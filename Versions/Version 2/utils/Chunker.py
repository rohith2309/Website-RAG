
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_documents(docs):
    """Create a fresh vector store from crawled pages."""
    if not docs:
        raise ValueError("The crawl returned no usable pages to index.")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=900,
        chunk_overlap=150,
        separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""],
        add_start_index=True,
    )
    split_docs = text_splitter.split_documents(docs)
    if not split_docs:
        raise ValueError("The crawl returned no text long enough to index.")

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return FAISS.from_documents(split_docs, embeddings)