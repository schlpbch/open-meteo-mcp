package com.openmeteo.prompts;

import ch.sbb.mcp.commons.prompts.McpPrompt;
import ch.sbb.mcp.commons.prompts.McpPromptArgument;
import ch.sbb.mcp.commons.prompts.McpPromptProvider;
import org.springframework.stereotype.Component;

import java.util.List;

/**
 * MCP Prompt: Ski Trip Weather
 * 
 * <p>Guides LLMs on how to check snow conditions and weather for ski trips,
 * using the swiss-ski-resorts resource and weather tools.</p>
 */
@Component
public class SkiTripWeatherPrompt implements McpPromptProvider {
    
    private static final String PROMPT_NAME = "ski-trip-weather";
    private static final String DESCRIPTION = "Guide for checking snow conditions and weather for ski trips to Swiss resorts";
    
    private static final String TEMPLATE = """
            You are helping plan a ski trip to Swiss Alps resorts. Follow this workflow:
            
            **Step 1: Identify the Resort**
            - If the user mentions a resort name, use the `swiss-ski-resorts` resource to get accurate coordinates
            - The resource contains 16 major Swiss ski resorts including Zermatt, Verbier, St. Moritz, Davos, etc.
            - Extract the latitude and longitude from the resource data
            
            **Step 2: Check Snow Conditions**
            - Use `getSnowConditions` tool with the resort coordinates
            - Key metrics to report:
              * Current snow depth (meters)
              * Recent snowfall (last 24-48 hours)
              * Forecast snowfall for next 7 days
              * Temperature trends (affects snow quality)
            
            **Step 3: Check General Weather**
            - Use `getWeather` tool for the same coordinates
            - Focus on:
              * Temperature (for comfort and snow quality)
              * Weather codes (use `weather-codes` resource to interpret)
              * Wind conditions (important for lift operations)
              * Visibility (fog can close lifts)
            
            **Step 4: Provide Ski Condition Assessment**
            - Combine snow and weather data to assess conditions:
              * **Excellent**: Fresh snow (>10cm), cold temps (-5°C to -15°C), clear skies
              * **Good**: Adequate snow depth (>50cm), stable temps, partly cloudy
              * **Fair**: Limited snow, warmer temps (risk of icy conditions), variable weather
              * **Poor**: No recent snow, very warm temps, heavy fog/storms
            
            **Step 5: Recommendations**
            - Suggest best days within the forecast period
            - Warn about potential issues (warm temps, storms, fog)
            - Recommend appropriate gear based on conditions
            
            **Example Query**: "What are the ski conditions in Zermatt this weekend?"
            
            **Example Response**:
            "I'll check the snow and weather conditions for Zermatt (45.9763°N, 7.6586°E).
            
            [Calls getSnowConditions and getWeather]
            
            **Current Conditions** (Jan 6, 2026):
            - Snow depth: 1.2m (excellent base)
            - Fresh snow: 15cm in last 24h
            - Temperature: -8°C (perfect for powder)
            - Weather: Clear skies (WMO code 0)
            - Wind: 12 km/h (lifts operating normally)
            
            **Weekend Forecast**:
            - Saturday: Partly cloudy, -6°C, no new snow
            - Sunday: Light snow expected (5-10cm), -10°C
            
            **Assessment**: Excellent conditions! Fresh powder from recent snowfall, cold temps preserving snow quality, and clear weather. Sunday looks especially good with more fresh snow expected.
            
            **Recommendations**:
            - Best day: Sunday (fresh powder)
            - Bring: Powder skis, warm layers
            - Note: Book early - conditions will attract crowds"
            
            **Related Resources**:
            - `swiss-ski-resorts`: Resort coordinates and metadata
            - `weather-codes`: Interpret weather condition codes
            - `weather-parameters`: Understanding snow depth, snowfall metrics
            
            **Related Tools**:
            - `getSnowConditions`: Snow depth, snowfall, mountain weather
            - `getWeather`: Temperature, precipitation, wind, visibility
            """;
    
    @Override
    public List<McpPrompt> getPrompts() {
        List<McpPromptArgument> arguments = List.of(
            new McpPromptArgument(
                "resort",
                "Name of the Swiss ski resort (e.g., 'Zermatt', 'Verbier', 'St. Moritz')",
                false
            ),
            new McpPromptArgument(
                "dates",
                "Specific dates or time period for the ski trip (e.g., 'this weekend', 'next week', 'January 10-15')",
                false
            )
        );
        
        return List.of(new McpPrompt(PROMPT_NAME, DESCRIPTION, arguments, TEMPLATE));
    }
}
