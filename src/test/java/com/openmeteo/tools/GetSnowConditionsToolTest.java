package com.openmeteo.tools;

import com.openmeteo.api.client.OpenMeteoClient;
import com.openmeteo.api.client.models.DailySnow;
import com.openmeteo.api.client.models.HourlySnow;
import com.openmeteo.api.client.models.SnowConditions;
import ch.sbb.mcp.commons.core.McpResult;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Tag;
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

@Tag("unit")
@ExtendWith(MockitoExtension.class)
class GetSnowConditionsToolTest {
    
    @Mock
    private OpenMeteoClient openMeteoClient;
    
    private GetSnowConditionsTool tool;
    
    @BeforeEach
    void setUp() {
        tool = new GetSnowConditionsTool(openMeteoClient);
    }
    
    @Test
    void testToolMetadata() {
        assertThat(tool.name()).isEqualTo("getSnowConditions");
        assertThat(tool.summary()).contains("snow conditions");
        assertThat(tool.description()).contains("snowfall");
        assertThat(tool.description()).containsIgnoringCase("snow depth");
        assertThat(tool.category()).isEqualTo("weather");
        assertThat(tool.inputSchema()).contains("latitude");
        assertThat(tool.inputSchema()).contains("longitude");
    }
    
    @Test
    void testSuccessfulSnowConditionsFetch() {
        // Arrange
        Map<String, Object> args = new HashMap<>();
        args.put("latitude", 45.9763); // Zermatt
        args.put("longitude", 7.6586);
        args.put("forecastDays", 3);
        
        SnowConditions mockConditions = createMockSnowConditions();
        when(openMeteoClient.getSnowConditions(
                eq(45.9763),
                eq(7.6586),
                anyString(),
                anyString(),
                eq(3),
                eq("Europe/Zurich")
        )).thenReturn(Mono.just(mockConditions));
        
        // Act & Assert
        StepVerifier.create(tool.invoke(args))
                .assertNext(result -> {
                    assertThat(result.isSuccess()).isTrue();
                    if (result instanceof McpResult.Success<SnowConditions> success) {
                        assertThat(success.data()).isEqualTo(mockConditions);
                        assertThat(success.data().latitude()).isEqualTo(45.9763);
                        assertThat(success.data().longitude()).isEqualTo(7.6586);
                    }
                })
                .verifyComplete();
    }
    
    @Test
    void testInvalidLatitude() {
        // Arrange
        Map<String, Object> args = new HashMap<>();
        args.put("latitude", 100.0); // Invalid: > 90
        args.put("longitude", 7.6586);
        
        // Act & Assert
        StepVerifier.create(tool.invoke(args))
                .assertNext(result -> {
                    assertThat(result.isSuccess()).isFalse();
                    if (result instanceof McpResult.Failure<SnowConditions> failure) {
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
        args.put("latitude", 45.9763);
        args.put("longitude", 200.0); // Invalid: > 180
        
        // Act & Assert
        StepVerifier.create(tool.invoke(args))
                .assertNext(result -> {
                    assertThat(result.isSuccess()).isFalse();
                    if (result instanceof McpResult.Failure<SnowConditions> failure) {
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
        args.put("longitude", 7.6586);
        
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
        args.put("latitude", 45.9763);
        args.put("longitude", 7.6586);
        // No forecastDays specified
        
        SnowConditions mockConditions = createMockSnowConditions();
        when(openMeteoClient.getSnowConditions(
                eq(45.9763),
                eq(7.6586),
                anyString(),
                anyString(),
                eq(7), // Default value
                eq("Europe/Zurich")
        )).thenReturn(Mono.just(mockConditions));
        
        // Act & Assert
        StepVerifier.create(tool.invoke(args))
                .assertNext(result -> assertThat(result.isSuccess()).isTrue())
                .verifyComplete();
    }
    
    @Test
    void testApiError() {
        // Arrange
        Map<String, Object> args = new HashMap<>();
        args.put("latitude", 45.9763);
        args.put("longitude", 7.6586);
        
        when(openMeteoClient.getSnowConditions(
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
                    if (result instanceof McpResult.Failure<SnowConditions> failure) {
                        assertThat(failure.error()).isNotNull();
                        assertThat(failure.error().message()).contains("Failed to fetch snow conditions");
                    }
                })
                .verifyComplete();
    }
    
    @Test
    void testIncludeHourlyFalse() {
        // Arrange
        Map<String, Object> args = new HashMap<>();
        args.put("latitude", 45.9763);
        args.put("longitude", 7.6586);
        args.put("includeHourly", false);
        
        SnowConditions mockConditions = createMockSnowConditions();
        when(openMeteoClient.getSnowConditions(
                eq(45.9763),
                eq(7.6586),
                isNull(), // hourlyParams should be null
                anyString(),
                anyInt(),
                anyString()
        )).thenReturn(Mono.just(mockConditions));
        
        // Act & Assert
        StepVerifier.create(tool.invoke(args))
                .assertNext(result -> assertThat(result.isSuccess()).isTrue())
                .verifyComplete();
    }
    
    @Test
    void testSwissAlpsCoordinates() {
        // Test with various Swiss ski resort coordinates
        testCoordinates(45.9763, 7.6586, "Zermatt");
        testCoordinates(46.0964, 7.2283, "Verbier");
        testCoordinates(46.4908, 9.8355, "St. Moritz");
    }
    
    private void testCoordinates(double lat, double lon, String resort) {
        Map<String, Object> args = new HashMap<>();
        args.put("latitude", lat);
        args.put("longitude", lon);
        
        SnowConditions mockConditions = createMockSnowConditions();
        when(openMeteoClient.getSnowConditions(
                eq(lat),
                eq(lon),
                anyString(),
                anyString(),
                anyInt(),
                anyString()
        )).thenReturn(Mono.just(mockConditions));
        
        StepVerifier.create(tool.invoke(args))
                .assertNext(result -> assertThat(result.isSuccess())
                        .as("Should successfully fetch snow conditions for " + resort)
                        .isTrue())
                .verifyComplete();
    }
    
    private SnowConditions createMockSnowConditions() {
        HourlySnow hourly = new HourlySnow(
                List.of("2025-12-23T00:00", "2025-12-23T01:00"),
                List.of(2.5, 1.0), // snowfall in cm
                List.of(150.0, 151.0), // snow depth in meters
                List.of(-5.0, -6.0) // temperature
        );
        
        DailySnow daily = new DailySnow(
                List.of("2025-12-23", "2025-12-24"),
                List.of(15.0, 20.0), // snowfall sum
                List.of(155.0, 175.0), // max snow depth
                List.of(-2.0, -1.0), // max temp
                List.of(-8.0, -7.0) // min temp
        );
        
        return new SnowConditions(
                45.9763,
                7.6586,
                "Europe/Zurich",
                hourly,
                daily
        );
    }
}
