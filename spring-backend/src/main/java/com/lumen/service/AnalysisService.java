package com.lumen.service;

import com.lumen.dto.AnalysisResponse;
import com.lumen.entity.AnalysisJob;
import com.lumen.repository.AnalysisJobRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

@Service
public class AnalysisService {
    
    private final AnalysisJobRepository jobRepository;
    
    @Value("${file.upload-dir:uploads}")
    private String uploadDir;
    
    public AnalysisService(AnalysisJobRepository jobRepository) {
        this.jobRepository = jobRepository;
    }
    
    public AnalysisResponse submitAnalysis(MultipartFile file) throws IOException {
        Path uploadPath = Paths.get(uploadDir);
        if (!Files.exists(uploadPath)) {
            Files.createDirectories(uploadPath);
        }
        
        String jobId = UUID.randomUUID().toString();
        String originalFilename = file.getOriginalFilename();
        String extension = originalFilename.substring(originalFilename.lastIndexOf("."));
        String filename = jobId + extension;
        Path filePath = uploadPath.resolve(filename);
        
        file.transferTo(filePath.toFile());
        
        AnalysisJob job = new AnalysisJob();
        job.setId(jobId);
        job.setFilename(originalFilename);
        job.setFilePath(filePath.toString());
        job.setStatus("PENDING");
        job.setCreatedAt(LocalDateTime.now());
        jobRepository.save(job);
        
        return AnalysisResponse.builder()
                .jobId(jobId)
                .status("PENDING")
                .message("Analysis started")
                .createdAt(job.getCreatedAt())
                .build();
    }
    
    public AnalysisResponse getStatus(String jobId) {
        Optional<AnalysisJob> jobOpt = jobRepository.findById(jobId);
        
        if (jobOpt.isEmpty()) {
            return AnalysisResponse.builder()
                    .jobId(jobId)
                    .status("NOT_FOUND")
                    .message("Job not found")
                    .build();
        }
        
        AnalysisJob job = jobOpt.get();
        
        Map<String, Object> result = null;
        if (job.getResult() != null) {
            result = new HashMap<>();
            result.put("data", job.getResult());
        }
        
        return AnalysisResponse.builder()
                .jobId(job.getId())
                .status(job.getStatus())
                .message(getStatusMessage(job.getStatus()))
                .createdAt(job.getCreatedAt())
                .result(result)
                .errorMessage(job.getErrorMessage())
                .build();
    }
    
    public AnalysisResponse getResults(String jobId) {
        return getStatus(jobId);
    }
    
    private String getStatusMessage(String status) {
        switch (status) {
            case "PENDING": return "Job queued, waiting to start";
            case "PROCESSING": return "Processing audio through all layers";
            case "COMPLETED": return "Analysis complete";
            case "FAILED": return "Analysis failed - see error message";
            default: return "Unknown status";
        }
    }
}
