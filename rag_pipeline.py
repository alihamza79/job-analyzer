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
        Please carefully analyze all provided documents and relevant data:

        CONTEXT:
        {context}

        QUERY:
        {input}

        Generate a concise analysis including:
        1. Key technical requirements
        2. Specific client needs or pain points
        3. Project or business goals
        4. Any deeper insights based on context

        If no video content is provided, do not mention it.
        Separate your findings with clear headings or bullet points.
        """)
        
        document_chain = create_stuff_documents_chain(llm, prompt)
        retrieval_chain = create_retrieval_chain(retriever, document_chain)
        return retrieval_chain.invoke({"input": query})
    
    def generate_proposal(self, analysis_result, retriever, template=None, has_video=False):
        """
        Create a proposal either using the default prompt or a user-provided template.
        The user-provided template must contain '{analysis}' to embed the analysis results.
        If has_video=False, do not mention or assume video references.
        """
        llm = ChatGroq(
            temperature=0.3,
            model_name="llama3-70b-8192"
        )

        # Build a more human-sounding default prompt dynamically
        base_prompt = """
        You are an experienced freelancer. Write a clear, client-focused proposal:
        
        ANALYSIS: {analysis}

        GUIDELINES:
        - Start with a greeting that acknowledges the client’s specific project or problem.
        - Highlight the main requirements from the job posting.
        - {video_line}
        - Outline how you plan to address the needs step by step.
        - Mention relevant experience you have for these requirements.
        - Suggest next steps or a clear call to action.
        - Keep the style professional but friendly, focusing on real value.

        IMPORTANT:
        - If there is no video, avoid any reference to it or a transcript.
        - Try to sound natural and conversational, not AI-generated.
        """

        if has_video:
            video_line = "If applicable, briefly mention insights gained from the video."
        else:
            video_line = "If no video is mentioned, skip any reference to it."

        # Insert the correct line for referencing video or not
        final_prompt = base_prompt.replace("{video_line}", video_line)

        if template and "{analysis}" in template:
            # If user provided a custom template with {analysis}, we use that
            prompt = ChatPromptTemplate.from_template(template)
        else:
            # Use the dynamic default prompt
            prompt = ChatPromptTemplate.from_template(final_prompt)
        
        chain = prompt | llm | StrOutputParser()
        return chain.invoke({"analysis": analysis_result})
