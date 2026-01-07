package com.openmeteo.controller;

import ch.sbb.mcp.commons.handler.McpResourceHandler;
import ch.sbb.mcp.commons.prompts.McpPromptHandler;
import ch.sbb.mcp.commons.protocol.McpRequest;
import ch.sbb.mcp.commons.protocol.McpResponse;
import ch.sbb.mcp.commons.registry.McpToolRegistry;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Mono;

import java.util.Map;

/**
 * MCP Protocol Controller
 * Handles Model Context Protocol requests for tools, resources, and prompts
 */
@RestController
@RequestMapping("/mcp")
public class McpController {

    private static final Logger log = LoggerFactory.getLogger(McpController.class);

    private final McpToolRegistry toolRegistry;
    private final McpResourceHandler resourceHandler;
    private final McpPromptHandler promptHandler;
    private final ObjectMapper objectMapper;

    public McpController(
            McpToolRegistry toolRegistry,
            McpResourceHandler resourceHandler,
            McpPromptHandler promptHandler,
            ObjectMapper objectMapper) {
        this.toolRegistry = toolRegistry;
        this.resourceHandler = resourceHandler;
        this.promptHandler = promptHandler;
        this.objectMapper = objectMapper;
    }

    /**
     * Main MCP endpoint - handles all MCP protocol requests
     */
    @PostMapping(
            consumes = MediaType.APPLICATION_JSON_VALUE,
            produces = MediaType.APPLICATION_JSON_VALUE
    )
    public Mono<McpResponse> handleMcpRequest(@RequestBody McpRequest request) {
        log.debug("Received MCP request: method={}, id={}", request.method(), request.id());

        return switch (request.method()) {
            // Tools
            case "tools/list" -> handleToolsList(request);
            case "tools/call" -> handleToolsCall(request);
            
            // Resources
            case "resources/list" -> resourceHandler.handleResourcesList(request);
            case "resources/read" -> resourceHandler.handleResourcesRead(request);
            case "resources/templates/list" -> resourceHandler.handleResourcesTemplatesList(request);
            
            // Prompts
            case "prompts/list" -> promptHandler.handlePromptsList(request);
            case "prompts/get" -> promptHandler.handlePromptsGet(request);
            
            default -> Mono.just(createErrorResponse(request, -32601, "Method not found: " + request.method()));
        };
    }

    /**
     * Handle tools/list request
     */
    private Mono<McpResponse> handleToolsList(McpRequest request) {
        try {
            var tools = toolRegistry.listTools();
            var result = Map.of("tools", tools);
            return Mono.just(McpResponse.success(request.id(), result));
        } catch (Exception e) {
            log.error("Error listing tools", e);
            return Mono.just(createErrorResponse(request, -32603, "Internal error: " + e.getMessage()));
        }
    }

    /**
     * Handle tools/call request
     */
    private Mono<McpResponse> handleToolsCall(McpRequest request) {
        try {
            @SuppressWarnings("unchecked")
            Map<String, Object> params = (Map<String, Object>) request.params();
            String toolName = (String) params.get("name");
            @SuppressWarnings("unchecked")
            Map<String, Object> arguments = (Map<String, Object>) params.get("arguments");

            if (toolName == null) {
                return Mono.just(createErrorResponse(request, -32602, "Missing required parameter: name"));
            }

            if (!toolRegistry.hasTool(toolName)) {
                return Mono.just(createErrorResponse(request, -32602, "Tool not found: " + toolName));
            }

            return toolRegistry.invokeTool(toolName, arguments != null ? arguments : Map.of())
                    .map(result -> McpResponse.success(request.id(), Map.of("content", result)))
                    .onErrorResume(e -> {
                        log.error("Error invoking tool: {}", toolName, e);
                        return Mono.just(createErrorResponse(request, -32603, "Tool execution error: " + e.getMessage()));
                    });
        } catch (Exception e) {
            log.error("Error processing tools/call request", e);
            return Mono.just(createErrorResponse(request, -32603, "Internal error: " + e.getMessage()));
        }
    }

    /**
     * Create an error response
     */
    private McpResponse createErrorResponse(McpRequest request, int code, String message) {
        var error = new ch.sbb.mcp.commons.protocol.McpResponse.McpError(code, message, null);
        return McpResponse.error(request.id(), error);
    }

    /**
     * Health check endpoint
     */
    @GetMapping("/health")
    public Map<String, String> health() {
        return Map.of(
                "status", "UP",
                "service", "open-meteo-mcp"
        );
    }
}
