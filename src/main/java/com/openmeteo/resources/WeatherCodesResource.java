package com.openmeteo.resources;

import ch.sbb.mcp.commons.resource.McpResource;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Component;
import reactor.core.publisher.Mono;

import java.io.IOException;

/**
 * MCP Resource: Weather Codes
 * 
 * <p>Provides WMO (World Meteorological Organization) weather code reference data
 * for interpreting weather conditions returned by the Open-Meteo API.</p>
 * 
 * <p>This resource helps LLMs understand weather codes and their implications for
 * travel planning and outdoor activities.</p>
 */
@Component
public class WeatherCodesResource implements McpResource {
    
    private static final Logger logger = LoggerFactory.getLogger(WeatherCodesResource.class);
    private static final String RESOURCE_URI = "weather://codes";
    private static final String RESOURCE_NAME = "weather-codes";
    private static final String RESOURCE_ENDPOINT = "/mcp/weather-codes";
    private static final String DATA_FILE = "data/weather-codes.json";
    
    private final ObjectMapper objectMapper;
    private String cachedContent;
    
    public WeatherCodesResource(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
    }
    
    @Override
    public String getResourceName() {
        return RESOURCE_NAME;
    }
    
    @Override
    public String getResourceDescription() {
        return "WMO weather code reference with descriptions, categories, icons, and travel impact assessments. " +
               "Use this to interpret weather_code values returned by weather tools.";
    }
    
    @Override
    public String getResourceEndpoint() {
        return RESOURCE_ENDPOINT;
    }
    
    @Override
    public String getResourceDataModel() {
        return "application/json";
    }
    
    @Override
    public Mono<Object> readResource() {
        if (cachedContent != null) {
            return Mono.just(cachedContent);
        }
        
        return Mono.fromCallable(() -> {
            try {
                ClassPathResource resource = new ClassPathResource(DATA_FILE);
                // Read and validate JSON
                Object data = objectMapper.readValue(resource.getInputStream(), Object.class);
                cachedContent = objectMapper.writeValueAsString(data);
                logger.debug("Loaded weather codes resource from {}", DATA_FILE);
                return cachedContent;
            } catch (IOException e) {
                logger.error("Failed to load weather codes resource", e);
                return "{\"error\": \"Failed to load weather codes data\"}";
            }
        });
    }
    
    @Override
    public boolean isAvailable() {
        return true;
    }
    
    @Override
    public String getResourceUri() {
        return RESOURCE_URI;
    }
}
