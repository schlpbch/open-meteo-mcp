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
 * MCP Resource: Weather Parameters
 * 
 * <p>Documents all available weather and snow parameters from the Open-Meteo API,
 * including hourly and daily measurements.</p>
 * 
 * <p>This resource helps LLMs understand what data is available and how to request
 * specific weather parameters for different use cases.</p>
 */
@Component
public class WeatherParametersResource implements McpResource {
    
    private static final Logger logger = LoggerFactory.getLogger(WeatherParametersResource.class);
    private static final String RESOURCE_URI = "weather://parameters";
    private static final String RESOURCE_NAME = "weather-parameters";
    private static final String RESOURCE_ENDPOINT = "/mcp/weather-parameters";
    private static final String DATA_FILE = "data/weather-parameters.json";
    
    private final ObjectMapper objectMapper;
    private String cachedContent;
    
    public WeatherParametersResource(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
    }
    
    @Override
    public String getResourceName() {
        return RESOURCE_NAME;
    }
    
    @Override
    public String getResourceDescription() {
        return "Available weather and snow parameters from Open-Meteo API including temperature, precipitation, " +
               "wind, snow depth, and more. Includes both hourly and daily measurements with units and categories.";
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
                logger.debug("Loaded weather parameters resource from {}", DATA_FILE);
                return cachedContent;
            } catch (IOException e) {
                logger.error("Failed to load weather parameters resource", e);
                return "{\"error\": \"Failed to load weather parameters data\"}";
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
