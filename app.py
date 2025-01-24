import streamlit as st
import os
import requests
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from video_processor import VideoProcessor
from rag_pipeline import RAGPipeline
from langchain.docstore.document import Document

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def scrape_job_post(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract job title
        title = soup.find('h1').get_text(strip=True) if soup.find('h1') else "Job Title Not Found"
        
        # Extract main content using structural patterns
        main_content = soup.find('div', {'role': 'main'}) or \
                     soup.find('main') or \
                     soup.find('div', class_=lambda x: x and 'description' in x.lower()) or \
                     soup.find('article')
        
        # Extract content sections
        description_sections = []
        if main_content:
            for element in main_content.find_all(['h2', 'h3', 'p', 'ul', 'ol']):
                if element.name in ['h2', 'h3']:
                    description_sections.append(f"\n## {element.get_text(strip=True)}")
                elif element.name in ['ul', 'ol']:
                    items = [f"- {li.get_text(strip=True)}" for li in element.find_all('li')]
                    description_sections.append('\n'.join(items))
                else:
                    text = element.get_text(strip=True)
                    if text and len(text) > 30:  # Filter out short paragraphs
                        description_sections.append(text)

        # Extract metadata using regex patterns
        full_text = soup.get_text()
        metadata = {
            'budget': re.search(r'Budget:\s*(\$[\d,]+)', full_text),
            'duration': re.search(r'Duration:\s*([\w\s]+)', full_text),
            'experience': re.search(r'Experience Level:\s*([\w\s]+)', full_text)
        }
        
        # Format metadata
        formatted_metadata = "\n".join([
            f"- {key}: {val.group(1) if val else 'Not specified'}" 
            for key, val in metadata.items()
        ])

        # Extract skills using keyword proximity
        skills = []
        skills_header = soup.find(lambda tag: re.search(r'Skills|Requirements', tag.text, re.IGNORECASE))
        if skills_header:
            skills_container = skills_header.find_next(['ul', 'div'])
            if skills_container:
                skills = [li.get_text(strip=True) 
                         for li in skills_container.find_all('li')][:10]  # Limit to 10 skills

        return (
            f"JOB TITLE: {title}\n\n"
            f"DESCRIPTION:\n" + '\n'.join(description_sections) + "\n\n"
            
        )
    except Exception as e:
        return f"Job post scraping error: {str(e)}"

def main():
    st.set_page_config(
        page_title="Upwork AI Assistant",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🚀 Upwork Job Analyzer Pro")
    st.markdown("### AI-Powered Precision Proposal System")
    
    vp = VideoProcessor()
    rag = RAGPipeline()
    
    with st.sidebar:
        st.header("Job Inputs")
        job_url = st.text_input("Job Posting URL (Required)")
        st.markdown("---")
        st.markdown("### Optional Video Analysis")
        video_input = st.text_input("YouTube Video URL (Optional)") 
        uploaded_file = st.file_uploader("Upload Video (Optional)", 
                                       type=["mp4", "mov", "mp3"])
        analyze_btn = st.button("Analyze Job", type="primary")

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

                # Process Video only if provided
                if video_input or uploaded_file:
                    st.write("🎬 Frame-by-Frame Video Analysis...")
                    video_source = video_input or uploaded_file
                    try:
                        video_text = vp.transcribe_video(video_source)
                        sources["video"] = video_text
                        docs.append(Document(page_content=video_text, 
                                          metadata={"source": "video"}))
                    except Exception as video_error:
                        st.warning(f"Video processing failed: {str(video_error)}. Continuing with job post analysis only.")

                # Create Knowledge Base
                st.write("🧠 Building Context-Aware Database...")
                retriever = rag.create_knowledge_base(docs)

                # Adjust analysis prompt based on available sources
                analysis_prompt = "Analyze the job post comprehensively"
                if sources["video"]:
                    analysis_prompt = "Analyze both job post and video transcript comprehensively"

                # Generate Analysis
                st.write("🤖 Synthesizing Strategic Insights...")
                analysis = rag.generate_response(analysis_prompt, retriever)
                
                status.update(label="Analysis Complete!", state="complete")

            # Display Results
            st.subheader("🔬 Precision Analysis Report")
            st.markdown(analysis["answer"])

            # Proposal Generation
            st.markdown("---")
            st.subheader("📝 Laser-Targeted Proposal")
            
            proposal = rag.generate_proposal(analysis["answer"], retriever)
            
            tab1, tab2 = st.tabs(["Formatted View", "Plain Text"])
            with tab1:
                st.markdown(proposal)
            with tab2:
                clean_proposal = proposal.replace("**", "").replace("*", "")
                st.code(clean_proposal, language="text")
                if st.button("📋 Copy Proposal"):
                    st.session_state.proposal = clean_proposal
                    st.success("Proposal ready to copy!")

            # Detailed Sources
            with st.expander("🔍 Full Source Materials"):
                st.subheader("Complete Job Post Analysis")
                st.markdown(f"```\n{sources['job']}\n```")
                
                if sources["video"]:
                    st.markdown("---")
                    st.subheader("Full Video Transcript")
                    st.markdown(f"```\n{sources['video']}\n```")

        except Exception as e:
            st.error(f"Analysis Failed: {str(e)}")
            st.error("Please check:\n1. Valid API Key\n2. Working Job Post URL")

if __name__ == "__main__":
    if not GROQ_API_KEY:
        st.error("GROQ_API_KEY missing in .env")
    else:
        main()