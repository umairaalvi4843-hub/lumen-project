package com.lumen.dto;

import java.time.LocalDateTime;
import java.util.Map;

public class AnalysisResponse {
    private String jobId;
    private String status;
    private String message;
    private LocalDateTime createdAt;
    private Map<String, Object> result;
    private String errorMessage;
    
    private AnalysisResponse(Builder builder) {
        this.jobId = builder.jobId;
        this.status = builder.status;
        this.message = builder.message;
        this.createdAt = builder.createdAt;
        this.result = builder.result;
        this.errorMessage = builder.errorMessage;
    }
    
    public static Builder builder() {
        return new Builder();
    }
    
    public static class Builder {
        private String jobId;
        private String status;
        private String message;
        private LocalDateTime createdAt;
        private Map<String, Object> result;
        private String errorMessage;
        
        public Builder jobId(String jobId) { this.jobId = jobId; return this; }
        public Builder status(String status) { this.status = status; return this; }
        public Builder message(String message) { this.message = message; return this; }
        public Builder createdAt(LocalDateTime createdAt) { this.createdAt = createdAt; return this; }
        public Builder result(Map<String, Object> result) { this.result = result; return this; }
        public Builder errorMessage(String errorMessage) { this.errorMessage = errorMessage; return this; }
        
        public AnalysisResponse build() {
            return new AnalysisResponse(this);
        }
    }
    
    // Getters
    public String getJobId() { return jobId; }
    public String getStatus() { return status; }
    public String getMessage() { return message; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public Map<String, Object> getResult() { return result; }
    public String getErrorMessage() { return errorMessage; }
}
