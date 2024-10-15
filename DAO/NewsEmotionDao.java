package com.capstone.finance.DAO;

import com.capstone.finance.Entity.NewsEmotionEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface NewsEmotionDao extends JpaRepository<NewsEmotionEntity, String> {
    @Query("SELECT new NewsEmotionEntity(n.code, SUM(n.score) as score) FROM NewsEmotionEntity n GROUP BY n.code")
    List<NewsEmotionEntity> findAllGroupByCode();
}