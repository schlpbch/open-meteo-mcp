package com.openmeteo.api.client.models;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.List;

/**
 * Daily snow summary from Open-Meteo API.
 * 
 * @param time List of dates (ISO 8601 format, YYYY-MM-DD)
 * @param snowfallSum Total daily snowfall in cm
 * @param snowDepthMax Maximum snow depth in meters
 * @param temperature2mMax Maximum daily temperature at 2 meters (°C)
 * @param temperature2mMin Minimum daily temperature at 2 meters (°C)
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public record DailySnow(
        List<String> time,
        
        @JsonProperty("snowfall_sum")
        List<Double> snowfallSum,
        
        @JsonProperty("snow_depth_max")
        List<Double> snowDepthMax,
        
        @JsonProperty("temperature_2m_max")
        List<Double> temperature2mMax,
        
        @JsonProperty("temperature_2m_min")
        List<Double> temperature2mMin
) {
}
