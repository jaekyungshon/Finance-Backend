package com.capstone.finance.Controller;

import com.capstone.finance.Entity.NewsArticlesEntity;
import com.capstone.finance.Service.NewsArticlesService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api")
public class NewsArticlesController {
    @Autowired
    private NewsArticlesService service;

    @GetMapping("/price-detail")
    public List<NewsArticlesEntity> getAllNewsArticles() {
        return service.getAllArticles();
    }
}
