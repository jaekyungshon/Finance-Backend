package com.capstone.finance.Service;

import com.capstone.finance.DAO.NewsArticlesDao;
import com.capstone.finance.Entity.NewsArticlesEntity;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;


import java.util.List;

@Service
public class NewsArticlesService {
    @Autowired
    private NewsArticlesDao repository;

    public List<NewsArticlesEntity> getAllArticles() {
        return repository.findAll();
    }
}

