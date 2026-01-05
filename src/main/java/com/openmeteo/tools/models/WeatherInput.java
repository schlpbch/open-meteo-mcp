package com.openmeteo.tools.models;

import ch.sbb.mcp.commons.validation.Validators;

/**
 * Input parameters for GetWeatherTool.
 * 
 * @param latitude Latitude in decimal degrees (-90 to 90)
 * @param longitude Longitude in decimal degrees (-180 to 180)
 * @param forecastDays Number of forecast days (1-16)
 * @param includeHourly Include hourly forecast data
 * @param timezone Timezone for timestamps
 */
public record WeatherInput(
    double latitude,
    double longitude,
    int forecastDays,
    boolean includeHourly,
    String timezone
) {
    
    /**
     * Creates WeatherInput with validation.
     */
    public WeatherInput {
        Validators.requireValidLatitude(latitude);
        Validators.requireValidLongitude(longitude);
        
        if (forecastDays < 1 || forecastDays > 16) {
            throw new IllegalArgumentException(
                "Forecast days must be between 1 and 16, got: " + forecastDays);
        }
        
        if (timezone == null || timezone.isBlank()) {
            throw new IllegalArgumentException("Timezone cannot be null or blank");
        }
    }
}
