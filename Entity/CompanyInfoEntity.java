package com.capstone.finance.Entity;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "company_info")
public class CompanyInfoEntity {
    @Id
    private String code;
    private String company;

    // Getters and setters
}
