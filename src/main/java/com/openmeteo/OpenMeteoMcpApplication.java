package com.openmeteo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication(exclude = {
        ch.sbb.mcp.commons.session.config.McpSessionAutoConfiguration.class
})
public class OpenMeteoMcpApplication {
    
    public static void main(String[] args) {
        SpringApplication.run(OpenMeteoMcpApplication.class, args);
    }
}
