package com.openmeteo.config;

import ch.sbb.mcp.commons.core.McpTool;
import com.openmeteo.tools.GetWeatherTool;
import com.openmeteo.tools.GetSnowConditionsTool;
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
}
