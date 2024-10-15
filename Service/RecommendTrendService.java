package com.capstone.finance.Service;

import com.capstone.finance.Entity.RecommendTrendEntity;
import com.capstone.finance.DAO.RecommendTrendDao;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class RecommendTrendService {
    private final RecommendTrendDao repository;

    @Autowired
    public RecommendTrendService(RecommendTrendDao repository){
        this.repository = repository;
    }
    public List<RecommendTrendEntity> findAll(){
        return repository.findAll();
    }
}
