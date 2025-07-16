import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.StringJoiner;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutionException;
import java.util.Map;

public class NewsAPIClient {
    final private String baseUrl;
    final private String apiKey;

    public NewsAPIClient(String baseUrl, String apiKey) {
        if (baseUrl == null || baseUrl.isEmpty()) {
            throw new IllegalArgumentException("baseUrl cannot be null or empty");
        }
        if (apiKey == null || apiKey.isEmpty()) {
            throw new IllegalArgumentException("apiKey cannot be null or empty");
        }
        this.baseUrl = baseUrl;
        this.apiKey = apiKey;
    }

    public HttpResponse<String> getNews(String Endpoint, Map<String, String> queryParams) {
        queryParams.put("apiKey", this.apiKey);
        String fullURL = buildURL(Endpoint, queryParams);
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(fullURL))
                .GET()
                .build();

        HttpClient client = HttpClient.newHttpClient();

    }

    private String buildURL(String endpoint, Map<String, String> queryParams) {
        StringJoiner joiner = new StringJoiner("&");
        for (Map.Entry<String, String> entry : queryParams.entrySet()) {
            // Ensure that special characters won't break the URL
            String key = URLEncoder.encode(entry.getKey(), "UTF-8");
            String value = URLEncoder.encode(entry.getValue(), "UTF-8");
            joiner.add(key + "=" + value);
        }
        return this.baseUrl + endpoint + "?" + joiner.toString();
    }

    private Map<String, String> buildQueryParams(Map<String, String> queryParams, String key, String value) {
        queryParams.put(key, value);
        return queryParams;
    }

}
