package com.lumen;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableAsync;

@SpringBootApplication
@EnableAsync
public class LumenApplication {
    
    public static void main(String[] args) {
        SpringApplication.run(LumenApplication.class, args);
        System.out.println("🚀 Lumen Backend Started!");
        System.out.println("   http://localhost:8080");
        System.out.println("   H2 Console: http://localhost:8080/h2-console");
    }
}
