# File: proposal_generator.py

from typing import Optional
from langchain_core.prompts import (ChatPromptTemplate,
    SystemMessagePromptTemplate, HumanMessagePromptTemplate)
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

def extract_bullet_points(analysis_text: str) -> str:
    if "-" in analysis_text or "•" in analysis_text:
        return analysis_text.strip()
    else:
        lines = analysis_text.split("\n")
        bulletified = "\n".join(f"- {l.strip()}" for l in lines if l.strip())
        return bulletified

def generate_human_sounding_proposal(
    bullet_points: str,
    job_title: str,
    has_video: bool,
    tone: str = "default"
) -> str:

    llm = ChatGroq(
        temperature=0.75,  # Slightly higher for more personality
        model_name="llama3-70b-8192"
    )

    # 1. Enhanced style instructions based on tone
    if tone.lower() == "formal":
        style_instructions = (
            "Write professionally but warmly. Use phrases like 'I noticed', 'I specialize in', "
            "'I've successfully delivered'. Show confidence while maintaining professionalism."
        )
    elif tone.lower() == "casual":
        style_instructions = (
            "Write like you're having a coffee chat. Use phrases like 'Hey there', 'I'd love to help', "
            "'Let's chat'. Be friendly and enthusiastic while showing expertise."
        )
    elif tone.lower() == "technical":
        style_instructions = (
            "Write like a seasoned technical expert. Use relevant terminology naturally. "
            "Include phrases like 'I've implemented', 'Based on my experience with similar projects'."
        )
    else:
        style_instructions = (
            "Write confidently and conversationally. Use phrases like 'I noticed', 'Here's what I can do', "
            "'Let me handle this for you'. Show genuine interest and expertise."
        )

    # 2. Enhanced system prompt for more compelling proposals
    system_prompt_text = f"""
    You are an experienced freelancer writing a winning Upwork proposal. Write as if you're having a real conversation.

    Follow this structure:
    1. Start with "Hey" or a friendly greeting
    2. Open with a hook about their specific needs
    3. Show understanding of their challenges/frustrations
    4. Demonstrate relevant experience with specific examples
    5. Include 2-3 brief client testimonials or results (use emojis like ✅)
    6. Provide clear next steps
    7. End with a friendly sign-off
    8. Add a P.S. with an extra hook or insight about their business

    Style Guidelines:
    - {style_instructions}
    - Use first-person perspective ("I", "my", "me")
    - Show confidence without arrogance
    - Keep paragraphs short (2-3 lines max)
    - Use bullet points for examples/results
    - Add personality with phrases like "Here's the thing..." or "The simple solution:"
    - NEVER mention AI or analysis
    - If has_video=False, never mention videos
    - End with a P.S. that adds value or shows extra interest

    AVOID:
    - Generic language or clichés
    - Overly formal tone
    - Long, dense paragraphs
    - Just listing skills without context
    - Desperate or needy language
    """

    # 3. Enhanced user prompt for better results
    user_prompt_text = f"""
    Job Title: '{job_title}'

    Key Points to Address:
    {bullet_points}

    has_video = {has_video}

    Write a compelling proposal that:
    1) Opens with a friendly, personalized greeting
    2) Shows deep understanding of their specific needs
    3) Demonstrates relevant experience with concrete examples
    4) Includes 2-3 brief testimonials/results with emojis
    5) Provides clear next steps
    6) Ends with a friendly sign-off AND a P.S.

    Make it sound like a confident expert who's excited about their project.
    """

    # 4. Use the older pattern: we explicitly create prompt objects:
    system_msg = SystemMessagePromptTemplate.from_template(system_prompt_text)
    user_msg   = HumanMessagePromptTemplate.from_template(user_prompt_text)

    # 5. Build ChatPromptTemplate with 'messages=[...]'
    prompt_template = ChatPromptTemplate(
        messages=[system_msg, user_msg],
        # If your version requires listing input variables, do so; 
        # but typically the placeholders are in the template text itself.
    )

    chain = prompt_template | llm | StrOutputParser()

    # 6. Invoke
    result = chain.invoke({})
    return result
