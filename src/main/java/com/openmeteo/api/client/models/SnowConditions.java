package com.openmeteo.api.client.models;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * Snow conditions response from Open-Meteo API.
 * 
 * @param latitude Latitude of the location
 * @param longitude Longitude of the location
 * @param timezone Timezone string (e.g., "Europe/Zurich")
 * @param hourly Hourly snow data
 * @param daily Daily snow data
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public record SnowConditions(
        double latitude,
        double longitude,
        String timezone,
        
        @JsonProperty("hourly")
        HourlySnow hourly,
        
        @JsonProperty("daily")
        DailySnow daily
) {
}
