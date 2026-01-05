package ch.sbb.ki.openmeteomcp.api.openmeteo.models;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.List;

/**
 * Hourly snow data from Open-Meteo API.
 * 
 * @param time List of timestamps (ISO 8601 format)
 * @param snowfall Hourly snowfall in cm
 * @param snowDepth Snow depth on ground in meters
 * @param temperature2m Temperature at 2 meters above ground (°C)
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public record HourlySnow(
        List<String> time,
        
        List<Double> snowfall,
        
        @JsonProperty("snow_depth")
        List<Double> snowDepth,
        
        @JsonProperty("temperature_2m")
        List<Double> temperature2m
) {
}
