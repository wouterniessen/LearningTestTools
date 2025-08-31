import pytest
from unittest.mock import AsyncMock, MagicMock
from main import NewsAPIClient, WeatherAPIClient, RESTClientManager


@pytest.mark.asyncio
async def test_news_api_client_fetch(mocker):
    # Arrange
    mock_response = {
        "status": "ok",
        "sources": [{"id": "abc-news", "name": "ABC News"}],
    }
    mock_async_client = mocker.patch("httpx.AsyncClient", autospec=True)
    mock_instance = mock_async_client.return_value.__aenter__.return_value

    # Mock the response object
    mock_http_response = MagicMock()
    mock_http_response.status_code = 200
    mock_http_response.json.return_value = mock_response  # Mock json() as synchronous
    mock_instance.get.return_value = mock_http_response

    client = NewsAPIClient(base_url="https://newsapi.org/v2", api_key="test_api_key")
    endpoint = "sources"
    params = {"language": "en"}

    # Act
    response = await client.fetch(endpoint, params)

    # Assert
    mock_instance.get.assert_called_once_with(
        "https://newsapi.org/v2/sources",
        params={"language": "en", "apiKey": "test_api_key"},
    )
    assert response == mock_response


@pytest.mark.asyncio
async def test_weather_api_client_fetch(mocker):
    # Arrange
    mock_response = {"location": {"name": "Delft"}, "current": {"temp_c": 15.0}}
    mock_async_client = mocker.patch("httpx.AsyncClient", autospec=True)
    mock_instance = mock_async_client.return_value.__aenter__.return_value

    # Mock the response object
    mock_http_response = MagicMock()
    mock_http_response.status_code = 200
    mock_http_response.json.return_value = mock_response  # Mock json() as synchronous
    mock_instance.get.return_value = mock_http_response

    client = WeatherAPIClient(
        base_url="http://api.weatherapi.com/v1", api_key="test_api_key"
    )
    endpoint = "current.json"
    params = {"q": "Delft", "lang": "en"}

    # Act
    response = await client.fetch(endpoint, params)

    # Assert
    mock_instance.get.assert_called_once_with(
        "http://api.weatherapi.com/v1/current.json",
        params={"q": "Delft", "lang": "en", "key": "test_api_key"},
    )
    assert response == mock_response


@pytest.mark.asyncio
async def test_rest_client_manager_fetch(mocker):
    # Arrange
    mock_news_response = {"status": "ok", "articles": [{"title": "News Title"}]}
    mock_weather_response = {"location": {"name": "Delft"}, "current": {"temp_c": 15.0}}

    # Mock NewsAPIClient
    mock_news_client = mocker.patch("main.NewsAPIClient", autospec=True)
    mock_news_instance = mock_news_client.return_value
    mock_news_instance.fetch.return_value = mock_news_response
    mock_news_instance.base_url = "https://newsapi.org/v2"  # Add base_url to the mock

    # Mock WeatherAPIClient
    mock_weather_client = mocker.patch("main.WeatherAPIClient", autospec=True)
    mock_weather_instance = mock_weather_client.return_value
    mock_weather_instance.fetch.return_value = mock_weather_response
    mock_weather_instance.base_url = (
        "http://api.weatherapi.com/v1"  # Add base_url to the mock
    )

    # Initialize RESTClientManager
    manager = RESTClientManager()

    # Act & Assert: Test NewsAPIClient delegation
    news_response = await manager.fetch("newsapi", "top-headlines", {"language": "en"})
    mock_news_instance.fetch.assert_called_once_with(
        "top-headlines", {"language": "en"}
    )
    assert news_response == mock_news_response

    # Act & Assert: Test WeatherAPIClient delegation
    weather_response = await manager.fetch("weatherapi", "current.json", {"q": "Delft"})
    mock_weather_instance.fetch.assert_called_once_with("current.json", {"q": "Delft"})
    assert weather_response == mock_weather_response

    # Act & Assert: Test invalid API name
    with pytest.raises(ValueError, match="No REST client found for API 'invalidapi'"):
        await manager.fetch("invalidapi", "endpoint", {})
