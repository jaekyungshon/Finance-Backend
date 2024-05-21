package com.capstone.finance.Service;

import com.capstone.finance.DAO.ChatbotHistoryRepository;
import com.capstone.finance.Entity.ChatbotHistoryEntity;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class ChatbotService {

    @Autowired
    private ChatbotHistoryRepository chatbotHistoryRepository;

    public ResponseEntity<List<ChatbotHistoryEntity>> getChatHistoryByUsername(String username) { //username에 해당하는 채팅내역 가져옴
        List<ChatbotHistoryEntity> chatHistory = chatbotHistoryRepository.findByUsername(username);

        if (chatHistory.isEmpty()) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(null);
        } else {
            return ResponseEntity.ok(chatHistory);
        }
    }
}