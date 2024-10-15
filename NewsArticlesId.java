package com.capstone.finance;

import java.io.Serializable;
import java.util.Date;
import java.util.Objects;

public class NewsArticlesId implements Serializable {
    private String code;
    private Date date;
    private String title;

    public NewsArticlesId() {
    }

    public NewsArticlesId(String code, Date date, String title) {
        this.code = code;
        this.date = date;
        this.title = title;
    }

    // Getters, Setters, hashCode, equals methods
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        NewsArticlesId that = (NewsArticlesId) o;
        return Objects.equals(code, that.code) &&
                Objects.equals(date, that.date) &&
                Objects.equals(title, that.title);
    }

    @Override
    public int hashCode() {
        return Objects.hash(code, date, title);
    }
}
