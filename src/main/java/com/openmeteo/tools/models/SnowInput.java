package com.openmeteo.tools.models;

import ch.sbb.mcp.commons.validation.Validators;

/**
 * Input parameters for GetSnowConditionsTool.
 * 
 * @param latitude Latitude in decimal degrees (-90 to 90)
 * @param longitude Longitude in decimal degrees (-180 to 180)
 * @param forecastDays Number of forecast days (1-16)
 * @param includeHourly Include hourly forecast data
 */
public record SnowInput(
    double latitude,
    double longitude,
    int forecastDays,
    boolean includeHourly
) {
    
    /**
     * Creates SnowInput with validation.
     */
    public SnowInput {
        Validators.requireValidLatitude(latitude);
        Validators.requireValidLongitude(longitude);
        
        if (forecastDays < 1 || forecastDays > 16) {
            throw new IllegalArgumentException(
                "Forecast days must be between 1 and 16, got: " + forecastDays);
        }
    }
}
