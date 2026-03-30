package com.lumen.repository;

import com.lumen.entity.AnalysisJob;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;

@Repository
public interface AnalysisJobRepository extends JpaRepository<AnalysisJob, String> {
    List<AnalysisJob> findByStatus(String status);
    Optional<AnalysisJob> findById(String id);
}
