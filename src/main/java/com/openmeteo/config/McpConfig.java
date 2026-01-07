package com.openmeteo.config;

import ch.sbb.mcp.commons.core.McpTool;
import ch.sbb.mcp.commons.resource.McpResource;
import ch.sbb.mcp.commons.prompts.McpPromptProvider;
import com.openmeteo.tools.GetWeatherTool;
import com.openmeteo.tools.GetSnowConditionsTool;
import com.openmeteo.resources.WeatherCodesResource;
import com.openmeteo.resources.SwissSkiResortsResource;
import com.openmeteo.resources.WeatherParametersResource;
import com.openmeteo.prompts.SkiTripWeatherPrompt;
import com.openmeteo.prompts.OutdoorActivityPrompt;
import com.openmeteo.prompts.WeatherAwareTravelPrompt;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.List;

@Configuration
public class McpConfig {
    
    @Bean
    public List<McpTool<?>> mcpTools(
            GetWeatherTool getWeatherTool,
            GetSnowConditionsTool getSnowConditionsTool) {
        return List.of(getWeatherTool, getSnowConditionsTool);
    }
    
    @Bean
    public List<McpResource> mcpResources(
            WeatherCodesResource weatherCodesResource,
            SwissSkiResortsResource swissSkiResortsResource,
            WeatherParametersResource weatherParametersResource) {
        return List.of(weatherCodesResource, swissSkiResortsResource, weatherParametersResource);
    }
    
    @Bean
    public List<McpPromptProvider> mcpPrompts(
            SkiTripWeatherPrompt skiTripWeatherPrompt,
            OutdoorActivityPrompt outdoorActivityPrompt,
            WeatherAwareTravelPrompt weatherAwareTravelPrompt) {
        return List.of(skiTripWeatherPrompt, outdoorActivityPrompt, weatherAwareTravelPrompt);
    }
    
    @Bean
    public ch.sbb.mcp.commons.registry.McpToolRegistry mcpToolRegistry(
            org.springframework.context.ApplicationContext applicationContext) {
        return new ch.sbb.mcp.commons.registry.McpToolRegistry(applicationContext);
    }
    
    @Bean
    public ch.sbb.mcp.commons.handler.McpResourceHandler mcpResourceHandler(
            List<McpResource> mcpResources,
            com.fasterxml.jackson.databind.ObjectMapper objectMapper) {
        return new ch.sbb.mcp.commons.handler.McpResourceHandler(mcpResources, objectMapper);
    }
    
    @Bean
    public ch.sbb.mcp.commons.prompts.McpPromptRegistry mcpPromptRegistry(
            org.springframework.context.ApplicationContext applicationContext) {
        return new ch.sbb.mcp.commons.prompts.McpPromptRegistry(applicationContext);
    }
    
    @Bean
    public ch.sbb.mcp.commons.prompts.McpPromptHandler mcpPromptHandler(
            ch.sbb.mcp.commons.prompts.McpPromptRegistry promptRegistry) {
        return new ch.sbb.mcp.commons.prompts.McpPromptHandler(promptRegistry);
    }
}
