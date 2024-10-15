package com.capstone.finance.Entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

import java.util.Date;

@Entity
@Getter
@Setter
@Table(name = "chatbot_history")
public class ChatbotHistoryEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "username")
    private String username;

    @Column(name = "date")
    private Date date;

    @Column(name = "req_msg")
    private String reqMsg;

    @Column(name = "res_msg")
    private String resMsg;

    // 생성자, getter, setter 등 필요한 메서드 추가
}