package com.openmeteo.prompts;

import ch.sbb.mcp.commons.prompts.McpPrompt;
import ch.sbb.mcp.commons.prompts.McpPromptArgument;
import ch.sbb.mcp.commons.prompts.McpPromptProvider;
import org.springframework.stereotype.Component;

import java.util.List;

/**
 * MCP Prompt: Weather-Aware Travel
 * 
 * <p>Guides LLMs on integrating weather information with journey planning,
 * helping users prepare for weather conditions at their destination.</p>
 */
@Component
public class WeatherAwareTravelPrompt implements McpPromptProvider {
    
    private static final String PROMPT_NAME = "weather-aware-travel";
    private static final String DESCRIPTION = "Integration pattern for combining weather forecasts with journey planning";
    
    private static final String TEMPLATE = """
            You are helping integrate weather information into travel planning. Follow this workflow:
            
            **Step 1: Extract Destination Information**
            - Identify the travel destination from the user's query
            - If coordinates are available from journey planning tools, use those
            - Otherwise, use known coordinates for major Swiss cities/destinations
            
            **Step 2: Determine Travel Timeframe**
            - Extract travel dates from the query
            - If planning a trip, focus on arrival and stay period
            - For day trips, check weather for the entire day
            - Default to 3-7 day forecast if dates are unclear
            
            **Step 3: Check Destination Weather**
            - Use `getWeather` tool with destination coordinates
            - For mountain destinations, also use `getSnowConditions` if relevant
            - Focus on:
              * Overall conditions (clear, rainy, snowy)
              * Temperature range
              * Precipitation amounts
              * Any severe weather warnings
            
            **Step 4: Provide Weather-Aware Travel Advice**
            
            **Packing Recommendations**:
            - **Clear/Sunny** (codes 0-1): Sunglasses, sunscreen, light clothing
            - **Partly Cloudy** (codes 2-3): Layers, light jacket
            - **Rainy** (codes 51-82): Waterproof jacket, umbrella, water-resistant shoes
            - **Snowy** (codes 71-86): Winter coat, warm layers, winter boots
            - **Stormy** (codes 95-99): Postpone if possible, or prepare for indoor activities
            
            **Temperature-Based Advice**:
            - **Cold** (<5°C): Warm coat, gloves, hat, thermal layers
            - **Cool** (5-15°C): Jacket, long sleeves, layers
            - **Mild** (15-25°C): Light jacket, comfortable clothing
            - **Warm** (>25°C): Light clothing, sun protection, hydration
            
            **Travel Impact Assessment**:
            - **No Impact**: Clear to partly cloudy, normal temperatures
            - **Minor Impact**: Light rain (bring umbrella), cold (dress warm)
            - **Moderate Impact**: Heavy rain (delays possible), snow (slower travel)
            - **Significant Impact**: Storms (major delays), extreme weather (consider rescheduling)
            
            **Step 5: Activity Suggestions**
            Based on weather, suggest appropriate activities:
            - **Good Weather**: Outdoor sightseeing, hiking, lake activities
            - **Mixed Weather**: Flexible plans, indoor/outdoor mix
            - **Poor Weather**: Museums, indoor attractions, covered markets
            
            **Example Query**: "I'm traveling to Lucerne tomorrow. What should I pack?"
            
            **Example Response**:
            "Let me check the weather forecast for Lucerne (47.0502°N, 8.3093°E) for tomorrow.
            
            [Calls getWeather]
            
            **Tomorrow's Weather in Lucerne**:
            - Condition: Partly cloudy (WMO code 2)
            - Temperature: 8-14°C
            - Precipitation: 0mm (dry day)
            - Wind: 15 km/h (light breeze)
            
            **Packing Recommendations**:
            - Light jacket or sweater (temps 8-14°C)
            - Comfortable walking shoes (dry conditions)
            - Sunglasses (partly cloudy, some sun)
            - Layers (temperature varies throughout day)
            
            **Travel Impact**: None expected. Good conditions for sightseeing.
            
            **Activity Suggestions**:
            - Perfect for walking the Chapel Bridge and old town
            - Lake Lucerne boat tours will be pleasant
            - Mt. Pilatus or Rigi excursions recommended (check mountain weather separately)
            
            **Note**: Morning will be cooler (8°C), warming to 14°C by afternoon. Start with layers and remove as it warms up."
            
            **Integration with Journey Planning**:
            
            When used alongside journey planning tools:
            1. Get destination coordinates from journey/station data
            2. Check weather for arrival time and duration of stay
            3. Warn about weather-related travel delays (snow, storms)
            4. Suggest weather-appropriate activities at destination
            
            **Example Integrated Query**: "Plan a trip from Zurich to Zermatt this weekend"
            
            **Integrated Response Flow**:
            1. [Journey tool] Find train connections Zurich → Zermatt
            2. [Weather tool] Check Zermatt weather for weekend
            3. [Snow tool] Check Zermatt snow conditions (mountain destination)
            4. Provide combined travel + weather + activity recommendations
            
            **Special Cases**:
            
            **Mountain Destinations**:
            - Always check `getSnowConditions` in addition to weather
            - Warn about altitude-related weather changes
            - Check for avalanche risk in winter (mention in severe weather)
            
            **Multi-Day Trips**:
            - Provide day-by-day weather summary
            - Suggest best days for outdoor vs. indoor activities
            - Recommend packing for variable conditions
            
            **International Travel**:
            - Weather tools work worldwide, not just Switzerland
            - Adjust temperature/condition expectations for destination climate
            - Consider seasonal differences
            
            **Related Resources**:
            - `weather-codes`: Interpret weather conditions
            - `swiss-ski-resorts`: Mountain destination coordinates
            - `weather-parameters`: Understanding weather metrics
            
            **Related Tools**:
            - `getWeather`: Destination weather forecast
            - `getSnowConditions`: Mountain/ski destination conditions
            - Journey planning tools (from other MCP servers): Get destination coordinates
            """;
    
    @Override
    public List<McpPrompt> getPrompts() {
        List<McpPromptArgument> arguments = List.of(
            new McpPromptArgument(
                "destination",
                "Travel destination (city, resort, or location name)",
                false
            ),
            new McpPromptArgument(
                "travel_dates",
                "When traveling (e.g., 'tomorrow', 'this weekend', 'January 10-15')",
                false
            ),
            new McpPromptArgument(
                "trip_type",
                "Type of trip (e.g., 'day trip', 'weekend getaway', 'ski trip', 'business travel')",
                false
            )
        );
        
        return List.of(new McpPrompt(PROMPT_NAME, DESCRIPTION, arguments, TEMPLATE));
    }
}
