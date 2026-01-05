package com.openmeteo.api.client.models;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.List;

/**
 * Daily weather data from Open-Meteo API.
 * 
 * @param time List of dates (ISO 8601 format, YYYY-MM-DD)
 * @param temperature2mMax Maximum daily temperature at 2 meters (°C)
 * @param temperature2mMin Minimum daily temperature at 2 meters (°C)
 * @param precipitationSum Total daily precipitation (mm)
 * @param rainSum Total daily rain (mm)
 * @param sunshineDuration Total sunshine duration (seconds)
 * @param weatherCode WMO Weather interpretation code for the day
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public record DailyWeather(
        List<String> time,
        
        @JsonProperty("temperature_2m_max")
        List<Double> temperature2mMax,
        
        @JsonProperty("temperature_2m_min")
        List<Double> temperature2mMin,
        
        @JsonProperty("precipitation_sum")
        List<Double> precipitationSum,
        
        @JsonProperty("rain_sum")
        List<Double> rainSum,
        
        @JsonProperty("sunshine_duration")
        List<Double> sunshineDuration,
        
        @JsonProperty("weather_code")
        List<Integer> weatherCode
) {
}
