package com.capstone.finance.Controller;

import com.capstone.finance.Entity.AnswerEntity;
import com.capstone.finance.Entity.ChatbotHistoryEntity;
import com.capstone.finance.Service.ChatbotService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

import java.util.List;

@RestController
@RequestMapping("/api")
public class ChatbotController {

    @Autowired
    private ChatbotService chatbotService;

    @PostMapping("chatbot-answer")
    public ResponseEntity<?> sendMessageToFlask(@RequestBody AnswerEntity answer) {
        if (answer.getUsername() == null || answer.getText() == null) {
            return ResponseEntity.badRequest().body("Username and text are required");
        }

        // 플라스크 서버에 요청 보냄
        String flaskUrl = "http://127.0.0.1:5000/chatbot-message";
        RestTemplate restTemplate = new RestTemplate();
        ResponseEntity<String> flaskResponse;

        try {

            flaskResponse = restTemplate.postForEntity(flaskUrl, answer, String.class);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Failed to send request to Flask server");
        }

        // 플라스크 서버 응답 처리
        if (flaskResponse.getStatusCode() == HttpStatus.OK) {
            //
            ResponseEntity<List<ChatbotHistoryEntity>> response = chatbotService.getChatHistoryByUsername(answer.getUsername());
            return response;
        } else {
           //플라스크 서버에 오류 응답을 받았을 때
            return ResponseEntity.status(flaskResponse.getStatusCode()).body("Failed to process request on Flask server");
        }
    }

    @PostMapping("/chatbot-init")
    public ResponseEntity<?> getChatHistory(@RequestBody AnswerEntity answer) {
        ResponseEntity<List<ChatbotHistoryEntity>> response = chatbotService.getChatHistoryByUsername(answer.getUsername());
        return response;
    }
}