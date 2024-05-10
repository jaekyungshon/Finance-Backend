package com.capstone.finance.Entity;

import com.capstone.finance.NewsArticlesId;
import jakarta.persistence.*;

import java.util.Date;

@Entity
@Table(name = "news_articles")
@IdClass(NewsArticlesId.class)
public class NewsArticlesEntity {
    @Id
    @Column(name = "code")
    private String code;

    @Id
    @Column(name = "date")
    @Temporal(TemporalType.TIMESTAMP)
    private Date date;

    @Id
    @Column(name = "title")
    private String title;

    @Column(name = "content", columnDefinition = "TEXT")
    private String content;

    @Lob
    @Column(name = "image")
    private byte[] image;

    @Column(name = "url", columnDefinition = "TEXT")
    private String url;

    // Getters and Setters
    public String getCode() {
        return code;
    }

    public Date getDate() {
        return date;
    }

    public String getTitle() {
        return title;
    }

    public String getContent() {
        return content;
    }

    public byte[] getImage() {
        return image;
    }

    public String getUrl() {
        return url;
    }
}