package com.lumen.controller;

import com.lumen.service.AnalysisService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import java.io.*;
import java.nio.file.*;
import java.util.*;

@RestController
@RequestMapping("/api/analysis")
@CrossOrigin(origins = "http://localhost:3000")
public class AnalysisController {

    @Autowired 
    private AnalysisService service;

    private final String WORKER_DIR = "/Users/apple/Documents/lumen-project/python-workers/";
    private final String UPLOAD_DIR = "/Users/apple/Documents/lumen-project/datasets/test_audio/";

    @PostMapping("/upload")
    public ResponseEntity<Map<String, String>> upload(@RequestParam("file") MultipartFile file) {
        try {
            String jobId = UUID.randomUUID().toString();
            String fileName = jobId + ".wav";
            
            Path uploadPath = Paths.get(UPLOAD_DIR);
            if (!Files.exists(uploadPath)) Files.createDirectories(uploadPath);
            
            Path destPath = uploadPath.resolve(fileName);
            Files.copy(file.getInputStream(), destPath, StandardCopyOption.REPLACE_EXISTING);
            
            new Thread(() -> {
                try {
                    Thread.sleep(500);
                    service.runAnalysis(jobId, destPath.toString());
                } catch (Exception e) {
                    System.err.println("LUMEN ERROR: " + e.getMessage());
                }
            }).start();

            return ResponseEntity.ok(Map.of("jobId", jobId, "status", "PROCESSING"));
        } catch (Exception e) {
            return ResponseEntity.internalServerError().body(Map.of("error", e.getMessage()));
        }
    }

    @GetMapping("/status/{jobId}")
    public ResponseEntity<Map<String, String>> getStatus(@PathVariable String jobId) {
        String status = service.getStatus(jobId);
        return ResponseEntity.ok(Map.of("jobId", jobId, "status", status != null ? status : "NOT_FOUND"));
    }

    @GetMapping("/results/{jobId}")
    public ResponseEntity<String> getResults(@PathVariable String jobId) {
        try {
            String resultFileName = "aligned_" + jobId + ".json";
            Path path = Paths.get(WORKER_DIR).resolve(resultFileName);
            
            System.out.println("Looking for: " + path.toAbsolutePath());

            if (!Files.exists(path)) {
                // Try alternative location
                path = Paths.get(WORKER_DIR + resultFileName);
                if (!Files.exists(path)) {
                    return ResponseEntity.status(404).body("{\"error\": \"Results not ready yet\"}");
                }
            }

            String content = Files.readString(path);
            
            // Parse and re-serialize to ensure valid JSON
            ObjectMapper mapper = new ObjectMapper();
            Object json = mapper.readValue(content, Object.class);
            String prettyJson = mapper.writeValueAsString(json);
            
            return ResponseEntity.ok()
                    .header("Content-Type", "application/json")
                    .body(prettyJson);
                    
        } catch (Exception e) {
            return ResponseEntity.status(500).body("{\"error\": \"" + e.getMessage() + "\"}");
        }
    }
}
