package com.openmeteo.api.client.models;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * Current weather conditions from Open-Meteo API.
 * 
 * @param temperature Current temperature (°C)
 * @param windSpeed Current wind speed (km/h)
 * @param windDirection Wind direction (degrees)
 * @param weatherCode WMO Weather interpretation code
 * @param time Timestamp of the current weather (ISO 8601)
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public record CurrentWeather(
        double temperature,
        
        @JsonProperty("windspeed")
        double windSpeed,
        
        @JsonProperty("winddirection")
        int windDirection,
        
        @JsonProperty("weathercode")
        int weatherCode,
        
        String time
) {
}
