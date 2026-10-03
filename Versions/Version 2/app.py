import streamlit as st
import asyncio

from crawler import crawl_website
from utils.RAGchain import setup_rag_chain
from utils.Chunker import chunk_documents
from utils.RankUtils import score_url
from utils.sitemapPraser import get_sitemap_urls



# ============================================================================
# STREAMLIT UI
# ============================================================================

# Configure Streamlit page
st.set_page_config(page_title="Web Crawl RAG V1 prototype", layout="wide")
st.title("WEBSITE RAG PROTOTYPE")

# Initialize session state
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "rag_chain" not in st.session_state:
    st.session_state.rag_chain = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "kb_created" not in st.session_state:
    st.session_state.kb_created = False

# Sidebar for setup
with st.sidebar:
    st.header("⚙️ Setup Knowledge Base")
    
    max_pages = st.slider("Max pages to crawl :", min_value=5, max_value=20, value=10)
    depth = st.slider("Max depth to crawl:", min_value=1, max_value=5, value=3)
    url = st.text_input("Enter URL to crawl:", placeholder="https://www.wilsonart.com")
   
    
    if st.button("🔄 Create Knowledge Base", use_container_width=True):
        if url :
            st.info("Starting knowledge base creation... This may take a few minutes.")
            st.info("working on parsing the sitemap url")
            urls = get_sitemap_urls(url)
            st.info(f"Found {len(urls)} URLs in the sitemap. Scoring and selecting top pages...")
            scored_urls = [s_url for s_url in urls if score_url(s_url)>=0]
            st.info(f"Selected {len(scored_urls)} top pages based on scoring. Starting crawl...")
            try:
                # Step 1: Crawl
                st.status("Crawling website...", state="running")
                with st.spinner("Crawling..."):
                    raw_docs = asyncio.run(crawl_website(scored_urls))
                    st.write(f"Crawled {len(raw_docs)} successful pages.")
                st.status("Crawling website...", state="complete")
                
                # Step 2: Chunk
                st.status("Processing documents...", state="running")
                with st.spinner("Chunking and embedding..."):
                    vectorstore = chunk_documents(raw_docs)
                st.status("Processing documents...", state="complete")
                
                # Step 3: Setup RAG chain
                st.status("Setting up QA chain...", state="running")
                with st.spinner("Initializing retriever..."):
                    rag_chain = setup_rag_chain(vectorstore)
                   
                st.status("Setting up QA chain...", state="complete")
                
                st.session_state.vectorstore = vectorstore
                st.session_state.rag_chain = rag_chain
                st.session_state.chat_history = []
                st.session_state.kb_created = True
                st.success("✅ Knowledge Base Ready! Start asking questions below.")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("Please enter  URL ")

# Main chat interface
if st.session_state.kb_created:
    st.header("💬 Ask Questions")
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for i, message in enumerate(st.session_state.chat_history):
            if message["role"] == "user":
                st.chat_message("user").write(message["content"])
            else:
                st.chat_message("assistant").write(message["content"])
                for source in message.get("sources", []):
                    st.caption(f"[{source['index']}] [{source['title']}]({source['url']})")
    
    # Input for new question
    user_input = st.chat_input("Ask a question about the content...")
    
    if user_input:
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)
        
        # Get response from RAG chain
        try:
            with st.spinner("Thinking..."):
                response = st.session_state.rag_chain.invoke({"input": user_input})
                answer_message = response["answer"]
                answer = answer_message.content if hasattr(answer_message, "content") else str(answer_message)
                usage = answer_message.usage_metadata or {}
                sources = []
                for index, document in enumerate(response["sources"], start=1):
                    source_url = document.metadata.get("url") or document.metadata.get("source")
                    if source_url:
                        sources.append({
                            "index": index,
                            "title": document.metadata.get("title") or source_url,
                            "url": source_url,
                        })
                
            # Add assistant response to history
            st.session_state.chat_history.append({"role": "assistant", "content": answer, "sources": sources})
            st.chat_message("assistant").write(answer)
            for source in sources:
                st.caption(f"[{source['index']}] [{source['title']}]({source['url']})")
            st.info(
                    f"Tokens: {usage.get('total_tokens', 'N/A')} "
                    f"(input: {usage.get('input_tokens', 'N/A')}, "
                    f"output: {usage.get('output_tokens', 'N/A')})"
                )  
            
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
else:
    st.info("👈 Please set up a knowledge base first using the sidebar!")
