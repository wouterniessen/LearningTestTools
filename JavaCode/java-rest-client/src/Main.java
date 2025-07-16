import java.io.IOException;
import java.io.FileInputStream;
import java.net.http.HttpResponse;
import java.sql.SQLOutput;
import java.util.HashMap;
import java.util.Properties;
import java.util.Map;
import java.util.concurrent.CompletableFuture;

public class Main {
    public static String baseURL = "https://newsapi.org/v2/";
    public static String apiKey;
    public static String endPoint = "top-headlines/";
    public static Map<String, String> queryParams;

    public static void main(String[] args) throws IOException {

        // Load in the apikey from .env file.
        Properties env = new Properties();
        try (FileInputStream in = new FileInputStream(".env")) {
            env.load(in);
        }
        apiKey = env.getProperty("NEWS_API_KEY");
        if (apiKey == null) {
            throw new IllegalStateException("NEWS_API_KEY missing from .env");
        }
        NewsAPIClient newsClient = new NewsAPIClient(baseURL, apiKey);
        queryParams = new HashMap<>();
        queryParams.put("country", "us");
        queryParams.put("category", "technology");
        CompletableFuture< HttpResponse<String>> future = newsClient.getNews(endPoint, queryParams);
        future.thenAccept(response -> {
            System.out.println("Status: " + response.statusCode());
            System.out.println("Body:\n"  + response.body());
        }).exceptionally(ex -> {
            Throwable cause = ex.getCause() != null ? ex.getCause() : ex;
            if (cause instanceof NewsAPIClient.ApiException) {
                System.err.println("API error: " + cause.getMessage());
            } else {
                System.err.println("Request failed: " + cause);
            }
            return null;
        })
                .join();
    }
}