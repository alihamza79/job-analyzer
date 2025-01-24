from config import GROQ_API_KEY
from job_scraper import scrape_job_post
from ui import setup_ui, sidebar_inputs, display_results
from video_processor import VideoProcessor
from rag_pipeline import RAGPipeline
from langchain.docstore.document import Document
import streamlit as st

def main():
    setup_ui()
    vp = VideoProcessor()
    rag = RAGPipeline()
    
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

                # Create Knowledge Base
                st.write("🧠 Building Context-Aware Database...")
                retriever = rag.create_knowledge_base(docs)

                # Generate Analysis
                st.write("🤖 Synthesizing Strategic Insights...")
                analysis_prompt = "Analyze both job post and video transcript comprehensively" if sources["video"] else "Analyze the job post comprehensively"
                analysis = rag.generate_response(analysis_prompt, retriever)
                
                status.update(label="Analysis Complete!", state="complete")

                # Generate Proposal
                proposal = rag.generate_proposal(analysis["answer"], retriever)
                
            display_results(analysis, proposal, sources)

        except Exception as e:
            st.error(f"Analysis Failed: {str(e)}")
            st.error("Please check:\n1. Valid API Key\n2. Working Job Post URL")

if __name__ == "__main__":
    if not GROQ_API_KEY:
        st.error("GROQ_API_KEY missing in .env")
    else:
        main()