package com.capstone.finance.Controller;

import com.capstone.finance.Entity.NewsKeywordsEntity;
import com.capstone.finance.Service.NewsKeywordsService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/home/keywords")
public class NewsKeywordsController {
    private final NewsKeywordsService service;

    @Autowired
    public NewsKeywordsController(NewsKeywordsService service){
        this.service = service;
    }

    @GetMapping
    public List<NewsKeywordsEntity> getAllKeywords(){
        return service.findAll();
    }

}
