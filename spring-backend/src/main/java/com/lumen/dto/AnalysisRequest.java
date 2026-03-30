package com.lumen.dto;

import lombok.Data;
import org.springframework.web.multipart.MultipartFile;

@Data
public class AnalysisRequest {
    private MultipartFile audioFile;
}
