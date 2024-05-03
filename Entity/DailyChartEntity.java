package com.capstone.finance.Entity;

import com.capstone.finance.DailyChartPK;
import com.capstone.finance.Entity.CompanyInfoEntity;
import jakarta.persistence.*;

import java.time.LocalDate;

@Entity
@Table(name = "daily_chart")
@IdClass(DailyChartPK.class)
public class DailyChartEntity {
    @Id
    private String code;
    @Id
    private LocalDate date;
    private Integer open;
    private Integer close;
    private Integer volume;

    @OneToOne
    @JoinColumn(name = "code", referencedColumnName = "code", insertable = false, updatable = false)
    private CompanyInfoEntity companyInfo;

    // Getters and setters
}