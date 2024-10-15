package com.capstone.finance.Controller;

import com.capstone.finance.Entity.NewsEmotionEntity;

import com.capstone.finance.Service.NewsEmotionService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/home/emotion")
public class NewsEmotionController {

    private final NewsEmotionService newsEmotionService;

    @Autowired
    public NewsEmotionController(NewsEmotionService newsEmotionService) {
        this.newsEmotionService = newsEmotionService;
    }

    @GetMapping
    public List<NewsEmotionEntity> getNewsEmotions() {
        return newsEmotionService.getNewsEmotions();
    }
}