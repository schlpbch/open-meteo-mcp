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
 * MCP Resource: Swiss Ski Resorts
 * 
 * <p>Provides coordinates and metadata for popular Swiss ski resorts to facilitate
 * snow condition queries and ski trip planning.</p>
 * 
 * <p>This resource helps LLMs quickly access accurate coordinates for major Swiss
 * ski destinations without hallucinating locations.</p>
 */
@Component
public class SwissSkiResortsResource implements McpResource {
    
    private static final Logger logger = LoggerFactory.getLogger(SwissSkiResortsResource.class);
    private static final String RESOURCE_URI = "weather://swiss-ski-resorts";
    private static final String RESOURCE_NAME = "swiss-ski-resorts";
    private static final String RESOURCE_ENDPOINT = "/mcp/swiss-ski-resorts";
    private static final String DATA_FILE = "data/swiss-ski-resorts.json";
    
    private final ObjectMapper objectMapper;
    private String cachedContent;
    
    public SwissSkiResortsResource(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
    }
    
    @Override
    public String getResourceName() {
        return RESOURCE_NAME;
    }
    
    @Override
    public String getResourceDescription() {
        return "Popular Swiss ski resort coordinates and metadata including Zermatt, Verbier, St. Moritz, Davos, " +
               "Grindelwald, and more. Use this to get accurate coordinates for snow condition queries.";
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
                logger.debug("Loaded Swiss ski resorts resource from {}", DATA_FILE);
                return cachedContent;
            } catch (IOException e) {
                logger.error("Failed to load Swiss ski resorts resource", e);
                return "{\"error\": \"Failed to load ski resort data\"}";
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
