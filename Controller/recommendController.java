package com.capstone.finance.Controller;

import com.capstone.finance.Entity.recommendEntity;
import com.capstone.finance.Service.RecommendService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.List;

@RestController
@RequestMapping("/api/recommend")
public class recommendController {
    @Autowired
    private RecommendService recommendService;

    @GetMapping
    public List<recommendEntity> getAllRecommendation(){
        return recommendService.getAllRecommendations();
    }

}
