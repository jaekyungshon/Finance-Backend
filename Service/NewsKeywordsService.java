package com.capstone.finance.Service;

import com.capstone.finance.Entity.NewsKeywordsEntity;
import com.capstone.finance.DAO.NewsKeywordsDao;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class NewsKeywordsService {
    private final NewsKeywordsDao repository;

    @Autowired
    public NewsKeywordsService(NewsKeywordsDao repository){
        this.repository = repository;
    }

    public List<NewsKeywordsEntity> findAll(){
        return repository.findAll();
    }
}
