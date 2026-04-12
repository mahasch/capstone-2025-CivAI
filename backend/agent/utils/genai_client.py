import os
from google import genai
from google.api_core import retry

# Singleton client instance
_client = None

def get_genai_client():
    """
    Returns a singleton instance of the GenAI client.
    Ensures the same client is used throughout the application.
    """
    global _client
    if _client is None:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise EnvironmentError("GOOGLE_API_KEY environment variable not set.")

        _client = genai.Client(api_key=api_key)

        # Add retry logic for API calls
        is_retriable = lambda e: (isinstance(e, genai.errors.APIError) and e.code in {429, 503})
        if not hasattr(genai.models.Models.generate_content, '__wrapped__'):
            genai.models.Models.generate_content = retry.Retry(
                predicate=is_retriable)(genai.models.Models.generate_content)

    return _client