import os
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

def get_analyzer_chain():
    """
    Returns an LCEL chain that uses ChatGroq to analyze reviews
    and output a strictly formatted JSON string.
    """
    model_name = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    llm = ChatGroq(
        model_name=model_name,
        temperature=0.1
    )

    # Define the system prompt with the requested JSON schema instructions
    system_prompt = """You are an expert review analyst. Your task is to analyze the provided reviews and output ONLY valid JSON.
Do not wrap your output in markdown blocks like ```json ... ```, just output the raw JSON string.

The JSON schema must include exactly the following keys:
- "overall_summary": (string) A comprehensive summary of all reviews combined.
- "food_summary": (string) Summary of comments related to food.
- "ambiance_summary": (string) Summary of comments related to ambiance or atmosphere.
- "cleanliness_summary": (string) Summary of comments related to cleanliness.
- "{service_key}": (string) Summary of comments related to the service or hospitality.
- "pros": (list of strings) Highlighting positive aspects.
- "cons": (list of strings) Highlighting negative aspects.
- "star_rating": (float) Calculate the star_rating by averaging the numeric ratings found in the fetched review text. Do not invent a number.

Please ensure your output is strictly valid JSON and nothing else."""

    human_prompt = """Please analyze the following reviews:

{reviews}"""

    # Create the complete chat prompt template
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_prompt),
        HumanMessagePromptTemplate.from_template(human_prompt)
    ])

    # Build an LCEL chain: prompt | llm | string output parser
    chain = prompt | llm | StrOutputParser()

    return chain
