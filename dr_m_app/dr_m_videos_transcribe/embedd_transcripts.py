import os
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from pathlib import Path
from langchain_core.documents import Document
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate

load_dotenv()


OPENAI_API_BASE =os.getenv('OPENAI_API_BASE')
OPENAI_API_KEY=os.getenv('OPENAI_API_KEY')

def load_transcripts(folder_path)->list[Document]:
    documents = []
    for transcript in Path(folder_path).iterdir():
        if transcript.suffix==".txt":
            loader = TextLoader(transcript, encoding="utf-8")
            docs = loader.load()
            for doc in docs:
                doc.metadata["source"] = transcript.stem
            documents.extend(docs)
    return documents
def split_documents(documents:Document)->list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " "]
    )
    return splitter.split_documents(documents)


def create_vectorstore(chunks:list[Document]):
    # embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    embeddings=HuggingFaceEmbeddings(
        model_name="thenlper/gte-base"
    )
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="./chroma_store"
    )
    vectorstore.persist()
    return vectorstore

def get_metadata_content(vectorstore:VectorStoreRetriever,querry:str):
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 2})
    docs=retriever.invoke(querry)
    context = "\n\n".join(
        f"[Video ID: {doc.metadata.get('source', 'unknown')}] Content: {doc.page_content}"
        for doc in docs
    )
    video_ids = list({doc.metadata.get("source", "unknown") for doc in docs})
    return {"context": context, "question": querry, "video_ids": video_ids}



def get_answer(vectorstore:VectorStoreRetriever,question:str)->Runnable: 

    prompt = ChatPromptTemplate.from_template(
    """
   You are an assistant for question-answering tasks.
    Use the following pieces of retrieved context to answer the question. 
    If the context doesn't make sense with respect to the quesion, just say "I don't know" else use
    three sentences maximum and keep the answer concise.

    Context:
    {context}

    Question:
    {question}
    """)  

    context_info=get_metadata_content(vectorstore,question)   
    input=    {
        "context": context_info['context'],
        "question": question,
    }

    llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY,base_url=OPENAI_API_BASE ,model="gpt-4", temperature=0.3)
    qa_chain = (
    prompt
    | llm
    | StrOutputParser()
    )
    answer=qa_chain.invoke(input)

    if ("I don't know".lower() or "context does not provide") in answer.lower():
        return {
            "answer": llm.invoke(question).content,
            "video_ids": "no video"
        }

    return {
            "answer": answer,
            "video_ids": context_info["video_ids"]
        }


