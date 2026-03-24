import os
from typing import Optional, Dict, Union, Any
from langchain_core.tools import tool
from serpapi import GoogleSearch

def check_if_hotel(place_type: Union[str, list, None]) -> bool:
    """Helper function to check if a place is a hotel based on its type keywords."""
    if not place_type:
        return False
        
    if isinstance(place_type, list):
        types_str = " ".join(place_type).lower()
    else:
        types_str = str(place_type).lower()
        
    hotel_keywords = ['hotel', 'lodging', 'resort', 'motel', 'inn', 'hostel', 'guesthouse']
    return any(keyword in types_str for keyword in hotel_keywords)

@tool
def fetch_place_reviews(place_name: str, location: str) -> dict:
    """
    Fetches the latest reviews for a given place and location using SerpApi Google Maps API.
    
    Args:
        place_name: The name of the place (e.g., "Starbucks").
        location: The location of the place (e.g., "New York, NY").
        
    Returns:
        A dictionary containing a boolean 'is_hotel' and a formatted string 'reviews' containing the review text and star rating for each review, up to 10 reviews.
    """
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        return {"error": "SERPAPI_API_KEY environment variable is not set."}

    query = f"{place_name} {location}"
    
    try:
        # Step 1: Search for the place to get its data_id
        search_params = {
            "engine": "google_maps",
            "q": query,
            "api_key": api_key
        }
        
        search = GoogleSearch(search_params)
        search_results = search.get_dict()
        
        # Check if place_results exists (direct match)
        data_id = None
        place_type = None
        if "place_results" in search_results and "data_id" in search_results["place_results"]:
            data_id = search_results["place_results"]["data_id"]
            place_type = search_results["place_results"].get("type")
        elif "local_results" in search_results and len(search_results["local_results"]) > 0:
            # Fallback to the first local result
            first_result = search_results["local_results"][0]
            data_id = first_result.get("data_id")
            place_type = first_result.get("type")
            
        if not data_id:
            return {"error": f"Could not find place '{place_name}' in '{location}'."}
            
        is_hotel = check_if_hotel(place_type)
            
        # Step 2: Fetch reviews using the data_id
        reviews_params = {
            "engine": "google_maps_reviews",
            "data_id": data_id,
            "sort_by": "newestFirst", # Get the newest reviews
            "api_key": api_key
        }
        
        reviews_search = GoogleSearch(reviews_params)
        reviews_results = reviews_search.get_dict()
        
        reviews = reviews_results.get("reviews", [])
        
        if not reviews:
            return {
                "is_hotel": is_hotel,
                "reviews": f"No reviews found for '{place_name}' in '{location}'."
            }
            
        # Format the top 10 reviews and truncate words
        formatted_reviews = []
        for i, review in enumerate(reviews[:10]):
            rating = review.get("rating", "N/A")
            text = review.get("snippet", "No text provided.")
            if not text or str(text).strip() == "":
                text = "No text provided."
            
            # Truncate each review to a maximum of 200 words
            words = str(text).split()
            if len(words) > 200:
                text = " ".join(words[:200]) + "..."
                
            formatted_reviews.append(f"Review {i+1}:\nRating: {rating} Stars\nText: {text}\n")
            
        # Check total characters length to prevent overflow context window limits
        combined_text = "\n".join(formatted_reviews)
        if len(combined_text) > 4000:
            # Fallback mapping limiting to the top 5 most relevant reviews
            combined_text = "\n".join(formatted_reviews[:5])
            
        return {
            "is_hotel": is_hotel,
            "reviews": combined_text
        }
        
    except Exception as e:
        return {"error": f"Error fetching reviews: {str(e)}"}
