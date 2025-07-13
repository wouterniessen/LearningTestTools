import asyncio
import httpx
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Fix SSL certificate issue
if "SSL_CERT_FILE" in os.environ:
    ssl_cert_file = os.environ["SSL_CERT_FILE"]
    if not os.path.exists(ssl_cert_file):
        print(f"Warning: Removing invalid SSL_CERT_FILE: {ssl_cert_file}")
        del os.environ["SSL_CERT_FILE"]


def main():
    request_url: str = "https://newsapi.org/v2"
    endpoint: str = "top-headlines"

    print(f"Requesting data from {request_url}/{endpoint}...")

    # Get the API key from environment variables
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        raise ValueError(
            "API key not found. Please set the NEWS_API_KEY environment variable."
        )

    # Define the parameters for the API request
    params: dict = {
        "category": "technology",
        "language": "en,nl",
        "apiKey": api_key,
    }

    # Create an instance of the RESTClient with the request URL
    client = RESTClient(request_url)

    try:
        # Fetch data from the REST API
        response = asyncio.run(client.fetch(endpoint, params))
        print(f"Number of articles found: {response.get('totalResults', 'Unknown')}")
    except Exception as e:
        print(f"Error: {e}")

    print(f"{response.get('articles', [])[:3]}")  # Print first 3 articles


class RESTClient:
    """
    A simple REST client for fetching data from a REST API.
    """

    def __init__(self, base_url: str):
        self.base_url = base_url

    async def fetch(self, endpoint: str, params: dict = None) -> dict:
        """Fetches data from the REST API and checks for sources if 'language' is in params.

        Args:
            endpoint (str): data endpoint to fetch.
            params (dict, optional): Request Parameters. Defaults to None.

        Returns:
            dict: Response data from the API.
        """
        if "language" in params and endpoint == "top-headlines":
            # If 'language' is in params, we need to fetch sources first
            # and then use the source IDs in the params for the main request.
            endpoint_sources = "/sources"
            sources = await self.get(endpoint_sources, params)
            source_ids = [source["id"] for source in sources.get("sources", [])]
            params["sources"] = ",".join(source_ids)

            del params["language"]  # Remove unsupported 'language' from params

        return await self.get(endpoint, params)

    async def get(self, endpoint: str, params: dict = None) -> dict:
        """Fetches data from the specified endpoint.

        Args:
            endpoint (str): data endpoint to fetch.
            params (dict, optional): Request Parameters. Defaults to None.

        Returns:
            dict: Response data from the API.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/{endpoint}", params=params)
            response.raise_for_status()
            return response.json()


if __name__ == "__main__":
    main()
