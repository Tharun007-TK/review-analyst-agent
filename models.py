from typing import List, Optional
from pydantic import BaseModel, Field

class ReviewAnalysis(BaseModel):
    """
    Pydantic model to validate the JSON schema output of the review analyzer chain.
    """
    overall_summary: str = Field(description="A comprehensive summary of all reviews combined.")
    food_summary: str = Field(description="Summary of comments related to food.")
    ambiance_summary: str = Field(description="Summary of comments related to ambiance or atmosphere.")
    cleanliness_summary: str = Field(description="Summary of comments related to cleanliness.")
    
    # Optional fields to accommodate both 'service_summary' (for restaurants) and 'hospitality_summary' (for hotels)
    service_summary: Optional[str] = Field(
        default=None, 
        description="Summary of comments related to service. Used when the place is a restaurant."
    )
    hospitality_summary: Optional[str] = Field(
        default=None, 
        description="Summary of comments related to hospitality. Used when the place is a hotel."
    )
    
    pros: List[str] = Field(description="List of positive aspects extracted from reviews.")
    cons: List[str] = Field(description="List of negative aspects extracted from reviews.")
    star_rating: float = Field(description="The calculated or estimated average star rating from the reviews.")
