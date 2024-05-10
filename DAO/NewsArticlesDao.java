package com.capstone.finance.DAO;

import com.capstone.finance.Entity.NewsArticlesEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface NewsArticlesDao extends JpaRepository<NewsArticlesEntity, String> {
    // 필요한 경우 추가적인 메소드를 정의할 수 있습니다.
}