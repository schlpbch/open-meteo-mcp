package ch.sbb.ki.openmeteomcp.api.openmeteo;

import ch.sbb.ki.openmeteomcp.api.openmeteo.models.WeatherForecast;
import ch.sbb.ki.openmeteomcp.api.openmeteo.models.SnowConditions;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

/**
 * Client for the Open-Meteo Weather API.
 * 
 * <p>Open-Meteo is a free, open-source weather API that provides:
 * <ul>
 *   <li>Current weather conditions</li>
 *   <li>Hourly forecasts (up to 16 days)</li>
 *   <li>Daily forecasts</li>
 *   <li>Historical weather data</li>
 * </ul>
 * 
 * <p>API Documentation: https://open-meteo.com/en/docs
 * 
 * <p>No API key required. Free for non-commercial use.
 */
@Component
public class OpenMeteoClient {
    
    private static final Logger logger = LoggerFactory.getLogger(OpenMeteoClient.class);
    private static final String BASE_URL = "https://api.open-meteo.com/v1";
    
    private final WebClient webClient;
    
    public OpenMeteoClient(WebClient.Builder webClientBuilder) {
        this.webClient = webClientBuilder
                .baseUrl(BASE_URL)
                .build();
    }
    
    /**
     * Get current weather and forecast for a location.
     * 
     * @param latitude Latitude in decimal degrees (e.g., 46.9479 for Bern)
     * @param longitude Longitude in decimal degrees (e.g., 7.4474 for Bern)
     * @param hourlyParams Hourly weather parameters to include (e.g., "temperature_2m,precipitation,sunshine_duration")
     * @param dailyParams Daily weather parameters to include (e.g., "temperature_2m_max,precipitation_sum,sunshine_duration")
     * @param forecastDays Number of forecast days (1-16, default 7)
     * @param timezone Timezone for timestamps (e.g., "Europe/Zurich", default "auto")
     * @return Weather forecast data
     */
    public Mono<WeatherForecast> getForecast(
            double latitude,
            double longitude,
            String hourlyParams,
            String dailyParams,
            Integer forecastDays,
            String timezone) {
        
        logger.debug("Fetching weather forecast for lat={}, lon={}", latitude, longitude);
        
        return webClient.get()
                .uri(uriBuilder -> {
                    var builder = uriBuilder
                            .path("/forecast")
                            .queryParam("latitude", latitude)
                            .queryParam("longitude", longitude)
                            .queryParam("timezone", timezone != null ? timezone : "auto");
                    
                    if (hourlyParams != null && !hourlyParams.isBlank()) {
                        builder.queryParam("hourly", hourlyParams);
                    }
                    
                    if (dailyParams != null && !dailyParams.isBlank()) {
                        builder.queryParam("daily", dailyParams);
                    }
                    
                    if (forecastDays != null && forecastDays > 0) {
                        builder.queryParam("forecast_days", Math.min(forecastDays, 16));
                    }
                    
                    return builder.build();
                })
                .retrieve()
                .bodyToMono(WeatherForecast.class)
                .doOnSuccess(forecast -> logger.debug("Successfully fetched weather forecast"))
                .doOnError(error -> logger.error("Failed to fetch weather forecast: {}", error.getMessage()));
    }
    
    /**
     * Get current weather for a location (simplified method).
     * 
     * @param latitude Latitude in decimal degrees
     * @param longitude Longitude in decimal degrees
     * @return Current weather and 7-day forecast
     */
    public Mono<WeatherForecast> getCurrentWeather(double latitude, double longitude) {
        return getForecast(
                latitude,
                longitude,
                "temperature_2m,relative_humidity_2m,precipitation,rain,weather_code,cloud_cover,wind_speed_10m",
                "temperature_2m_max,temperature_2m_min,precipitation_sum,rain_sum,sunshine_duration,weather_code",
                7,
                "auto"
        );
    }
    
    /**
     * Get snow conditions for a location.
     * 
     * @param latitude Latitude in decimal degrees (e.g., 45.9763 for Zermatt)
     * @param longitude Longitude in decimal degrees (e.g., 7.6586 for Zermatt)
     * @param hourlyParams Hourly snow parameters (e.g., "snowfall,snow_depth,temperature_2m")
     * @param dailyParams Daily snow parameters (e.g., "snowfall_sum,snow_depth_max,temperature_2m_max,temperature_2m_min")
     * @param forecastDays Number of forecast days (1-16, default 7)
     * @param timezone Timezone for timestamps (e.g., "Europe/Zurich", default "auto")
     * @return Snow conditions data
     */
    public Mono<SnowConditions> getSnowConditions(
            double latitude,
            double longitude,
            String hourlyParams,
            String dailyParams,
            Integer forecastDays,
            String timezone) {
        
        logger.debug("Fetching snow conditions for lat={}, lon={}", latitude, longitude);
        
        return webClient.get()
                .uri(uriBuilder -> {
                    var builder = uriBuilder
                            .path("/forecast")
                            .queryParam("latitude", latitude)
                            .queryParam("longitude", longitude)
                            .queryParam("timezone", timezone != null ? timezone : "Europe/Zurich");
                    
                    if (hourlyParams != null && !hourlyParams.isBlank()) {
                        builder.queryParam("hourly", hourlyParams);
                    }
                    
                    if (dailyParams != null && !dailyParams.isBlank()) {
                        builder.queryParam("daily", dailyParams);
                    }
                    
                    if (forecastDays != null && forecastDays > 0) {
                        builder.queryParam("forecast_days", Math.min(forecastDays, 16));
                    }
                    
                    return builder.build();
                })
                .retrieve()
                .bodyToMono(SnowConditions.class)
                .doOnSuccess(conditions -> logger.debug("Successfully fetched snow conditions"))
                .doOnError(error -> logger.error("Failed to fetch snow conditions: {}", error.getMessage()));
    }
    
    /**
     * Get snow conditions for a location (simplified method).
     * 
     * @param latitude Latitude in decimal degrees
     * @param longitude Longitude in decimal degrees
     * @return Snow conditions with 7-day forecast
     */
    public Mono<SnowConditions> getSnowConditions(double latitude, double longitude) {
        return getSnowConditions(
                latitude,
                longitude,
                "snowfall,snow_depth,temperature_2m",
                "snowfall_sum,snow_depth_max,temperature_2m_max,temperature_2m_min",
                7,
                "Europe/Zurich"
        );
    }
}
