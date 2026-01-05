package com.openmeteo.tools;

import com.openmeteo.api.client.OpenMeteoClient;
import com.openmeteo.api.client.models.SnowConditions;
import ch.sbb.mcp.commons.core.McpError;
import ch.sbb.mcp.commons.core.McpResult;
import ch.sbb.mcp.commons.core.McpTool;
import com.openmeteo.tools.models.SnowInput;
import ch.sbb.mcp.commons.handler.BaseToolHandler;
import org.springframework.stereotype.Component;
import reactor.core.publisher.Mono;

import java.util.Map;

@Component
public class GetSnowConditionsTool 
    extends BaseToolHandler<SnowInput, SnowConditions>
    implements McpTool<McpResult<SnowConditions>> {
    
    private static final String NAME = "getSnowConditions";
    private static final String SUMMARY = "Get snow conditions for Swiss Alps ski resorts (snowfall, snow depth, temperature)";
    private static final String DESCRIPTION = """
        Get snow conditions and forecasts for Swiss Alps ski resorts and mountain regions.
        
        **Examples**:
        - "Snow conditions in St. Moritz?" → latitude: 46.4908, longitude: 9.8355
        - "Is there fresh snow in Zermatt?" → Check hourly snowfall
        - "Ski conditions this weekend?" → Check daily forecast
        
        **Provides**:
        - Hourly snowfall (last 24h and forecast)
        - Daily snow forecast (next 7 days)
        - Snow depth on ground
        - Temperature (important for snow quality)
        - Freezing level altitude
        
        **Popular Swiss Ski Resorts**:
        - Zermatt (Matterhorn): 45.9763, 7.6586
        - Verbier: 46.0964, 7.2283
        - St. Moritz: 46.4908, 9.8355
        - Davos: 46.8029, 9.8366
        - Grindelwald: 46.6244, 8.0411
        
        **Data Source**: Open-Meteo API with mountain weather model
        
        **Performance**: < 250ms
        
        **Use this tool when**:
        - User asks about snow or ski conditions
        - Planning ski trips
        - Checking mountain weather
        - Combined with journey planning to ski resorts
        
        **Related tools**: getWeather (for general weather), findTrips (to plan journey to ski resort), findPlaces (to get coordinates from resort names)
        """;
    
    private static final String INPUT_SCHEMA = """
        {
          "type": "object",
          "properties": {
            "latitude": {
              "type": "number",
              "description": "Latitude in decimal degrees (e.g., 45.9763 for Zermatt)",
              "minimum": -90,
              "maximum": 90
            },
            "longitude": {
              "type": "number",
              "description": "Longitude in decimal degrees (e.g., 7.6586 for Zermatt)",
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
            }
          },
          "required": ["latitude", "longitude"]
        }
        """;
    
    private final OpenMeteoClient openMeteoClient;
    
    public GetSnowConditionsTool(OpenMeteoClient openMeteoClient) {
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
    public Mono<McpResult<SnowConditions>> invoke(Map<String, Object> arguments) {
        return execute(arguments)
            .map(McpResult::success)
            .onErrorResume(ch.sbb.mcp.commons.validation.ValidationException.class, e ->
                Mono.just(McpResult.invalidInput(e.getMessage(), "Validation failed"))
            )
            .onErrorResume(IllegalArgumentException.class, e ->
                Mono.just(McpResult.invalidInput(e.getMessage(), "Invalid argument"))
            )
            .onErrorResume(e -> Mono.just(McpResult.failure(
                McpError.internalError("Failed to fetch snow conditions", e.getMessage())
            )));
    }
    
    @Override
    protected String getToolName() {
        return NAME;
    }
    
    @Override
    protected SnowInput validateAndParse(Map<String, Object> arguments) {
        double latitude = getRequiredDouble(arguments, "latitude");
        double longitude = getRequiredDouble(arguments, "longitude");
        int forecastDays = getOptionalInt(arguments, "forecastDays", 7);
        boolean includeHourly = getOptionalBoolean(arguments, "includeHourly", true);
        
        return new SnowInput(latitude, longitude, forecastDays, includeHourly);
    }
    
    @Override
    protected Mono<SnowConditions> executeInternal(SnowInput input) {
        String hourlyParams = input.includeHourly() 
                ? "snowfall,snow_depth,temperature_2m"
                : null;
        String dailyParams = "snowfall_sum,snow_depth_max,temperature_2m_max,temperature_2m_min";
        
        return openMeteoClient.getSnowConditions(
            input.latitude(),
            input.longitude(),
            hourlyParams,
            dailyParams,
            input.forecastDays(),
            "Europe/Zurich"
        );
    }
}
