#
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
    api_name: str = "newsapi"
    endpoint: str = "top-headlines"

    # Define the parameters for the API request
    params: dict = {
        "category": "technology",
        "language": "en,nl",
    }

    # Create an instance of the RESTClient with the request URL
    client = RESTClientManager()

    try:
        # Fetch data from the REST API
        response = asyncio.run(client.fetch(api_name, endpoint, params))
        print(f"Number of articles found: {response.get('totalResults', 'Unknown')}")
    except httpx.HTTPStatusError as e:
        print(f"HTTP error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        print(f"Error: {e}")

    print(f"{response.get('articles', [])[:3]}")  # Print first 3 articles


class RESTClientManager:
    """Manager for multiple REST clients."""

    def __init__(self):
        news_api_key = os.getenv("NEWS_API_KEY")
        if not news_api_key:
            raise ValueError(
                "API key not found. Please set the NEWS_API_KEY environment variable."
            )
        self.clients = {
            "newsapi": NewsAPIClient("https://newsapi.org/v2", news_api_key),
            # Add more APIs here
        }

    async def fetch(self, api_name: str, endpoint: str, params: dict = None) -> dict:
        """Initiates a fetch request to the specified API and endpoint.

        Args:
            api_name (str): Name of the API to fetch from.
            endpoint (str): Endpoint to fetch data from.
            params (dict, optional): Request Parameters. Defaults to None.

        Raises:
            ValueError: If the specified API client does not exist.

        Returns:
            dict: Response data from the API.
        """

        client = self.clients.get(api_name)
        if not client:
            raise ValueError(f"No REST client found for API '{api_name}'")
        else:
            print(f"Requesting data from {client.base_url}/{endpoint}...")
        return await client.fetch(endpoint, params)


class NewsAPIClient:
    """
    A simple REST client for fetching data from a REST API.
    """

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key

    async def fetch(self, endpoint: str, params: dict = None) -> dict:
        """Fetches data from the REST API and checks for sources if 'language' is in params.

        Args:
            endpoint (str): data endpoint to fetch.
            params (dict, optional): Request Parameters. Defaults to None.

        Returns:
            dict: Response data from the API.
        """
        if params is None:
            params = {}
        params["apiKey"] = self.api_key  # Always add the API key

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
