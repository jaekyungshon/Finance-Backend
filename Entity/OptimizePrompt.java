package com.capstone.finance.Entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
@Entity
@Getter
@Setter
@Table(name = "optimize_prompt")
public class OptimizePrompt {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "prev_req_msg")
    private String prevReqmsg;

    @Column(name = "result_msg")
    private String resultMsg;



}
