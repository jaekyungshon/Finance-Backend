package com.capstone.finance.Service;

import jakarta.persistence.*;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class CompanyInfoService {
    @PersistenceContext
    private EntityManager entityManager;

    @Cacheable("latestDailyChart")
    public List<Object[]> getLatestDailyChartData() {
        String sql = "SELECT dc.code, dc.date, ci.company, dc.open, dc.close, dc.volume " +
                "FROM daily_chart dc " +
                "JOIN company_info ci ON dc.code = ci.code " +
                "WHERE dc.date IN (SELECT MAX(date) FROM daily_chart GROUP BY code)";

        Query query = entityManager.createNativeQuery(sql);
        return query.getResultList();
    }
}
