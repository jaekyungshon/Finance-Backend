package com.capstone.finance.Service;

import com.capstone.finance.Entity.NewsEmotionEntity;
import com.capstone.finance.DAO.NewsEmotionDao;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class NewsEmotionService {

    private final NewsEmotionDao newsEmotionDao;

    @Autowired
    public NewsEmotionService(NewsEmotionDao newsEmotionDao) {
        this.newsEmotionDao = newsEmotionDao;
    }

    public List<NewsEmotionEntity> getNewsEmotions() {
        return newsEmotionDao.findAllGroupByCode();
    }
}