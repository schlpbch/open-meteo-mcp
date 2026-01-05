package com.openmeteo.tools;

import com.openmeteo.api.client.OpenMeteoClient;
import com.openmeteo.api.client.models.WeatherForecast;
import ch.sbb.mcp.commons.core.McpError;
import ch.sbb.mcp.commons.core.McpResult;
import ch.sbb.mcp.commons.core.McpTool;
import com.openmeteo.tools.models.WeatherInput;
import ch.sbb.mcp.commons.handler.BaseToolHandler;
import org.springframework.stereotype.Component;
import reactor.core.publisher.Mono;

import java.util.Map;

/**
 * MCP Tool: Get Weather
 * 
 * <p>Fetch weather information (temperature, rain, sunshine) for a location using Open-Meteo API.</p>
 * 
 * <p>Example invocation:</p>
 * <pre>{@code
 * {
 *   "name": "getWeather",
 *   "arguments": {
 *     "latitude": 46.9479,
 *     "longitude": 7.4474,
 *     "forecastDays": 3
 *   }
 * }
 * }</pre>
 */
@Component
public class GetWeatherTool 
    extends BaseToolHandler<WeatherInput, WeatherForecast>
    implements McpTool<McpResult<WeatherForecast>> {
    
    private static final String NAME = "getWeather";
    private static final String SUMMARY = "Get weather forecast for a location (temperature, rain, sunshine)";
    private static final String DESCRIPTION = """
        Get current weather conditions for any location in Switzerland (or worldwide).
        
        **Examples**:
        - "What's the weather in Zürich?" → latitude: 47.3769, longitude: 8.5417
        - "Weather at destination" → Use coordinates from journey endpoint
        - "Is it raining in Bern?" → Check precipitation field
        
        **Provides**:
        - Current temperature (°C)
        - Weather condition (clear, cloudy, rain, snow)
        - Precipitation amount (mm)
        - Wind speed (km/h)
        - Humidity (%)
        - Hourly and daily forecasts
        
        **Data Source**: Open-Meteo API (free, no API key required)
        
        **Performance**: < 200ms
        
        **Use this tool when**:
        - User asks about weather conditions
        - Planning outdoor activities
        - Checking if weather affects travel
        - Combined with journey planning
        
        **Related tools**: getSnowConditions (for ski resorts), findTrips (to plan weather-appropriate travel), findPlaces (to get coordinates from place names)
        """;
    
    private static final String INPUT_SCHEMA = """
        {
          "type": "object",
          "properties": {
            "latitude": {
              "type": "number",
              "description": "Latitude in decimal degrees (e.g., 46.9479 for Bern)",
              "minimum": -90,
              "maximum": 90
            },
            "longitude": {
              "type": "number",
              "description": "Longitude in decimal degrees (e.g., 7.4474 for Bern)",
              "minimum": -180,
              "maximum": 180
            },
            "forecastDays": {
              "type": "integer",
              "description": "Number of forecast days (1-16, default 7)",
              "minimum": 1,
              "maximum": 16,
              "default": 7
            },
            "includeHourly": {
              "type": "boolean",
              "description": "Include hourly forecast data (default true)",
              "default": true
            },
            "timezone": {
              "type": "string",
              "description": "Timezone for timestamps (e.g., 'Europe/Zurich', default 'auto')",
              "default": "auto"
            }
          },
          "required": ["latitude", "longitude"]
        }
        """;
    
    private final OpenMeteoClient openMeteoClient;
    
    public GetWeatherTool(OpenMeteoClient openMeteoClient) {
        this.openMeteoClient = openMeteoClient;
    }
    
    @Override
    public String name() {
        return NAME;
    }
    
    @Override
    public String summary() {
        return SUMMARY;
    }
    
    @Override
    public String description() {
        return DESCRIPTION;
    }
    
    @Override
    public String inputSchema() {
        return INPUT_SCHEMA;
    }
    
    @Override
    public String category() {
        return "weather";
    }
    
    @Override
    public Mono<McpResult<WeatherForecast>> invoke(Map<String, Object> arguments) {
        // Use BaseToolHandler.execute() for validation, logging, and execution
        return execute(arguments)
            .map(McpResult::success)
            .onErrorResume(ch.sbb.mcp.commons.validation.ValidationException.class, e ->
                Mono.just(McpResult.invalidInput(e.getMessage(), "Validation failed"))
            )
            .onErrorResume(IllegalArgumentException.class, e ->
                Mono.just(McpResult.invalidInput(e.getMessage(), "Invalid argument"))
            )
            .onErrorResume(e -> Mono.just(McpResult.failure(
                McpError.internalError("Failed to fetch weather data", e.getMessage())
            )));
    }
    
    @Override
    protected String getToolName() {
        return NAME;
    }
    
    @Override
    protected WeatherInput validateAndParse(Map<String, Object> arguments) {
        // Extract and validate parameters using BaseToolHandler helper methods
        double latitude = getRequiredDouble(arguments, "latitude");
        double longitude = getRequiredDouble(arguments, "longitude");
        int forecastDays = getOptionalInt(arguments, "forecastDays", 7);
        boolean includeHourly = getOptionalBoolean(arguments, "includeHourly", true);
        String timezone = getOptionalString(arguments, "timezone", "auto");
        
        // WeatherInput constructor validates lat/lon ranges using Validators from commons
        return new WeatherInput(latitude, longitude, forecastDays, includeHourly, timezone);
    }
    
    @Override
    protected Mono<WeatherForecast> executeInternal(WeatherInput input) {
        // Build parameter strings
        String hourlyParams = input.includeHourly() 
                ? "temperature_2m,relative_humidity_2m,precipitation,rain,weather_code,cloud_cover,wind_speed_10m"
                : null;
        String dailyParams = "temperature_2m_max,temperature_2m_min,precipitation_sum,rain_sum,sunshine_duration,weather_code";
        
        // Call Open-Meteo API
        return openMeteoClient.getForecast(
            input.latitude(),
            input.longitude(),
            hourlyParams,
            dailyParams,
            input.forecastDays(),
            input.timezone()
        );
    }
}
