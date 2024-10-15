package com.capstone.finance.Service;

import com.capstone.finance.Entity.recommendEntity;
import com.capstone.finance.DAO.recommendDao;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.util.List;
@Service
public class RecommendService {
    @Autowired
    private recommendDao recommendDao;

    public List<recommendEntity> getAllRecommendations(){
        return recommendDao.findAll();
    }

}
