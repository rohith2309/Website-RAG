from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_aws import ChatBedrockConverse
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

def setup_rag_chain(vectorstore=None):
    """Build a grounded QA chain using the current crawl's vector store."""
    if vectorstore is None:
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vectorstore = FAISS.load_local(
            "./faiss_index",
            embeddings,
            allow_dangerous_deserialization=True,
        )
    
    llm = ChatBedrockConverse(
        model="amazon.nova-lite-v1:0",
        temperature=0,
        region_name='us-east-1',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    )
    
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 6, "fetch_k": 24, "lambda_mult": 0.6},
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Answer using only the supplied website excerpts. If the excerpts do not contain the answer, say that the crawled pages do not provide enough information. Do not guess or combine conflicting facts as if they were certain. Cite each factual claim with its source number, for example [1].

Website excerpts:
{context}"""),
        ("human", "{input}"),
    ])
    
    def format_docs(docs):
        sections = []
        for index, doc in enumerate(docs, start=1):
            title = doc.metadata.get("title") or "Untitled page"
            url = doc.metadata.get("url") or doc.metadata.get("source") or "unknown source"
            sections.append(
                f"[Source {index}: {title} | {url}]\n{doc.page_content}"
            )
        return "\n\n".join(sections)
    
    rag_chain = (
        RunnablePassthrough.assign(
            source_documents=(lambda values: values["input"]) | retriever,
        )
        .assign(context=lambda values: format_docs(values["source_documents"]))
        | RunnableParallel(
            answer=prompt | llm,
            sources=lambda values: values["source_documents"],
        )
    )
    return rag_chain