package com.openmeteo.api.client.models;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.List;

/**
 * Hourly weather data from Open-Meteo API.
 * 
 * @param time List of timestamps (ISO 8601 format)
 * @param temperature2m Temperature at 2 meters above ground (°C)
 * @param relativeHumidity2m Relative humidity at 2 meters (%)
 * @param precipitation Total precipitation (rain + snow) (mm)
 * @param rain Rain only (mm)
 * @param weatherCode WMO Weather interpretation code
 * @param cloudCover Cloud cover (%)
 * @param windSpeed10m Wind speed at 10 meters (km/h)
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public record HourlyWeather(
        List<String> time,
        
        @JsonProperty("temperature_2m")
        List<Double> temperature2m,
        
        @JsonProperty("relative_humidity_2m")
        List<Integer> relativeHumidity2m,
        
        List<Double> precipitation,
        List<Double> rain,
        
        @JsonProperty("weather_code")
        List<Integer> weatherCode,
        
        @JsonProperty("cloud_cover")
        List<Integer> cloudCover,
        
        @JsonProperty("wind_speed_10m")
        List<Double> windSpeed10m
) {
}
