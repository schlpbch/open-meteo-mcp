package com.openmeteo.session;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.codec.ServerSentEvent;
import org.springframework.stereotype.Component;
import reactor.core.publisher.Sinks;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Manages SSE sessions for MCP Inspector compatibility
 * Handles session lifecycle and message routing
 */
@Component
public class SseSessionManager {

    private static final Logger log = LoggerFactory.getLogger(SseSessionManager.class);

    private final Map<String, Sinks.Many<ServerSentEvent<String>>> sessions = new ConcurrentHashMap<>();

    /**
     * Register a new SSE session
     */
    public void registerSession(String sessionId, Sinks.Many<ServerSentEvent<String>> sink) {
        log.info("Registering SSE session: {}", sessionId);
        sessions.put(sessionId, sink);
    }

    /**
     * Send a message to a specific session
     */
    public void sendMessage(String sessionId, String message) {
        Sinks.Many<ServerSentEvent<String>> sink = sessions.get(sessionId);
        if (sink != null) {
            log.debug("Sending message to session {}: {}", sessionId, message);
            Sinks.EmitResult result = sink.tryEmitNext(ServerSentEvent.<String>builder()
                    .event("message")
                    .data(message)
                    .build());
            if (result.isFailure()) {
                log.warn("Failed to send message to session {}: {}", sessionId, result);
            }
        } else {
            log.warn("Session not found: {}", sessionId);
        }
    }

    /**
     * Remove a session
     */
    public void removeSession(String sessionId) {
        log.info("Removing SSE session: {}", sessionId);
        sessions.remove(sessionId);
    }

    /**
     * Check if a session exists
     */
    public boolean hasSession(String sessionId) {
        return sessions.containsKey(sessionId);
    }

    /**
     * Get active session count
     */
    public int getActiveSessionCount() {
        return sessions.size();
    }
}
