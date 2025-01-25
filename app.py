# File: app.py
# Main application file for Upwork Job Analyzer Pro

from config import GROQ_API_KEY
from job_scraper import scrape_job_post
from ui import setup_ui, sidebar_inputs, display_results
from video_processor import VideoProcessor
from rag_pipeline import RAGPipeline
from langchain.docstore.document import Document
import streamlit as st

# Import from proposal_generator
from proposal_generator import extract_bullet_points, generate_human_sounding_proposal

def main():
    # 1) Set up the UI layout
    setup_ui()
    
    # 2) Initialize required objects
    vp = VideoProcessor()
    rag = RAGPipeline()

    # 3) Get sidebar inputs (existing code)
    (
        job_url,
        video_input,
        uploaded_file,
        analyze_btn,
        selected_template,
        custom_template_text
    ) = sidebar_inputs()

    if analyze_btn:
        if not job_url:
            st.error("Please provide a job posting URL to analyze.")
            return

        try:
            with st.spinner("Deep Analysis in Progress..."):
                # Prepare doc storage
                docs = []
                sources = {
                    "job": {
                        "title": "",
                        "description": "",
                        "links": [],
                        "documents": []
                    },
                    "video": ""
                }

                # 4) Scrape job post
                st.write("🔍 Deep Scanning Job Post...")
                scraped_data = scrape_job_post(job_url)
                if "error" in scraped_data:
                    st.error(scraped_data["error"])
                    return

                # Put scraped info into 'sources'
                sources["job"]["title"] = scraped_data["title"]
                sources["job"]["description"] = scraped_data["description"]
                sources["job"]["links"] = scraped_data["links"]
                sources["job"]["documents"] = scraped_data["documents"]

                docs.append(Document(
                    page_content=sources["job"]["description"],
                    metadata={"source": "job_post"}
                ))

                # 5) Check if video was provided
                has_video = False
                if video_input or uploaded_file:
                    has_video = True
                    st.write("🎬 Frame-by-Frame Video Analysis...")
                    video_source = video_input or uploaded_file
                    try:
                        video_text = vp.transcribe_video(video_source)
                        sources["video"] = video_text
                        docs.append(Document(
                            page_content=video_text,
                            metadata={"source": "video"}
                        ))
                    except Exception as video_error:
                        st.warning(f"Video processing failed: {str(video_error)}")

                # 6) Build Knowledge Base & generate RAG analysis
                st.write("🧠 Building Context-Aware Database...")
                retriever = rag.create_knowledge_base(docs)

                analysis_prompt = (
                    "Analyze this job post and, if present, any video content to extract "
                    "key requirements, client needs, and project goals. If no video is "
                    "provided, ignore video references."
                )
                analysis = rag.generate_response(analysis_prompt, retriever)
                analysis_text = analysis["answer"]  # the analysis from RAG

                # 7) Convert the analysis text into bullet points
                bullet_points = extract_bullet_points(analysis_text)

                # 8) Decide the tone based on selected_template
                #    If user picks "Default"/"Formal"/"Casual"/"Technical"/"Custom",
                #    we can interpret that as a "tone" param.
                #    - For "Custom" you might do something else, but let's treat "Custom"
                #      as just 'default' or we can read custom_template_text if you want
                #      to handle that. Below is an example.

                tone_map = {
                    "Default": "default",
                    "Formal": "formal",
                    "Casual": "casual",
                    "Technical": "technical"
                }
                if selected_template in tone_map:
                    chosen_tone = tone_map[selected_template]
                else:
                    chosen_tone = "default"  # fallback

                # 9) Generate the final proposal
                job_title = sources["job"]["title"] or "Client"
                proposal = generate_human_sounding_proposal(
                    bullet_points=bullet_points,
                    job_title=job_title,
                    has_video=has_video,
                    tone=chosen_tone
                )

            # 10) Display final results (unchanged)
            display_results(analysis, proposal, sources)

        except Exception as e:
            st.error(f"Scraping Failed: {str(e)}")
            st.error("Please check:\n1. Valid Job Post URL\n2. Network Connection")

if __name__ == "__main__":
    if not GROQ_API_KEY:
        st.error("GROQ_API_KEY missing in .env")
    else:
        main()
