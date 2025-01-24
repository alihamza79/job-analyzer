# File: rag_pipeline.py
# Handles RAG (Retrieval Augmented Generation) pipeline for analysis

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.output_parsers import StrOutputParser

class RAGPipeline:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
    def create_knowledge_base(self, documents):
        chunks = self.text_splitter.split_documents(documents)
        vectorstore = FAISS.from_documents(
            documents=chunks,
            embedding=self.embeddings
        )
        return vectorstore.as_retriever(search_kwargs={"k": 5})
    
    def generate_response(self, query, retriever):
        llm = ChatGroq(
            temperature=0.7,
            model_name="llama3-70b-8192"
        )
        
        prompt = ChatPromptTemplate.from_template("""
        Analyze the job post and video transcript with surgical precision:
        
        CONTEXT:
        {context}
        
        QUERY:
        {input}
        
        Create comprehensive analysis with:
        1. EXACT technical requirements from both sources
        2. SPECIFIC client pain points mentioned
        3. PROJECT GOALS extracted verbatim
        4. CLIENT'S DEEP NEEDS inferred from context
        5. ACTIONABLE SOLUTION COMPONENTS
        
        Structure analysis with clear section headers. Use bullet points for requirements.
        """)
        
        document_chain = create_stuff_documents_chain(llm, prompt)
        retrieval_chain = create_retrieval_chain(retriever, document_chain)
        return retrieval_chain.invoke({"input": query})
    
    def generate_proposal(self, analysis_result, retriever):
        llm = ChatGroq(
            temperature=0.3,
            model_name="llama3-70b-8192"
        )
        
        prompt = ChatPromptTemplate.from_template("""
        Create hyper-personalized proposal using EXACT details:
        
        ANALYSIS: {analysis}
        
        Structure:
        - Open with SPECIFIC project understanding
        - Address ALL stated requirements from job post
        - Reference SPECIFIC video points
        - Timeline with phase details
        - Relevant experience MATCHING exact needs
        - Clear next steps
        
        Use client's terminology from sources. Include 5 SPECIFIC examples.
        """)
        
        chain = prompt | llm | StrOutputParser()
        return chain.invoke({"analysis": analysis_result})