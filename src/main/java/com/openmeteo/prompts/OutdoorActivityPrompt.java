package com.openmeteo.prompts;

import ch.sbb.mcp.commons.prompts.McpPrompt;
import ch.sbb.mcp.commons.prompts.McpPromptArgument;
import ch.sbb.mcp.commons.prompts.McpPromptProvider;
import org.springframework.stereotype.Component;

import java.util.List;

/**
 * MCP Prompt: Plan Outdoor Activity
 * 
 * <p>Guides LLMs on weather-aware outdoor activity planning, helping users
 * choose suitable dates and prepare for weather conditions.</p>
 */
@Component
public class OutdoorActivityPrompt implements McpPromptProvider {
    
    private static final String PROMPT_NAME = "plan-outdoor-activity";
    private static final String DESCRIPTION = "Weather-aware outdoor activity planning workflow for hiking, cycling, and other outdoor pursuits";
    
    private static final String TEMPLATE = """
            You are helping plan outdoor activities with weather awareness. Follow this workflow:
            
            **Step 1: Understand the Activity**
            - Identify the activity type (hiking, cycling, camping, climbing, etc.)
            - Determine weather sensitivity:
              * **High sensitivity**: Climbing, via ferrata, high-altitude hiking (avoid rain, storms, high winds)
              * **Medium sensitivity**: Day hiking, cycling (manageable in light rain, avoid storms)
              * **Low sensitivity**: Walking, sightseeing (possible in most conditions except severe weather)
            
            **Step 2: Get Location Coordinates**
            - If the user provides a specific location, use those coordinates
            - For Swiss locations, you may reference common destinations
            - Ensure you have latitude and longitude for the activity area
            
            **Step 3: Check Weather Forecast**
            - Use `getWeather` tool with appropriate forecast days (typically 3-7 days)
            - Key metrics for outdoor activities:
              * **Precipitation**: Rain/snow amounts (mm)
              * **Weather codes**: Use `weather-codes` resource to interpret conditions
              * **Temperature**: Comfort and safety considerations
              * **Wind**: Important for exposed areas, high-altitude activities
              * **Visibility**: Critical for mountain activities
            
            **Step 4: Assess Suitability**
            Evaluate each day in the forecast:
            
            **Ideal Conditions**:
            - Clear or partly cloudy (codes 0-2)
            - No precipitation or minimal (<1mm)
            - Moderate temperatures (10-25°C for summer activities)
            - Light winds (<20 km/h for exposed areas)
            
            **Acceptable Conditions**:
            - Overcast but dry (code 3)
            - Light drizzle (<2mm, codes 51-53)
            - Appropriate temperature range for activity
            - Moderate winds (20-30 km/h)
            
            **Poor Conditions**:
            - Heavy rain (codes 61-65, >5mm)
            - Thunderstorms (codes 95-99)
            - Extreme temperatures
            - High winds (>30 km/h for exposed activities)
            - Fog (codes 45-48) for mountain activities
            
            **Step 5: Provide Recommendations**
            - Identify best days within the forecast period
            - Suggest alternative dates if conditions are poor
            - Recommend weather-appropriate gear:
              * Rain gear for drizzle/light rain
              * Warm layers for cold/wind
              * Sun protection for clear days
            - Provide safety warnings for severe weather
            
            **Example Query**: "I want to hike the Eiger Trail next week. What's the weather looking like?"
            
            **Example Response**:
            "I'll check the weather forecast for the Eiger Trail area (Grindelwald region: 46.6244°N, 8.0411°E) for the next 7 days.
            
            [Calls getWeather with 7-day forecast]
            
            **Forecast Summary**:
            - Mon-Tue: Partly cloudy, 15-18°C, no rain - **Ideal**
            - Wed: Overcast, 14°C, light drizzle (2mm) - **Acceptable with rain gear**
            - Thu-Fri: Rain showers, 12°C, 8-12mm - **Not recommended**
            - Sat-Sun: Clearing, 16-19°C, no rain - **Ideal**
            
            **Recommendation**: 
            Best days are **Monday, Tuesday, Saturday, or Sunday**. These offer clear to partly cloudy conditions with no precipitation - perfect for the exposed sections of the Eiger Trail.
            
            **Avoid Thursday-Friday** due to significant rain showers (8-12mm). The trail can become slippery and visibility may be reduced.
            
            **What to Bring**:
            - Layers (temps 15-19°C)
            - Sun protection (clear days)
            - Light rain jacket (just in case)
            - Sturdy hiking boots
            
            **Safety Note**: The Eiger Trail has exposed sections. Check local conditions before starting, especially after rain."
            
            **Activity-Specific Guidelines**:
            
            **Hiking**:
            - Avoid thunderstorms (lightning risk)
            - Check snow conditions for high-altitude trails
            - Consider visibility for mountain routes
            
            **Cycling**:
            - Light rain acceptable, avoid heavy rain (slippery roads)
            - Check wind conditions for exposed routes
            - Temperature comfort range: 10-28°C
            
            **Climbing/Via Ferrata**:
            - Requires dry conditions (wet rock is dangerous)
            - Avoid any rain or recent rain (<24h)
            - Check for afternoon thunderstorms in summer
            
            **Camping**:
            - Avoid heavy rain and storms
            - Check overnight temperatures
            - Wind important for tent stability
            
            **Related Resources**:
            - `weather-codes`: Interpret weather conditions
            - `weather-parameters`: Understanding precipitation, wind metrics
            
            **Related Tools**:
            - `getWeather`: Comprehensive weather forecast
            - `getSnowConditions`: For high-altitude activities in winter
            """;
    
    @Override
    public List<McpPrompt> getPrompts() {
        List<McpPromptArgument> arguments = List.of(
            new McpPromptArgument(
                "activity",
                "Type of outdoor activity (e.g., 'hiking', 'cycling', 'climbing', 'camping')",
                false
            ),
            new McpPromptArgument(
                "location",
                "Location for the activity (city, mountain, trail name)",
                false
            ),
            new McpPromptArgument(
                "timeframe",
                "When planning to do the activity (e.g., 'this weekend', 'next week', specific dates)",
                false
            )
        );
        
        return List.of(new McpPrompt(PROMPT_NAME, DESCRIPTION, arguments, TEMPLATE));
    }
}
