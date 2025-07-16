import java.io.UnsupportedEncodingException;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.HashMap;
import java.util.StringJoiner;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutionException;
import java.util.Map;
import java.io.IOException;

public class NewsAPIClient {
    final private String baseUrl;
    final private String apiKey;
    final private HttpClient httpClient;

    public NewsAPIClient(String baseUrl, String apiKey) {
        if (baseUrl == null || baseUrl.isEmpty()) {
            throw new IllegalArgumentException("baseUrl cannot be null or empty");
        }
        if (apiKey == null || apiKey.isEmpty()) {
            throw new IllegalArgumentException("apiKey cannot be null or empty");
        }
        this.baseUrl = baseUrl;
        this.apiKey = apiKey;
        this.httpClient = HttpClient.newHttpClient();
    }

    public CompletableFuture<HttpResponse<String>> getNews(String Endpoint, Map<String, String> queryParams) {

        // copy params to avoid mutating caller's map
        Map<String, String> params = new HashMap<>(queryParams);
        params.put("apiKey", this.apiKey);
        String fullURL;
        try {
            fullURL = buildURL(Endpoint, params);
        } catch (UnsupportedEncodingException e) {
            CompletableFuture<HttpResponse<String>>  failed = new CompletableFuture<>();
            failed.completeExceptionally(e);
            return failed;
        }
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(fullURL))
                .timeout(Duration.ofSeconds(20))
                .GET()
                .build();

        return httpClient.sendAsync(request, HttpResponse.BodyHandlers.ofString())
                .thenCompose(response -> {
                    int statusCode = response.statusCode();
                    if (statusCode >= 200 && statusCode < 300) {
                        return CompletableFuture.completedFuture(response);
                    } else {
                        CompletableFuture<HttpResponse<String>>  failed = new CompletableFuture<>();
                        failed.completeExceptionally(
                                new ApiException("HTTP error: " + statusCode + "\nBody: " + response.body())
                        );
                        return failed;
                    }
                });

    }

    private String buildURL(String endpoint, Map<String, String> queryParams) throws UnsupportedEncodingException {
        StringJoiner joiner = new StringJoiner("&");
        for (Map.Entry<String, String> entry : queryParams.entrySet()) {
            // Ensure that special characters won't break the URL
            String key = URLEncoder.encode(entry.getKey(), StandardCharsets.UTF_8);
            String value = URLEncoder.encode(entry.getValue(), StandardCharsets.UTF_8);
            joiner.add(key + "=" + value);
        }
        return this.baseUrl + endpoint + "?" + joiner.toString();
    }

    private Map<String, String> buildQueryParams(Map<String, String> queryParams, String key, String value) {
        queryParams.put(key, value);
        return queryParams;
    }

    public static class ApiException extends Exception {
        public ApiException(String message) {
            super(message);
        }
    }

}
