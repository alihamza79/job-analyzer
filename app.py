# File: app.py
# Main application file for Upwork Job Analyzer Pro

from config import GROQ_API_KEY
from job_scraper import scrape_job_post
from ui import setup_ui, sidebar_inputs, display_results
from video_processor import VideoProcessor
# from rag_pipeline import RAGPipeline  # Commented out
from langchain.docstore.document import Document
import streamlit as st

def main():
    setup_ui()
    vp = VideoProcessor()
    # rag = RAGPipeline()  # Commented out
    
    job_url, video_input, uploaded_file, analyze_btn = sidebar_inputs()

    if analyze_btn:
        if not job_url:
            st.error("Please provide a job posting URL to analyze.")
            return
            
        try:
            with st.status("Deep Analysis in Progress...", expanded=True) as status:
                docs = []
                sources = {"job": "", "video": ""}

                # Process Job Post
                st.write("🔍 Deep Scanning Job Post...")
                job_text = scrape_job_post(job_url)
                sources["job"] = job_text
                docs.append(Document(page_content=job_text, 
                                   metadata={"source": "job_post"}))

                # Process Video
                if video_input or uploaded_file:
                    st.write("🎬 Frame-by-Frame Video Analysis...")
                    video_source = video_input or uploaded_file
                    try:
                        video_text = vp.transcribe_video(video_source)
                        sources["video"] = video_text
                        docs.append(Document(page_content=video_text, 
                                          metadata={"source": "video"}))
                    except Exception as video_error:
                        st.warning(f"Video processing failed: {str(video_error)}")

                # Commented out RAG pipeline
                # st.write("🧠 Building Context-Aware Database...")
                # retriever = rag.create_knowledge_base(docs)
                # analysis = rag.generate_response(analysis_prompt, retriever)
                # proposal = rag.generate_proposal(analysis["answer"], retriever)
                
                status.update(label="Scraping Complete!", state="complete")
                
                # Dummy data for UI compatibility
                analysis = {"answer": "## LLM Analysis Disabled\n*Scraping development mode*"}
                proposal = "Proposal generation currently disabled"

            display_results(analysis, proposal, sources)

        except Exception as e:
            st.error(f"Scraping Failed: {str(e)}")
            st.error("Please check:\n1. Valid Job Post URL\n2. Network Connection")

if __name__ == "__main__":
    if not GROQ_API_KEY:
        st.error("GROQ_API_KEY missing in .env")
    else:
        main()