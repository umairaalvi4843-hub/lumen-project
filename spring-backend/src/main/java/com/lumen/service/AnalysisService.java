package com.lumen.service;

import org.springframework.stereotype.Service;
import java.io.*;
import java.util.Map;
import java.util.concurrent.*;

@Service
public class AnalysisService {
    private final String PYTHON_EXE = "/Users/apple/Documents/lumen-project/python-workers/venv/bin/python3";
    private final String WORKING_DIR = "/Users/apple/Documents/lumen-project/python-workers/";
    
    // Concurrent map to handle multiple simultaneous jobs safely
    private final Map<String, String> jobStatus = new ConcurrentHashMap<>();

    public String getStatus(String jobId) {
        return jobStatus.getOrDefault(jobId, "NOT_FOUND");
    }

    public void runAnalysis(String jobId, String absoluteAudioPath) {
        try {
            jobStatus.put(jobId, "PROCESSING");
            
            String[] scripts = {
                "transcriber.py", 
                "diarizer.py", 
                "stress_analyzer.py", 
                "sentiment_analyzer.py", 
                "aligner_production_fixed.py"
            };

            for (String script : scripts) {
                System.out.println("LUMEN: Executing " + script + " for file " + absoluteAudioPath);
                
                ProcessBuilder pb = new ProcessBuilder(PYTHON_EXE, script, absoluteAudioPath);
                pb.directory(new File(WORKING_DIR));
                pb.redirectErrorStream(true);
                
                Process p = pb.start();
                
                // Read logs in real-time to prevent the process buffer from hanging
                try (BufferedReader reader = new BufferedReader(new InputStreamReader(p.getInputStream()))) {
                    String line;
                    while ((line = reader.readLine()) != null) {
                        System.out.println("[" + script + "]: " + line);
                    }
                }

                int exitCode = p.waitFor();
                if (exitCode != 0) {
                    System.err.println("LUMEN ERROR: " + script + " failed with exit code " + exitCode);
                    jobStatus.put(jobId, "FAILED");
                    return;
                }
            }
            
            jobStatus.put(jobId, "COMPLETED");
            System.out.println("LUMEN SUCCESS: Job " + jobId + " finished perfectly.");
            
        } catch (Exception e) {
            System.err.println("LUMEN CRITICAL ERROR: " + e.getMessage());
            jobStatus.put(jobId, "FAILED");
        }
    }
}