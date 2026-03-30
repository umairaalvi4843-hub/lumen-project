package com.lumen.controller;

import com.lumen.dto.AnalysisResponse;
import com.lumen.service.AnalysisService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/analysis")
@CrossOrigin(origins = "*")
public class AnalysisController {
    
    private final AnalysisService analysisService;
    
    public AnalysisController(AnalysisService analysisService) {
        this.analysisService = analysisService;
    }
    
    @PostMapping("/upload")
    public ResponseEntity<AnalysisResponse> uploadFile(
            @RequestParam("file") MultipartFile file) {
        
        if (file.isEmpty()) {
            return ResponseEntity.badRequest()
                    .body(AnalysisResponse.builder()
                            .status("ERROR")
                            .message("File is empty")
                            .build());
        }
        
        try {
            AnalysisResponse response = analysisService.submitAnalysis(file);
            return ResponseEntity.accepted().body(response);
        } catch (IOException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(AnalysisResponse.builder()
                            .status("ERROR")
                            .message("Failed to upload file: " + e.getMessage())
                            .build());
        }
    }
    
    @GetMapping("/status/{jobId}")
    public ResponseEntity<AnalysisResponse> getStatus(@PathVariable String jobId) {
        AnalysisResponse response = analysisService.getStatus(jobId);
        
        if ("NOT_FOUND".equals(response.getStatus())) {
            return ResponseEntity.notFound().build();
        }
        
        return ResponseEntity.ok(response);
    }
    
    @GetMapping("/results/{jobId}")
    public ResponseEntity<AnalysisResponse> getResults(@PathVariable String jobId) {
        AnalysisResponse response = analysisService.getResults(jobId);
        
        if ("NOT_FOUND".equals(response.getStatus())) {
            return ResponseEntity.notFound().build();
        }
        
        return ResponseEntity.ok(response);
    }
    
    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> health() {
        Map<String, String> health = new HashMap<>();
        health.put("status", "UP");
        health.put("service", "Lumen Backend");
        return ResponseEntity.ok(health);
    }
}
