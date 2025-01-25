# File: ui.py

import streamlit as st
from langchain.docstore.document import Document

def setup_ui():
    st.set_page_config(
        page_title="Upwork AI Assistant",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.title("🚀 Upwork Job Analyzer Pro")
    st.markdown("### AI-Powered Precision Proposal System")

def sidebar_inputs():
    with st.sidebar:
        st.header("Job Inputs")
        job_url = st.text_input("Job Posting URL (Required)")
        st.markdown("---")
        st.markdown("### Optional Video Analysis")
        video_input = st.text_input("YouTube Video URL (Optional)") 
        uploaded_file = st.file_uploader("Upload Video (Optional)", 
                                         type=["mp4", "mov", "mp3"])
        
        st.markdown("---")
        st.header("Proposal Template System")
        template_options = [
            "Default",
            "Formal",
            "Casual",
            "Technical",
            "Custom"
        ]
        selected_template = st.selectbox("Select Proposal Template:", template_options)
        custom_template_text = ""
        if selected_template == "Custom":
            st.write("Provide a custom proposal template below. **Use `{analysis}`** anywhere you'd like the AI to insert the analysis result.")
            custom_template_text = st.text_area(
                "Custom Template",
                placeholder="Type your custom proposal template here..."
            )
        
        analyze_btn = st.button("Analyze Job", type="primary")
        
    # Return all sidebar inputs, including template selection
    return job_url, video_input, uploaded_file, analyze_btn, selected_template, custom_template_text

def display_results(analysis, proposal, sources):
    st.subheader("🔬 Precision Analysis Report")
    st.markdown(analysis["answer"])

    st.markdown("---")
    st.subheader("📝 Laser-Targeted Proposal")

    tab1, tab2 = st.tabs(["Formatted View", "Plain Text"])
    with tab1:
        st.markdown(proposal)
    with tab2:
        clean_proposal = proposal.replace("**", "").replace("*", "")
        st.code(clean_proposal, language="text")
        if st.button("📋 Copy Proposal"):
            st.session_state.proposal = clean_proposal
            st.success("Proposal copied to clipboard (in session).")

    with st.expander("🔍 Full Source Materials"):
        st.subheader("Complete Job Post Analysis")
        st.markdown(f"**Title:** {sources['job']['title']}\n\n")
        st.markdown(f"**Description:**\n```\n{sources['job']['description']}\n```")

        if sources["job"]["links"]:
            st.markdown("---")
            st.subheader("Extracted Links")
            for link in sources["job"]["links"]:
                st.markdown(f"- {link}")

        if sources["job"]["documents"]:
            st.markdown("---")
            st.subheader("Extracted Documents")
            for doc in sources["job"]["documents"]:
                st.markdown(f"- {doc}")

        if sources["video"]:
            st.markdown("---")
            st.subheader("Full Video Transcript")
            st.markdown(f"```\n{sources['video']}\n```")
