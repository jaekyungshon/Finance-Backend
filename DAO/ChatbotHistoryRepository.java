package com.capstone.finance.DAO;

import com.capstone.finance.Entity.ChatbotHistoryEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ChatbotHistoryRepository extends JpaRepository<ChatbotHistoryEntity, Long> {

    List<ChatbotHistoryEntity> findByUsername(String username);
}