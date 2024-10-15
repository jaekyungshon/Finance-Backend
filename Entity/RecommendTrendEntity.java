package com.capstone.finance.Entity;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.Data;

@Data
@Entity
@Table(name = "chatgpt_recommend_trend")
public class RecommendTrendEntity {
    @Id
    private String code;
    private String content;
}
