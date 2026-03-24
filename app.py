import streamlit as st
import json
from agent import run_analysis_agent

st.set_page_config(page_title="Review Insight Agent", layout="centered")

# Sidebar for API info
with st.sidebar:
    st.header("About This App")
    st.write("This app uses the **LangChain Agent** architecture to fetch and summarize reviews.")
    st.subheader("APIs Used:")
    st.markdown("- **SerpApi (Google Maps)**: Fetches the latest reviews from Google Maps.")
    st.markdown("- **Groq (llama3-70b)**: Analyzes the fetched reviews to generate a structured JSON summary.")
    st.info("Make sure your API keys (GROQ_API_KEY, SERPAPI_API_KEY) are set in the .env file.")

st.title("Review Insight Agent")

place_name = st.text_input("Place Name", placeholder="e.g. Starbucks")
location = st.text_input("Location", placeholder="e.g. Seattle, WA")

if st.button("Generate Report"):
    if place_name and location:
        with st.spinner("Analyzing reviews... This may take a moment."):
            query = f"{place_name} in {location}"
            try:
                # Call the agent
                json_response_str = run_analysis_agent(query)
                
                # Parse the final json result
                result_data = json.loads(json_response_str)
                
                # Check for logic/api errors bubbled up inside the json
                if "error" in result_data:
                    st.error(f"Agent Error: {result_data['error']}")
                else:
                    # Metric for Star Rating
                    st.metric(label="⭐ Star Rating", value=result_data.get("star_rating", "N/A"))
                    
                    st.subheader("Detailed Summaries")
                    
                    with st.expander("Overall Summary", expanded=True):
                        st.write(result_data.get("overall_summary", "N/A"))
                        
                    with st.expander("Food Summary"):
                        st.write(result_data.get("food_summary", "N/A"))
                        
                    with st.expander("Ambiance Summary"):
                        st.write(result_data.get("ambiance_summary", "N/A"))
                        
                    with st.expander("Cleanliness Summary"):
                        st.write(result_data.get("cleanliness_summary", "N/A"))
                        
                    # Figure out which service summary to display dynamically
                    service_val = result_data.get("service_summary")
                    hospitality_val = result_data.get("hospitality_summary")
                    
                    if service_val:
                        with st.expander("Service Summary"):
                            st.write(service_val)
                    elif hospitality_val:
                        with st.expander("Hospitality Summary"):
                            st.write(hospitality_val)
                    else:
                        with st.expander("Service / Hospitality Summary"):
                            st.write("N/A")
                    
                    st.subheader("Pros & Cons")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### 👍 Pros")
                        for pro in result_data.get("pros", []):
                            st.markdown(f"- {pro}")
                            
                    with col2:
                        st.markdown("### 👎 Cons")
                        for con in result_data.get("cons", []):
                            st.markdown(f"- {con}")

            except json.JSONDecodeError:
                st.error("Failed to parse the response from the agent. The LLM may have hallucinated formatting.")
                with st.expander("Show Raw Text Output", expanded=False):
                    st.write(json_response_str)
            except Exception as e:
                # Catch-all for other execution exceptions
                st.error(f"An unexpected error occurred during execution: {str(e)}")
    else:
        st.warning("Please enter both Place Name and Location.")
