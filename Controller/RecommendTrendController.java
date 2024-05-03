package com.capstone.finance.Controller;

import com.capstone.finance.Entity.RecommendTrendEntity;
import com.capstone.finance.Service.RecommendTrendService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/trend")
public class RecommendTrendController {
    private final RecommendTrendService service;

    @Autowired
    public RecommendTrendController(RecommendTrendService service){
        this.service = service;
    }

    @GetMapping
    public List<RecommendTrendEntity> getAllTrend(){
        return service.findAll();
    }
}
