package com.openmeteo.tools;

import com.openmeteo.api.client.OpenMeteoClient;
import com.openmeteo.api.client.models.DailyWeather;
import com.openmeteo.api.client.models.HourlyWeather;
import com.openmeteo.api.client.models.WeatherForecast;
import ch.sbb.mcp.commons.core.McpResult;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import reactor.core.publisher.Mono;
import reactor.test.StepVerifier;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class GetWeatherToolTest {
    
    @Mock
    private OpenMeteoClient openMeteoClient;
    
    private GetWeatherTool tool;
    
    @BeforeEach
    void setUp() {
        tool = new GetWeatherTool(openMeteoClient);
    }
    
    @Test
    void testToolMetadata() {
        assertThat(tool.name()).isEqualTo("getWeather");
        assertThat(tool.summary()).contains("weather forecast");
        assertThat(tool.description()).contains("temperature");
        assertThat(tool.category()).isEqualTo("weather");
        assertThat(tool.inputSchema()).contains("latitude");
        assertThat(tool.inputSchema()).contains("longitude");
    }
    
    @Test
    void testSuccessfulWeatherFetch() {
        // Arrange
        Map<String, Object> args = new HashMap<>();
        args.put("latitude", 46.9479);
        args.put("longitude", 7.4474);
        args.put("forecastDays", 3);
        
        WeatherForecast mockForecast = createMockForecast();
        when(openMeteoClient.getForecast(
                eq(46.9479),
                eq(7.4474),
                anyString(),
                anyString(),
                eq(3),
                eq("auto")
        )).thenReturn(Mono.just(mockForecast));
        
        // Act & Assert
        StepVerifier.create(tool.invoke(args))
                .assertNext(result -> {
                    assertThat(result.isSuccess()).isTrue();
                    if (result instanceof McpResult.Success<WeatherForecast> success) {
                        assertThat(success.data()).isEqualTo(mockForecast);
                    }
                })
                .verifyComplete();
    }
    
    @Test
    void testInvalidLatitude() {
        // Arrange
        Map<String, Object> args = new HashMap<>();
        args.put("latitude", 100.0); // Invalid: > 90
        args.put("longitude", 7.4474);
        
        // Act & Assert
        StepVerifier.create(tool.invoke(args))
                .assertNext(result -> {
                    assertThat(result.isSuccess()).isFalse();
                    if (result instanceof McpResult.Failure<WeatherForecast> failure) {
                        assertThat(failure.error()).isNotNull();
                        assertThat(failure.error().message()).containsIgnoringCase("latitude");
                    }
                })
                .verifyComplete();
    }
    
    @Test
    void testInvalidLongitude() {
        // Arrange
        Map<String, Object> args = new HashMap<>();
        args.put("latitude", 46.9479);
        args.put("longitude", 200.0); // Invalid: > 180
        
        // Act & Assert
        StepVerifier.create(tool.invoke(args))
                .assertNext(result -> {
                    assertThat(result.isSuccess()).isFalse();
                    if (result instanceof McpResult.Failure<WeatherForecast> failure) {
                        assertThat(failure.error()).isNotNull();
                        assertThat(failure.error().message()).containsIgnoringCase("longitude");
                    }
                })
                .verifyComplete();
    }
    
    @Test
    void testMissingLatitude() {
        // Arrange
        Map<String, Object> args = new HashMap<>();
        args.put("longitude", 7.4474);
        
        // Act & Assert
        StepVerifier.create(tool.invoke(args))
                .assertNext(result -> {
                    assertThat(result.isSuccess()).isFalse();
                })
                .verifyComplete();
    }
    
    @Test
    void testDefaultForecastDays() {
        // Arrange
        Map<String, Object> args = new HashMap<>();
        args.put("latitude", 46.9479);
        args.put("longitude", 7.4474);
        // No forecastDays specified
        
        WeatherForecast mockForecast = createMockForecast();
        when(openMeteoClient.getForecast(
                eq(46.9479),
                eq(7.4474),
                anyString(),
                anyString(),
                eq(7), // Default value
                eq("auto")
        )).thenReturn(Mono.just(mockForecast));
        
        // Act & Assert
        StepVerifier.create(tool.invoke(args))
                .assertNext(result -> assertThat(result.isSuccess()).isTrue())
                .verifyComplete();
    }
    
    @Test
    void testApiError() {
        // Arrange
        Map<String, Object> args = new HashMap<>();
        args.put("latitude", 46.9479);
        args.put("longitude", 7.4474);
        
        when(openMeteoClient.getForecast(
                anyDouble(),
                anyDouble(),
                anyString(),
                anyString(),
                anyInt(),
                anyString()
        )).thenReturn(Mono.error(new RuntimeException("API error")));
        
        // Act & Assert
        StepVerifier.create(tool.invoke(args))
                .assertNext(result -> {
                    assertThat(result.isSuccess()).isFalse();
                    if (result instanceof McpResult.Failure<WeatherForecast> failure) {
                        assertThat(failure.error()).isNotNull();
                        assertThat(failure.error().message()).contains("Failed to fetch weather");
                    }
                })
                .verifyComplete();
    }
    
    @Test
    void testIncludeHourlyFalse() {
        // Arrange
        Map<String, Object> args = new HashMap<>();
        args.put("latitude", 46.9479);
        args.put("longitude", 7.4474);
        args.put("includeHourly", false);
        
        WeatherForecast mockForecast = createMockForecast();
        when(openMeteoClient.getForecast(
                eq(46.9479),
                eq(7.4474),
                isNull(), // hourlyParams should be null
                anyString(),
                anyInt(),
                anyString()
        )).thenReturn(Mono.just(mockForecast));
        
        // Act & Assert
        StepVerifier.create(tool.invoke(args))
                .assertNext(result -> assertThat(result.isSuccess()).isTrue())
                .verifyComplete();
    }
    
    @Test
    void testCustomTimezone() {
        // Arrange
        Map<String, Object> args = new HashMap<>();
        args.put("latitude", 46.9479);
        args.put("longitude", 7.4474);
        args.put("timezone", "Europe/Zurich");
        
        WeatherForecast mockForecast = createMockForecast();
        when(openMeteoClient.getForecast(
                anyDouble(),
                anyDouble(),
                anyString(),
                anyString(),
                anyInt(),
                eq("Europe/Zurich")
        )).thenReturn(Mono.just(mockForecast));
        
        // Act & Assert
        StepVerifier.create(tool.invoke(args))
                .assertNext(result -> assertThat(result.isSuccess()).isTrue())
                .verifyComplete();
    }
    
    private WeatherForecast createMockForecast() {
        HourlyWeather hourly = new HourlyWeather(
                List.of("2025-12-23T00:00"),
                List.of(5.0),
                List.of(80),
                List.of(0.0),
                List.of(0.0),
                List.of(0),
                List.of(50),
                List.of(10.0)
        );
        
        DailyWeather daily = new DailyWeather(
                List.of("2025-12-23"),
                List.of(8.0),
                List.of(2.0),
                List.of(0.0),
                List.of(0.0),
                List.of(3600.0),
                List.of(0)
        );
        
        return new WeatherForecast(
                46.9479,
                7.4474,
                542.0,
                "Europe/Zurich",
                "CET",
                3600,
                hourly,
                daily,
                null
        );
    }
}
