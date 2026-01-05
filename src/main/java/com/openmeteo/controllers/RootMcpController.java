package com.openmeteo.controllers;

import ch.sbb.mcp.commons.core.McpTool;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Mono;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/mcp/v1")
public class RootMcpController {
    
    private final List<McpTool<?>> tools;
    
    public RootMcpController(List<McpTool<?>> tools) {
        this.tools = tools;
    }
    
    @GetMapping("/tools")
    public Mono<Map<String, Object>> listTools() {
        return Mono.just(Map.of(
            "tools", tools.stream()
                .map(tool -> Map.of(
                    "name", tool.name(),
                    "description", tool.description(),
                    "inputSchema", tool.inputSchema()
                ))
                .toList()
        ));
    }
    
    @PostMapping("/tools/call")
    public Mono<?> callTool(@RequestBody Map<String, Object> request) {
        String toolName = (String) request.get("name");
        @SuppressWarnings("unchecked")
        Map<String, Object> arguments = (Map<String, Object>) request.get("arguments");
        
        return tools.stream()
            .filter(tool -> tool.name().equals(toolName))
            .findFirst()
            .map(tool -> tool.invoke(arguments))
            .orElse(Mono.error(new IllegalArgumentException("Tool not found: " + toolName)));
    }
}
