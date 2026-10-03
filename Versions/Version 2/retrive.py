from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_aws import ChatBedrockConverse

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import boto3
import os
from dotenv import load_dotenv
load_dotenv()

llm=ChatBedrockConverse(
    model="amazon.nova-lite-v1:0", 
    temperature=0, 
    region_name='us-east-1',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
       
    )
embeddings=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")  # Ensure this matches your embedding model
vectorstore=FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)



retriever = vectorstore.as_retriever(search_kwargs={"k": 3})



prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer the user's question based only on the following context:\n\n{context}"),
    ("human", "{input}"),
])

# Assemble the chains using LCEL (LangChain Expression Language)
def format_docs(docs):
    return "\n\n".join([doc.page_content for doc in docs])

rag_chain = (
    RunnableParallel(
        context=(lambda x: x["input"]) | retriever | format_docs,
        input=RunnablePassthrough()
    )
    | prompt
    | llm
)

# Execute the pipeline
response = rag_chain.invoke({"input": "How do I configure the confidence threshold?"})
print(response.content)