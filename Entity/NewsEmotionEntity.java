package com.capstone.finance.Entity;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "recommend_news_articles_emotion")
public class NewsEmotionEntity {
    @Id
    private String code;
    private Long score; // int에서 Long으로 변경

    public NewsEmotionEntity() {
    }

    // JPQL 쿼리 결과와 일치하는 생성자 추가
    public NewsEmotionEntity(String code, Long score) {
        this.code = code;
        this.score = score;
    }

    // Getters and Setters
    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code;
    }

    public Long getScore() {
        return score;
    }

    public void setScore(Long score) {
        this.score = score;
    }
}
