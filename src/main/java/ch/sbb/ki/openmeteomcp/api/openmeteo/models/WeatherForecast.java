package ch.sbb.ki.openmeteomcp.api.openmeteo.models;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * Weather forecast response from Open-Meteo API.
 * 
 * @param latitude Latitude of the location
 * @param longitude Longitude of the location
 * @param elevation Elevation in meters above sea level
 * @param timezone Timezone identifier (e.g., "Europe/Zurich")
 * @param timezoneAbbreviation Timezone abbreviation (e.g., "CET")
 * @param utcOffsetSeconds UTC offset in seconds
 * @param hourly Hourly weather data
 * @param daily Daily weather data
 * @param currentWeather Current weather conditions (if requested)
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public record WeatherForecast(
        double latitude,
        double longitude,
        double elevation,
        String timezone,
        
        @JsonProperty("timezone_abbreviation")
        String timezoneAbbreviation,
        
        @JsonProperty("utc_offset_seconds")
        int utcOffsetSeconds,
        
        HourlyWeather hourly,
        DailyWeather daily,
        
        @JsonProperty("current_weather")
        CurrentWeather currentWeather
) {
}
