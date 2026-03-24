import json
import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_groq import ChatGroq

from tools import fetch_place_reviews
from analyzer import get_analyzer_chain
from models import ReviewAnalysis

load_dotenv()

def run_analysis_agent(user_query: str) -> str:
    """
    Invokes the agent to fetch reviews for the given user_query using LangChain v1.2+
    create_agent API, then analyzes with the analyzer chain and validates via Pydantic.
    """
    # 1. Initialize the Groq LLM
    model_name = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    llm = ChatGroq(model_name=model_name, temperature=0.1)

    # 2. Create the agent using the new create_agent API (LangChain v1.2+ / LangGraph)
    system_prompt = (
        "You are a helpful assistant. Use the provided tools to fulfill the user's request. "
        "You MUST use the fetch_place_reviews tool to get data. Do NOT summarize or analyze yourself."
    )

    agent = create_agent(
        model=llm,
        tools=[fetch_place_reviews],
        system_prompt=system_prompt,
    )

    # 3. Invoke the agent — new API returns a dict with 'messages'
    result = agent.invoke({"messages": [{"role": "user", "content": user_query}]})

    # 4. Extract intermediate tool calls to find the fetch_place_reviews observation
    messages = result.get("messages", [])

    is_hotel = False
    reviews_text = ""

    # Walk messages in reverse to find the last ToolMessage response
    for msg in reversed(messages):
        msg_type = getattr(msg, "type", None) or msg.get("type", "")
        if msg_type == "tool":
            # The tool message content is the observation from fetch_place_reviews
            content = getattr(msg, "content", None) or msg.get("content", "")
            try:
                # Our tool returns a JSON-serializable dict; Langchain serializes it as string
                observation = json.loads(content) if isinstance(content, str) else content
            except (json.JSONDecodeError, TypeError):
                observation = content

            if isinstance(observation, dict):
                if "error" in observation:
                    return json.dumps({"error": observation["error"]})
                is_hotel = observation.get("is_hotel", False)
                reviews_text = observation.get("reviews", "")
            else:
                reviews_text = str(observation)
            break

    if not reviews_text or "No reviews found" in reviews_text:
        return json.dumps({"error": "No reviews were found for analysis."})

    # 5. Prepare and invoke the analyzer chain
    chain = get_analyzer_chain()
    service_key = "hospitality_summary" if is_hotel else "service_summary"

    # LCEL chain returns a string directly via StrOutputParser
    json_output_str = chain.invoke({
        "service_key": service_key,
        "reviews": reviews_text
    })

    # Clean up markdown code fences if the LLM wrapped the output
    if json_output_str.startswith("```json"):
        json_output_str = json_output_str.split("```json")[1].split("```")[0].strip()
    elif json_output_str.startswith("```"):
        json_output_str = json_output_str.split("```")[1].split("```")[0].strip()

    try:
        # 6. Validate the structured JSON against the ReviewAnalysis Pydantic model
        validated_analysis = ReviewAnalysis.model_validate_json(json_output_str)
        return validated_analysis.model_dump_json(indent=2)
    except Exception as e:
        print(f"Validation Error: {e}")
        return json_output_str


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(f"Executing query: {query}")
        result = run_analysis_agent(query)
        print("\n\nFINAL STRUCTURED OUTPUT:\n")
        print(result)
