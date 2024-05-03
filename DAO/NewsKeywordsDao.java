package com.capstone.finance.DAO;

import com.capstone.finance.Entity.NewsKeywordsEntity;
import org.springframework.data.jpa.repository.JpaRepository;

public interface NewsKeywordsDao extends JpaRepository<NewsKeywordsEntity, String> {

}
