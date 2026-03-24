import os
import pytest
import json
from unittest.mock import patch
from agent import run_analysis_agent
from models import ReviewAnalysis

@pytest.fixture
def mock_serpapi():
    """
    Mocks the SerpApi GoogleSearch calls to avoid using real API credits during tests.
    It returns a fake place_id and a couple of fake reviews.
    """
    # Force a dummy SERPAPI_API_KEY so tools.py doesn't error out early
    with patch.dict(os.environ, {"SERPAPI_API_KEY": "fake_serpapi_key"}):
        with patch('tools.GoogleSearch') as MockGoogleSearch:
            def google_search_side_effect(params):
                class MockSearch:
                    def get_dict(self):
                        if params.get('engine') == 'google_maps':
                            return {
                                "place_results": {
                                    "data_id": "0xfake:0xid",
                                    "type": "Hotel"
                                }
                            }
                        elif params.get('engine') == 'google_maps_reviews':
                            return {
                                "reviews": [
                                    {"rating": 5, "snippet": "Amazing service and perfectly clean rooms! The food was also great."},
                                    {"rating": 4, "snippet": "Good ambiance, but the checking process was a bit slow."}
                                ]
                            }
                        return {}
                return MockSearch()
                
            MockGoogleSearch.side_effect = google_search_side_effect
            yield

def test_run_analysis_agent_validates_schema(mock_serpapi):
    """
    Tests that the LangChain agent successfully fetches (mocked) reviews,
    passes them to the analyzer chain, and outputs a JSON matching the ReviewAnalysis model.
    """
    query = "Mocked Test Hotel in Mock City"
    response_str = run_analysis_agent(query)
    
    # 1. Ensure it returned a valid JSON string
    try:
        response_json = json.loads(response_str)
        if "error" in response_json:
            pytest.fail(f"Agent returned an error: {response_json['error']}")
    except json.JSONDecodeError:
        pytest.fail(f"Agent did not return valid JSON. Raw output: {response_str}")
        
    # 2. Validate the JSON perfectly matches the ReviewAnalysis Pydantic model
    try:
        validated_model = ReviewAnalysis.model_validate(response_json)
        
        # Verify specific structural requirements
        assert validated_model.overall_summary is not None
        assert isinstance(validated_model.pros, list)
        assert isinstance(validated_model.cons, list)
        
        # Verify the LLM accurately calculated the average of the mock star ratings (4 and 5)
        # Note: Depending on the LLM's exact math handling, it should be 4.5
        assert validated_model.star_rating == 4.5
        
    except Exception as e:
        pytest.fail(f"Output JSON does not match ReviewAnalysis schema. Validation Error: {e}")

if __name__ == "__main__":
    # Allows running with: python test_agent.py
    pytest.main([__file__, "-v"])
